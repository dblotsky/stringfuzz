import random
import os
import sys
import subprocess
import multiprocessing
import threading
import datetime
import signal
import statistics

from heapq import heappush, heappop
from collections import namedtuple

from stringfuzz.transformers import *
from stringfuzz.generators import random_ast
from stringfuzz.mergers import simple, DISJOINT_RENAME
from stringfuzz.generator import generate
from stringfuzz.ast import AssertNode, CheckSatNode, FunctionDeclarationNode
from stringfuzz.util import coin_toss, split_ast

__all__ = [
    'SAT_ANSWER',
    'UNSAT_ANSWER',
    'TIMEOUT_ANSWER',
    'UNKNOWN_ANSWER',
    'ERROR_ANSWER',
    'simulate'
]

# constants
DEFAULT_MUTATION_ROUNDS = 4
DEFAULT_TIMEOUT         = 5
NUM_TO_KEEP             = 4

UNWANTED_PUNISH_FACTOR = 2

SAT_ANSWER     = 'SAT'
UNSAT_ANSWER   = 'UNSAT'
TIMEOUT_ANSWER = 'timeout'
UNKNOWN_ANSWER = 'unknown'
ERROR_ANSWER   = 'error'

SOLVER_ERROR_FORMAT = '''Solver invocation error:
    Command: {command}
    Run time: {time}
    Answer: {answer}
v - STDOUT - v
{stdout}
v - STDERR - v
{stderr}
v - INSTANCE - v
{instance}
'''

# globals
_language        = None
_timeout         = DEFAULT_TIMEOUT
_tracing_on      = False
_wanted_answer   = None
_min_num_asserts = 1
_max_num_asserts = 1
_stop_simulation = False

# data structures
RunResult = namedtuple('RunResult', ['run_time', 'answer', 'stdout', 'stderr', 'exception'])
Karma     = namedtuple('Karma', ['run_time', 'score', 'answer', 'lines', 'asserts', 'bytes'])

# helpers
def trace(*args, **kwargs):
    global _tracing_on
    if _tracing_on is True:
        print(*args, file=sys.stderr, **kwargs)

def generate_problem(problem):
    global _language
    return generate(problem, _language)

def get_num_free_cores():
    num_cores = multiprocessing.cpu_count()

    # subtracting one because at least the current core is used
    num_free_cores = num_cores - 1

    return num_free_cores

def time_to_trace(generation, resolution):
    return (generation % resolution) == 0

def get_only_asserts(organism):
    return [e for e in organism if isinstance(e, AssertNode)]

def interpret_answer(stdout, stderr):

    # if there is error output, assume error
    if len(stderr) > 0:
        return ERROR_ANSWER

    # if both outputs are empty, assume unknown answer
    if len(stderr) == 0 and len(stdout) == 0:
        return UNKNOWN_ANSWER

    # parse stdout
    stdout = stdout.lower().strip()
    if stdout == 'unsat':
        return UNSAT_ANSWER
    if stdout == 'sat':
        return SAT_ANSWER
    if stdout == 'unknown':
        return UNKNOWN_ANSWER
    if stdout == 'timeout':
        return TIMEOUT_ANSWER

    # if parsing failed, assume error
    return ERROR_ANSWER

# ---------------------------------------------------
# sampling
# ---------------------------------------------------

def run_solver(command, problem, timeout):

    # # print command that will be run
    # trace('RUNNING:', repr(command))

    # get start time
    start = datetime.datetime.now().timestamp()

    # run command
    process = subprocess.Popen(
        command,
        shell              = True,
        stdin              = subprocess.PIPE,
        stdout             = subprocess.PIPE,
        stderr             = subprocess.PIPE,
        preexec_fn         = os.setsid,
        universal_newlines = True
    )

    # feed it the problem and wait for it to complete
    try:
        stdout, stderr = process.communicate(input=problem, timeout=timeout)

    # if it times out ...
    except subprocess.TimeoutExpired as e:

        # trace('TIMED OUT:', repr(command), '... killing', process.pid)

        # kill it
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGINT)
        except (PermissionError, ProcessLookupError) as e:
            print('COULDN\'T KILL SOLVER!', e, file=sys.stderr)

        # set timeout result
        elapsed = timeout
        answer  = TIMEOUT_ANSWER

        # gather outputs
        stdout = process.stdout.read()
        stderr = process.stderr.read()

    # if it completes in time ...
    else:

        # measure run time
        end     = datetime.datetime.now().timestamp()
        elapsed = end - start

        answer = interpret_answer(stdout, stderr)

    return RunResult(run_time=elapsed, answer=answer, stdout=stdout, stderr=stderr, exception=None)

def thread_main(index, results, **kwargs):

    # get run result
    try:
        result = run_solver(**kwargs)
    except Exception as e:
        result = RunResult(run_time=0, answer=None, stdout='', stderr='', exception=e)

    # record it
    results[index] = result

def sample_runs(organism, num_samples, solver_command):

    global _timeout

    # run one thread per sample
    samples = [None for i in range(num_samples)]
    threads = []
    for i in range(num_samples):
        thread = threading.Thread(
            target = thread_main,
            args   = (i, samples),
            kwargs = {
                'command': solver_command,
                'timeout': _timeout,
                'problem': generate_problem(organism)
            }
        )
        threads.append(thread)

    # run experiments in parallel
    for thread in threads:
        thread.start()

    # wait for experiments to finish
    for thread in threads:
        thread.join()

    return samples

# ---------------------------------------------------
# reproduction
# ---------------------------------------------------

def mutate_reverse(ast):
    return reverse(ast)

def mutate_translate(ast):
    return translate(ast, translate_integers=False, skip_re_range=True)

def mutate_add(ast):

    # create random AST with one assert
    new_ast = random_ast(
        num_vars            = 1,
        num_asserts         = 1,
        depth               = 5,
        max_terms           = 5,
        max_str_lit_length  = 10,
        max_int_lit         = 30,
        literal_probability = 0.5,
        semantically_valid  = True
    )

    # merge both ASTs, with shared variables
    return simple([ast, new_ast], rename_type=DISJOINT_RENAME)

def mutate_remove(ast):
    head, declarations, asserts, tail = split_ast(ast)
    return head + declarations + asserts[:-1] + tail

def choose_mutator(ast):

    # always-available mutators
    mutators = [mutate_reverse, mutate_translate]

    # adding more asserts
    num_asserts = len(get_only_asserts(ast))
    if num_asserts < _max_num_asserts:
        mutators.append(mutate_add)

    # removing asserts
    if num_asserts > _min_num_asserts:
        mutators.append(mutate_remove)

    # pick a mutator
    mutator = random.choice(mutators)

    return mutator

def mutate(ast):
    mutator = choose_mutator(ast)
    mutated = mutator(ast)
    return mutated

def vegetative_mate(parent, num_mutation_rounds=DEFAULT_MUTATION_ROUNDS):
    child = parent

    for i in range(num_mutation_rounds):
        child = mutate(child)

    return child

def mate(parents):
    return vegetative_mate(random.choice(parents))

def reproduce(survivors, world_size):

    # create offspring
    num_offspring = world_size - len(survivors)
    offspring     = [mate(survivors) for i in range(num_offspring)]

    # return new population
    new_population = survivors + offspring
    return new_population

# ---------------------------------------------------
# simulation
# ---------------------------------------------------

def judge_one(organism, solver_command):

    # take run samples
    num_samples = get_num_free_cores()
    samples     = sample_runs(organism, num_samples, solver_command)

    # process the samples
    any_sat_answers     = False
    any_unsat_answers   = False
    any_timeout_answers = False
    any_unknown_answers = False
    for sample in samples:

        # check for errors
        if sample.exception is not None:
            raise sample.exception

        if (
            (sample.stderr != '' and sample.answer != TIMEOUT_ANSWER) or
            (sample.answer == ERROR_ANSWER)
        ):
            error_message = SOLVER_ERROR_FORMAT.format(
                command  = solver_command,
                answer   = sample.answer,
                time     = sample.run_time,
                stdout   = sample.stdout,
                stderr   = sample.stderr,
                instance = generate_problem(organism)
            )
            raise RuntimeError(error_message)

        # keep track of answers
        if sample.answer == SAT_ANSWER:
            any_sat_answers = True
        if sample.answer == UNSAT_ANSWER:
            any_unsat_answers = True
        if sample.answer == UNKNOWN_ANSWER:
            any_unknown_answers = True
        if sample.answer == TIMEOUT_ANSWER:
            any_timeout_answers = True

    # get median run time
    run_times       = [sample.run_time for sample in samples]
    median_run_time = statistics.median(run_times)

    # sanity check: should never be both sat and unsat answers
    if any_sat_answers and any_unsat_answers:
        raise RuntimeError('Solver returned different answers for the same instance: {}\n'.format(generate_problem(organism)))

    # figure out "logical" answer
    if any_sat_answers:
        logical_answer = SAT_ANSWER
    elif any_unsat_answers:
        logical_answer = UNSAT_ANSWER
    elif any_unknown_answers:
        logical_answer = UNKNOWN_ANSWER
    elif any_timeout_answers:
        logical_answer = TIMEOUT_ANSWER
    else:
        logical_answer = None

    # start the score as the time
    score = median_run_time

    # reduce score for an unwanted SAT/UNSAT
    if (
        (_wanted_answer is not None) and
        (logical_answer == SAT_ANSWER or logical_answer == UNSAT_ANSWER)
    ):
        if logical_answer != _wanted_answer:
            score /= UNWANTED_PUNISH_FACTOR

    # compute and return karma
    karma = Karma(
        score    = score,
        run_time = median_run_time,
        answer   = logical_answer,
        lines    = len(organism),
        asserts  = len(get_only_asserts(organism)),
        bytes    = len(generate_problem(organism))
    )
    return karma

def judge_all(population, solver_command):
    return [judge_one(organism, solver_command) for organism in population]

def sort_population(population, karma):

    # annotate the population with the karma
    annotated_population = zip(population, karma)

    # sort by size: lowest bytes first
    by_bytes = sorted(annotated_population, key=lambda x: x[1].bytes)

    # sort by score: highest score and lowest bytes first
    by_score_and_bytes = sorted(by_bytes, reverse=True, key=lambda x: x[1].score)

    return by_score_and_bytes

def cull(population, karma):

    # get best specimens
    sorted_population = sort_population(population, karma)
    best = sorted_population[:NUM_TO_KEEP]

    # return survivors
    return [survivor for survivor, _ in best]

def show_world(g, population, karma):
    sorted_population = sort_population(population, karma)

    trace('at generation {}:'.format(g))
    trace('population (from best to worst):')
    for i, (organism, its_karma) in enumerate(sorted_population):
        row = '  {i}: {k.answer} {s:.4f} score [{k.run_time:.4f}s, {k.asserts} asserts, {k.lines} lines, {k.bytes} bytes]'.format(
            i = i,
            k = its_karma,
            s = its_karma.score
        )
        trace(row)
    trace('')

    # if more than half timed out, signal that
    num_timeouts  = len([k for k in karma if k.answer == TIMEOUT_ANSWER])
    timeout_ratio = float(num_timeouts) / float(len(karma))
    if timeout_ratio > 0.5:
        return True
    return False

def handle_sigint(signal, frame):
    print('Received SIGINT', file=sys.stderr)
    global _stop_simulation
    _stop_simulation = True

# public API
def simulate(
    progenitor,
    language,

    # solver args
    solver_command,
    solver_timeout,

    # simulation args
    num_generations,
    world_size,
    wanted_answer,
    max_num_asserts,
    min_num_asserts,

    # output args
    trace_resolution,
    enable_tracing
):

    # set global config
    global _language
    global _timeout
    global _tracing_on
    global _wanted_answer
    global _max_num_asserts
    global _min_num_asserts
    _language        = language
    _timeout         = solver_timeout
    _tracing_on      = enable_tracing
    _wanted_answer   = wanted_answer
    _max_num_asserts = max_num_asserts
    _min_num_asserts = min_num_asserts

    # set up signal handler
    signal.signal(signal.SIGINT, handle_sigint)

    # create initial population
    population   = [progenitor]
    strike_count = 0
    many_timeouts = False

    # run simulation
    for g in range(num_generations):

        # log generation progress
        print('generation {} running ...'.format(g), file=sys.stderr)

        # sanity check: there should be organisms
        assert len(population) > 0

        # populate world
        population = reproduce(population, world_size)

        # measure performance of each organism
        karma = judge_all(population, solver_command)

        # print world
        if time_to_trace(g, trace_resolution):
            many_timeouts = show_world(g, population, karma)

        # keep only the "best" organisms
        population = cull(population, karma)

        # check for timeout-only runs
        if many_timeouts:
            strike_count += 1
            print('strike', strike_count, file=sys.stderr)
            if strike_count > 5:
                print('most dudes keep timing out; stopping simulation', file=sys.stderr)
                global _stop_simulation
                _stop_simulation = True
        else:
            strike_count = max(0, strike_count-1)

        # break out if needed
        if _stop_simulation:
            break

    # return final population
    return population
