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

from stringfuzz.transformers import fuzz, graft
from stringfuzz.generators import random_ast
from stringfuzz.generator import generate
from stringfuzz.ast import AssertNode, CheckSatNode
from stringfuzz.util import coin_toss

__all__ = [
    'simulate'
]

# constants
DEFAULT_MUTATION_ROUNDS = 4
DEFAULT_TIMEOUT         = 5
MAX_NUM_ASSERTS         = 20

SAT_ANSWER     = 'sat'
UNSAT_ANSWER   = 'unsat'
TIMEOUT_ANSWER = 'timeout'
UNKNOWN_ANSWER = 'unknown'
ERROR_ANSWER   = 'error'

# globals
_language   = None
_timeout    = DEFAULT_TIMEOUT
_tracing_on = False

# data structures
RunResult = namedtuple('RunResult', ['run_time', 'answer', 'stdout', 'stderr', 'exception'])

# helpers
def trace(*args, **kwargs):
    global _tracing_on
    if _tracing_on is True:
        print(*args, file=sys.stderr, **kwargs)

def decompose(ast):
    head    = []
    asserts = []
    tail    = []
    for e in ast:
        if isinstance(e, AssertNode):
            asserts.append(e)
        elif isinstance(e, CheckSatNode):
            tail.append(e)
        else:
            head.append(e)
    return head, asserts, tail

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
        os.killpg(os.getpgid(process.pid), signal.SIGINT)

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

        answer = stdout

    return RunResult(run_time=elapsed, answer=answer, stdout=stdout, stderr=stderr, exception=None)

def thread_main(index, results, **kwargs):

    # get run result
    try:
        result = run_solver(**kwargs)
    except Exception as e:
        result = RunResult(run_time=0, answer=ERROR_ANSWER, stdout='', stderr='', exception=e)

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

def mutate_fuzz(ast):
    return ast
    # return fuzz(ast, skip_re_range=False)

def mutate_add(ast):

    if len(ast) >= MAX_NUM_ASSERTS:
        return ast

    # decompose existing AST
    head, asserts, tail = decompose(ast)

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

    # isolate just the new assert
    _, new_asserts, _ = decompose(new_ast)

    # return with the new asserts added
    return head + asserts + new_asserts + tail

def mutate_pop(ast):
    head, asserts, tail = decompose(ast)
    return head + asserts[:-1] + tail

def mutate_graft(ast):
    return ast
    # return graft(ast, skip_str_to_re=False)

def mutate(ast):
    choice = random.randint(1, 4)

    if choice == 1:
        return mutate_fuzz(ast)

    if choice == 2:
        return mutate_pop(ast)

    if choice == 3:
        return mutate_add(ast)

    if choice == 4:
        return mutate_graft(ast)

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
# genetic world
# ---------------------------------------------------

def judge_one(organism, solver_command):

    # take run samples
    num_samples = get_num_free_cores()
    samples     = sample_runs(organism, num_samples, solver_command)

    # get run times and outputs
    run_times  = (sample.run_time for sample in samples)
    answers    = (sample.stdout for sample in samples)

    # check for errors
    for sample in samples:
        if sample.stderr != '' and sample.answer != TIMEOUT_ANSWER:
            raise RuntimeError('Solver returned errors:\n{}'.format(error))
        if sample.exception is not None:
            raise sample.exception

    # get median run time
    median_run_time = statistics.median(run_times)

    # process answers
    first_answer   = next(answers)
    satisfiability = first_answer

    # figure out score
    score = median_run_time

    return score

def judge_all(population, solver_command):
    return [judge_one(organism, solver_command) for organism in population]

def cull(population, scores):

    # annotate specimens with their scores
    global _timeout
    indices   = range(len(population))
    annotated = zip([(_timeout - s) for s in scores], indices)

    # create a min-heap out of annotated specimens
    heap = []
    for entry in annotated:
        heappush(heap, entry)

    # get best specimens
    best_entries = [heappop(heap) for i in range(3)]
    best_indices = [entry[1] for entry in best_entries]
    best         = [population[i] for i in best_indices]

    return best

def show_world(g, population, scores):
    annotated_population = zip(population, scores)
    sorted_population    = sorted(annotated_population, key=lambda x: x[1])

    trace('at generation {}:'.format(g))
    trace('population:')
    for i, (organism, score) in enumerate(sorted_population):
        row = '  {index}: {score} score, {length} statements'.format(
            index  = i,
            length = len(organism),
            score  = score
        )
        trace(row)
    trace('')

# public API
def simulate(progenitor, language, solver_command, num_generations, world_size, trace_resolution, enable_tracing):

    # set global config
    global _language
    global _tracing_on
    _language   = language
    _tracing_on = enable_tracing

    # create initial population
    population = [progenitor]

    # run simulation
    for g in range(num_generations):

        # log generation progress
        trace('generation {} running ...'.format(g))

        # sanity check: there should be organisms
        assert len(population) > 0

        # populate world
        population = reproduce(population, world_size)

        # measure performance of each organism
        scores = judge_all(population, solver_command)

        # print world
        if time_to_trace(g, trace_resolution):
            show_world(g, population, scores)

        # keep only the "best" organisms
        population = cull(population, scores)

    # return final population
    return population
