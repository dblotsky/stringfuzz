import re
import random
import string

from stringfuzz.generator import generate
from stringfuzz.smt import *

__all__ = [
    'concats',
    'random_text',
    'random_ast'
]

# constants
RANDOM_CHARS = string.printable

SYNTACTIC_DEPTH = 'syntactic'
SEMANTIC_DEPTH  = 'semantic'

# concats fuzzer
def set_concat(r, a, b):
    return smt_assert(smt_equal(r, smt_concat(a, b)))

def set_equal(a, b):
    return smt_assert(smt_equal(a, b))

def make_semantic_concats(depth, balanced):

    if balanced is True:
        raise ValueError('balanced trees with semantic concats are unsupported')

    # compute number of variables
    num_vars = (depth * 2) + 1

    # make variable names
    variables = [smt_var(i) for i in range(num_vars)]

    # make concats
    expressions = []
    for i in range(0, len(variables) - 2, 2):
        expression = set_concat(variables[i], variables[i + 1], variables[i + 2])
        expressions.append(expression)

    return variables, [], expressions

def make_syntactic_concats(depth, balanced):

    def concats_helper(depth, balanced):

        # base case
        if depth < 1:
            new_var = smt_new_var()
            return [new_var], new_var

        # make right side
        right_vars, right_expr = concats_helper(depth - 1, balanced)

        # make left side
        if balanced is True:
            left_vars, left_expr = concats_helper(depth - 1, balanced)
        else:
            left_vars, left_expr = concats_helper(0, balanced)

        # build return value
        all_vars = left_vars + right_vars
        concat   = smt_concat(left_expr, right_expr)

        return all_vars, concat

    # make first variable
    first_var = smt_new_var()

    # create return values
    variables   = [first_var]
    constants   = []
    expressions = []

    # make deep concat
    if depth > 0:
        concat_variables, concat_expr = concats_helper(depth, balanced)

        variables  += concat_variables
        expressions = [set_equal(first_var, concat_expr)]

    return variables, constants, expressions

def make_concats(depth, depth_type, solution, balanced):

    # generate problem components
    if depth_type == SEMANTIC_DEPTH:
        variables, constants, expressions = make_semantic_concats(depth, balanced)

    else:
        variables, constants, expressions = make_syntactic_concats(depth, balanced)

    # get first variable
    first_var = variables[0]

    # create definitions
    definitions = []
    definitions.extend([smt_declare_var(v) for v in variables])
    definitions.extend([smt_declare_const(v) for v in constants])

    # set first variable to expected solution
    expressions.append(set_equal(first_var, smt_str_lit(solution)))

    # add sat-check
    expressions.append(smt_sat())
    expressions.append(smt_model())

    return definitions + expressions

# random text fuzzer
def make_random_text(length):
    return ''.join(random.choice(RANDOM_CHARS) for i in range(length))

# random ast fuzzer
def make_random_ast():
    return []

# public API
def concats(language, *args, **kwargs):
    return generate(make_concats(*args, **kwargs), language)

def random_text(language, *args, **kwargs):
    return make_random_text(*args, **kwargs)

def random_ast(language, *args, **kwargs):
    return generate(make_random_ast(*args, **kwargs), language)
