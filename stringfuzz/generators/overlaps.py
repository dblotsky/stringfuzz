import random

from stringfuzz.scanner import ALPHABET
from stringfuzz.smt import *

__all__ = [
    'overlaps',
]

def random_string(size):
    return ''.join(random.choice(ALPHABET) for i in range(size))

def chain_concats(length):

    # create left side
    left_expr = smt_new_var()
    left_vars = [left_expr]

    # base case
    if length < 2:
        return left_vars, left_expr

    # create right side
    right_vars, right_expr = chain_concats(length - 1)

    # build return value
    all_vars = left_vars + right_vars
    concat = smt_concat(left_expr, right_expr)

    return all_vars, concat

def make_verlaps(num_vars, length_of_consts):

    # check args
    if num_vars < 1:
        raise ValueError('the number of variables must be at least 1')

    # create constants
    left  = smt_str_lit(random_string(length_of_consts))
    right = smt_str_lit(random_string(length_of_consts))

    # create middle variables
    variables, middle = chain_concats(num_vars)

    # create overlapping constraint
    left_concat     = smt_concat(left, middle)
    right_concat    = smt_concat(middle, right)
    concat_equality = smt_assert(smt_equal(left_concat, right_concat))

    # add constraint and sat-check
    expressions = [
        concat_equality,
        smt_sat()
    ]

    # create variable declarations
    declarations = []
    for v in variables:
        declarations.append(smt_declare_var(v))

    return declarations + expressions

# public API
def overlaps(*args, **kwargs):
    smt_reset_counters()
    return make_verlaps(*args, **kwargs)
