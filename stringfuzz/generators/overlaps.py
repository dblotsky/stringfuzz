import random

from stringfuzz.scanner import ALPHABET
from stringfuzz.smt import *

__all__ = [
    'overlaps',
]

def random_string(size):
    return ''.join(random.choice(ALPHABET) for i in range(size))

def make_verlaps(num_equalities, length_of_consts, length_of_vars):

    # create equalities of overlapping variables
    variables   = []
    expressions = []
    model       = {}
    for i in range(num_equalities):

        # create new constants and variables
        left               = smt_str_lit(random_string(length_of_consts))
        right              = smt_str_lit(random_string(length_of_consts))
        middle_a, middle_b = smt_new_var(), smt_new_var()

        # create two concats
        first_concat  = smt_concat(left, middle_a)
        second_concat = smt_concat(middle_b, right)

        # create constraints
        concat_constraint = smt_assert(smt_equal(
            first_concat,
            second_concat)
        )
        length_constraint_a = smt_assert(smt_equal(
            smt_len(middle_a),
            smt_int_lit(length_of_vars))
        )
        length_constraint_b = smt_assert(smt_equal(
            smt_len(middle_b),
            smt_int_lit(length_of_vars))
        )

        # add constraints
        expressions.append(concat_constraint)
        expressions.append(length_constraint_a)
        expressions.append(length_constraint_b)

        # remember variables
        variables.append(middle_a)
        variables.append(middle_b)

    # add sat-check
    expressions.append(smt_sat())

    # create variable declarations
    declarations = []
    for v in variables:
        declarations.append(smt_declare_var(v))

    return declarations + expressions

# public API
def overlaps(*args, **kwargs):
    smt_reset_counters()
    return make_verlaps(*args, **kwargs)
