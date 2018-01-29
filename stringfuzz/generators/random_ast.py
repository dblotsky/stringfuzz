import random
import inspect

from stringfuzz.smt import *
from stringfuzz.util import random_string, coin_toss

__all__ = [
    'random_ast'
]

# constants
NONTERMINALS = [
    smt_and,
    smt_or,
    smt_not,
    smt_equal,
    smt_gt,
    smt_lt,
    smt_gte,
    smt_lte,
    smt_concat,
    smt_at,
    smt_len,
    smt_str_to_re,
    smt_regex_in,
    smt_regex_concat,
    smt_regex_plus,
    smt_regex_range,
    smt_regex_star,
    smt_regex_union,
    smt_assert,
]

ALMOST_TERMINALS = [
    smt_str_to_re,
    smt_regex_range,
]

N_ARY_NONTERMINALS = [
    smt_concat,
    smt_regex_concat,
    smt_and,
    smt_or,
    smt_equal,
    smt_regex_union,
]

# NOTE:
#      these guys are here (and not with the other helpers) because
#      the list below needs them to be defined before it
def random_str_lit():
    return smt_str_lit(random_string(_max_str_lit_length))

def random_int_lit():
    return smt_int_lit(random.randint(0, _max_int_lit))

def random_bool_lit():
    return smt_bool_lit(coin_toss())

LITERALS = [
    random_str_lit,
    random_int_lit,
    random_bool_lit,
]

# global config
_max_terms          = 0
_max_str_lit_length = 0
_max_int_lit        = 0

# helpers
def make_random_literal():
    literal_generator = random.choice(LITERALS)
    return literal_generator()

def make_random_terminal(variables):

    # randomly choose between a variable or a literal
    if coin_toss():
        return random.choice(variables)

    return make_random_literal()

def make_random_expression(variables, depth):

    # at depth 0, make a terminal
    if depth < 1:
        return make_random_terminal(variables)

    # randomly shrink the depth
    shrunken_depth = random.randint(0, depth - 1)

    # get random expression generator
    expression_generator = random.choice(NONTERMINALS)

    # get the number of arguments it takes
    generator_signature = inspect.signature(expression_generator)
    generator_args      = generator_signature.parameters
    num_args            = len(generator_args)

    # generate random arguments
    random_args = [make_random_expression(variables, shrunken_depth) for i in range(num_args)]

    # build expression
    expression = expression_generator(*random_args)

    return expression

def generate_assert(variables, depth):
    expression = make_random_expression(variables, depth)
    return smt_assert(expression)

def make_random_ast(num_vars, num_asserts, depth, max_terms, max_str_lit_length, max_int_lit, semantically_valid):
    global _max_terms
    global _max_str_lit_length
    global _max_int_lit

    # set global config
    _max_terms          = max_terms
    _max_str_lit_length = max_str_lit_length
    _max_int_lit        = max_int_lit

    # create variables
    variables    = [smt_new_var() for i in range(num_vars)]
    declarations = [smt_declare_var(v) for v in variables]

    # create asserts
    asserts = [generate_assert(variables, depth) for i in range(num_asserts)]

    # add check-sat
    asserts.append(smt_check_sat())

    return declarations + asserts

# public API
def random_ast(*args, **kwargs):
    smt_reset_counters()
    return make_random_ast(*args, **kwargs)
