import random

from collections import namedtuple

from stringfuzz.smt import *

__all__ = [
    'lengths',
]

# data structures
Variable = namedtuple('Variable', ['length'])

# functions
def new_model(min_length, max_length):
    length = random.randint(min_length, max_length)
    return Variable(length)

def set_equal(a, b):
    return smt_assert(smt_equal(a, b))

def make_lengths(num_vars, min_length, max_length, num_concats, random_relations):

    # make list of possible relations to use in constraints
    if random_relations is True:
        def choose_relation():
            return random.choice([smt_equal, smt_gt, smt_lt])
    else:
        def choose_relation():
            return smt_equal

    # create variables
    variables = [smt_new_var() for i in range(num_vars)]

    # create model
    model = {v : new_model(min_length, max_length) for v in variables}

    # create length constraints
    expressions = []
    for v in variables:

        # pick a relation
        chosen_relation = choose_relation()

        # build constraint
        model_length  = smt_int_lit(model[v].length)
        actual_length = smt_len(v)
        constraint    = smt_assert(chosen_relation(model_length, actual_length))

        # add constraint
        expressions.append(constraint)

    # validate args
    max_num_concats = num_vars // 2
    if num_concats > max_num_concats:
        raise ValueError('can\'t add more concats than the number of variables divided by 2 (that is, {})'.format(max_num_concats))

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

            # pick a relation
            chosen_relation = choose_relation()

            # build constraint
            sum_length_lit = smt_int_lit(sum_length)
            actual_length  = smt_len(concat)
            constraint     = smt_assert(chosen_relation(sum_length_lit, actual_length))

            # add constraint
            expressions.append(constraint)

    # add sat-check
    expressions.append(smt_sat())

    # create declarations
    declarations = [smt_declare_var(v) for v in variables]

    return declarations + expressions

# public API
def lengths(*args, **kwargs):
    smt_reset_counters()
    return make_lengths(*args, **kwargs)
