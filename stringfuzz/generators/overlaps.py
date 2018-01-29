import random

from stringfuzz.scanner import ALPHABET
from stringfuzz.smt import *
from stringfuzz.util import join_terms_with, random_string

__all__ = [
    'overlaps',
]

def make_overlaps(num_vars, length_of_consts):

    # check args
    if num_vars < 1:
        raise ValueError('the number of variables must be at least 1')

    # create constants
    left  = smt_str_lit(random_string(length_of_consts))
    right = smt_str_lit(random_string(length_of_consts))

    # create middle variables
    middle_vars = [smt_new_var() for i in range(num_vars)]
    middle      = join_terms_with(middle_vars, smt_concat)

    # create overlapping constraint
    left_concat     = smt_concat(left, middle)
    right_concat    = smt_concat(middle, right)
    concat_equality = smt_assert(smt_equal(left_concat, right_concat))

    # add constraint and sat-check
    expressions = [
        concat_equality,
        smt_check_sat()
    ]

    # create variable declarations
    declarations = []
    for v in middle_vars:
        declarations.append(smt_declare_var(v))

    return declarations + expressions

# public API
def overlaps(*args, **kwargs):
    smt_reset_counters()
    return make_overlaps(*args, **kwargs)
