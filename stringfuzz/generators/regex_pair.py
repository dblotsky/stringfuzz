import random

from stringfuzz.scanner import ALPHABET
from stringfuzz.smt import *

__all__ = [
    'regex_pair',
    'INCREASING_REGEX',
    'RANDOM_REGEX',
]

# constants
INCREASING_REGEX = 'increasing'
RANDOM_REGEX     = 'random'

LITERAL_TYPES = [
    INCREASING_REGEX,
    RANDOM_REGEX,
]

# global config
# NOTE:
#      using globals because it's annoying to pass around a bunch of variables
_cursor       = 0
_literal_type   = None
_term_length = 1

# helpers
def random_string(length):
    return ''.join(random.choice(ALPHABET) for i in range(length))

def fill_string(character, length):
    return character * length

def get_char_and_advance():
    global _cursor
    character = ALPHABET[_cursor]
    _cursor   = (_cursor + 1) % len(ALPHABET)
    return character

def make_regex_string():
    global _literal_type
    global _term_length

    # use a fixed-length string of one character, each time using
    # the next character from the alphabet
    if _literal_type == INCREASING_REGEX:
        filler = get_char_and_advance()
        string = fill_string(filler, _term_length)

    # generate a random string
    elif _literal_type == RANDOM_REGEX:
        string = random_string(_term_length)

    return smt_str_to_re(smt_str_lit(string))

def make_regex_star():
    return smt_regex_star(make_regex_string())

def make_random_regex_term():
    generator = get_random_generator()
    term      = generator()
    return term

def concat_regex_terms(terms):
    assert len(terms) > 0

    # concat all terms
    result = terms[0]
    for term in terms[1:]:
        result = smt_regex_concat(term, result)

    return result

def get_random_generator():
    term_generators = [
        make_regex_string,
        make_regex_star
    ]

    return random.choice(term_generators)

def make_random_regex(num_terms):
    terms = [make_random_regex_term() for i in range(num_terms)]
    regex = concat_regex_terms(terms)
    return regex

def make_regex_pair(num_terms, term_length, literal_type):

    # check args
    if num_terms < 1:
        raise ValueError('number of terms must be greater than 1')

    if term_length < 1:
        raise ValueError('lengths of terms must be greater than 1')

    if literal_type not in LITERAL_TYPES:
        raise ValueError('unknown literal type: {!r}'.format(literal_type))

    # set globals
    global _cursor
    global _literal_type
    global _term_length

    _cursor       = 0
    _literal_type = literal_type
    _term_length  = term_length

    # create variable
    matched = smt_new_var()

    # create regexes
    regex1 = make_random_regex(num_terms)
    regex2 = make_random_regex(num_terms)

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
