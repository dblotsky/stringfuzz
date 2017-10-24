import random

from stringfuzz.scanner import ALPHABET
from stringfuzz.smt import *

__all__ = [
    'regex_pair',
]

# constants
REGEX_LENGTH = 10

# helpers
def random_string(size):
    return ''.join(random.choice(ALPHABET) for i in range(size))

def make_random_regex_constant(length):
    return smt_str_to_re(smt_str_lit(random_string(length)))

def make_random_regex(length):
    return make_random_regex_constant(length)

def make_regex_pair():

    # create variable
    matched = smt_new_var()

    # create regexes
    regex1 = make_random_regex(REGEX_LENGTH)
    regex2 = make_random_regex(REGEX_LENGTH)

    # create constraints
    matches_1      = smt_assert(smt_regex_in(matched, regex1))
    doesnt_match_2 = smt_assert(smt_not(smt_regex_in(matched, regex2)))

    # build formula
    declarations = [
        smt_declare_var(matched)
    ]

    expressions = [
        matches_1,
        doesnt_match_2,
        smt_sat()
    ]

    return declarations + expressions

# public API
def regex_pair(*args, **kwargs):
    smt_reset_counters()
    return make_regex_pair(*args, **kwargs)
