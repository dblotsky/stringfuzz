import random

from stringfuzz.generator import generate
from stringfuzz.scanner import ALPHABET
from stringfuzz.smt import *

__all__ = [
    'concats',
    'SYNTACTIC_DEPTH',
    'SEMANTIC_DEPTH',
]

# constants
SYNTACTIC_DEPTH = 'syntactic'
SEMANTIC_DEPTH  = 'semantic'

# functions
def set_equal(a, b):
    return smt_assert(smt_equal(a, b))

def set_concat(result, a, b):
    return set_equal(result, smt_concat(a, b))

def extract(character, string, index):
    return set_equal(character, smt_at(string, index))

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

def make_concats(depth, depth_type, solution, balanced, num_extracts, max_extract_index):

    # generate concats
    if depth_type == SEMANTIC_DEPTH:
        variables, constants, expressions = make_semantic_concats(depth, balanced)

    else:
        variables, constants, expressions = make_syntactic_concats(depth, balanced)

    # get first variable
    first_var = variables[0]

    # validate args
    max_num_extracts      = max_extract_index + 1
    num_chars_in_vars     = max_num_extracts * len(variables)
    num_chars_in_consts   = sum(map(len, constants))
    num_possible_extracts = num_chars_in_vars + num_chars_in_consts
    if num_extracts > num_possible_extracts:
        raise ValueError('number of requested extracts exceeds number of possible unique extracts')

    # set first variable to expected solution if one was given
    if solution is not None:
        expressions.append(set_equal(first_var, smt_str_lit(solution)))

    # add extracts if required
    if num_extracts > 0:

        # create model to avoid contradictions
        extract_model  = {var : list(range(max_num_extracts)) for var in variables}
        remaining_vars = list(variables)

        # shuffle indices in model
        for indices in extract_model.values():
            random.shuffle(indices)

        # create the extracts
        for i in range(num_extracts):

            # randomly pick a variable and a char to extract from it
            var_index = random.randrange(len(remaining_vars))
            var       = remaining_vars[var_index]
            char      = smt_str_lit(random.choice(ALPHABET))

            # pop the first index from which to extract, without replacement
            index = smt_int_lit(extract_model[var].pop())

            # remove the variable if it can no longer be extracted from
            num_remaining_indices = len(extract_model[var])
            if num_remaining_indices < 1:
                remaining_vars.pop(var_index)

            # add extract
            expressions.append(extract(char, var, index))

    # create definitions
    definitions = []
    definitions.extend([smt_declare_var(v) for v in variables])
    definitions.extend([smt_declare_const(v) for v in constants])

    # add sat-check
    expressions.append(smt_sat())

    return definitions + expressions

# public API
def concats(language, *args, **kwargs):
    return generate(make_concats(*args, **kwargs), language)
