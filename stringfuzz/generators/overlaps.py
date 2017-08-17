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

def make_verlaps(num_vars, length_of_vars):

    # check args
    num_middle_vars = num_vars - 2
    if num_middle_vars < 1:
        raise ValueError('the number of variables must be at least 3')

    # create new variables
    left                       = smt_new_var()
    middle_vars, middle_concat = chain_concats(num_middle_vars)
    right                      = smt_new_var()
    variables                  = [left] + middle_vars + [right]

    # create overlapping constraint
    left_concat     = smt_concat(left, middle_concat)
    right_concat    = smt_concat(middle_concat, right)
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

    # create length constraints
    length_constraints = []
    for v in variables:
        length_constraint = smt_assert(smt_equal(
            smt_len(v),
            smt_int_lit(length_of_vars))
        )
        length_constraints.append(length_constraint)

    return declarations + length_constraints + expressions

# public API
def overlaps(*args, **kwargs):
    smt_reset_counters()
    return make_verlaps(*args, **kwargs)
