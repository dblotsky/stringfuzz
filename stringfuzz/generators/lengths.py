import random
import string

from collections import namedtuple

from stringfuzz.generators.util import call_generate
from stringfuzz.smt import *

__all__ = [
    'lengths'
]

# data structures
Variable = namedtuple('Variable', ['length'])

# functions
def new_model(min_length, max_length):
    length = random.randint(min_length, max_length)
    return Variable(length)

def set_equal(a, b):
    return smt_assert(smt_equal(a, b))

def make_lengths(num_vars, min_length, max_length, num_concats):

    # create variables
    variables = [smt_new_var() for i in range(num_vars)]

    # create model
    model = {v : new_model(min_length, max_length) for v in variables}

    # create length constraints
    expressions = []
    for v in variables:
        expressions.append(set_equal(smt_int_lit(model[v].length), smt_len(v)))

    # validate args
    if num_concats > (num_vars / 2):
        raise ValueError('can\'t add more concats than the number of variables divided by 2')

    # if concats are required, add them
    if num_concats > 0:

        # copy and shuffle variable list to use in concats
        unused_variables = list(variables)
        random.shuffle(unused_variables)

        # generate the concats
        for i in range(num_concats):

            # pick operands
            a          = unused_variables.pop()
            b          = unused_variables.pop()
            concat     = smt_concat(a, b)
            sum_length = model[a].length + model[b].length

            # add constraint
            expressions.append(set_equal(smt_int_lit(sum_length), smt_len(concat)))

    # add sat-check
    expressions.append(smt_sat())

    # create declarations
    declarations = [smt_declare_var(v) for v in variables]

    return declarations + expressions

# public API
def lengths(language, produce_models, *args, **kwargs):
    return call_generate(make_lengths(*args, **kwargs), language, produce_models)
