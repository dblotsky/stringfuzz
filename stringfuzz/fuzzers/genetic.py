import random
import os
import sys
import subprocess
import threading
import datetime
import signal
import statistics

from heapq import heappush, heappop

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
NUM_RUNS                = 8

# globals
_language = None
_timeout  = DEFAULT_TIMEOUT

# helpers
def mutate_fuzz(ast):
    return ast
    # return fuzz(ast, skip_re_range=False)

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

def time_solver(command, problem, timeout, verbose=False, debug=False):

    # print command that will be run
    if verbose is True or debug is True:
        print('RUNNING:', repr(command), file=sys.stderr)

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

        # if verbose is True:
        print('TIMED OUT:', repr(command), '... killing', process.pid, file=sys.stderr)

        # kill it
        os.killpg(os.getpgid(process.pid), signal.SIGINT)

        # set timeout result
        elapsed = timeout

        # print output
        # if verbose is True:
        print('STDOUT:', process.stdout.read(), file=sys.stderr, end='')
        print('STDERR:', process.stderr.read(), file=sys.stderr, end='')

    # if it completes in time ...
    else:

        # measure run time
        end     = datetime.datetime.now().timestamp()
        elapsed = end - start

        if stderr != '':
            print('STDERR IS NOT EMPTY!:', stderr, file=sys.stderr, end='')
            print('PROBLEM: \n', problem, file=sys.stderr, end='')

        # print output
        if debug is True:
            print('STDOUT:', stdout, file=sys.stderr, end='')
            print('STDERR:', stderr, file=sys.stderr, end='')

    return elapsed

def reproduce(survivors, world_size):

    # create offspring
    num_offspring = world_size - len(survivors)
    offspring     = [mate(survivors) for i in range(num_offspring)]

    # return new population
    new_population = survivors + offspring
    return new_population

def generate_problem(problem):
    global _language
    return generate(problem, _language)

def normalise(bottom, top, value):
    width = top - bottom
    return value / width

def time_in_thread(index, times, **kwargs):
    time         = time_solver(**kwargs)
    times[index] = time

def get_score(organism, saint_peter):
    global _timeout

    # get average run time
    times   = [0 for i in range(NUM_RUNS)]
    threads = []
    for i in range(NUM_RUNS):
        thread = threading.Thread(
            target = time_in_thread,
            args   = (i, times),
            kwargs = {
                'command': saint_peter,
                'timeout': _timeout,
                'problem': generate_problem(organism)
            }
        )
        threads.append(thread)

    # run experiments in parallel
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    # return median run time
    score = statistics.median(times)
    return score

def judge(population, saint_peter):
    for organism in population:
        yield get_score(organism, saint_peter)

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
    print('population', ' '.join(['p[{i}]={s}'.format(s=len(e), i=i) for i, e in enumerate(population)]))
    best_entries = [heappop(heap) for i in range(3)]
    print('best entries', best_entries)
    best_indices = [entry[1] for entry in best_entries]
    print('best indices', best_indices)
    best         = [population[i] for i in best_indices]
    print('best:', ' '.join(['p[{i}]={s} for {t}'.format(t=e[0], s=len(population[e[1]]), i=e[1]) for e in best_entries]))
    print('')

    return best

def time_to_log(generation, resolution):
    return (generation % resolution) == 0

# public API
def simulate(progenitor, language, saint_peter, num_generations, world_size, log_resolution):

    # set global config
    global _language
    _language = language

    # create initial population
    population = [progenitor]

    # run simulation
    for g in range(num_generations):

        # log generation progress
        if time_to_log(g, log_resolution):
            print('generation {}'.format(g))

        # sanity check: there should be organisms
        assert len(population) > 0

        # populate world
        population = reproduce(population, world_size)

        # measure performance of each organism
        scores = judge(population, saint_peter)

        # keep only the "best" organisms
        population = cull(population, scores)

    # return final population
    return population
