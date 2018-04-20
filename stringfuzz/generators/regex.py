import random
import re

from stringfuzz.scanner import ALPHABET
from stringfuzz.smt import *
from stringfuzz.util import join_terms_with, random_string, coin_toss

__all__ = [
    'regex',
    'INCREASING_LITERALS',
    'RANDOM_LITERALS',
    'MEMBER_IN',
    'MEMBER_NOT_IN',
    'MEMBER_ALTERNATING',
    'MEMBER_RANDOM',
    'OPERATOR_STAR',
    'OPERATOR_PLUS',
    'OPERATOR_UNION',
    'OPERATOR_INTER',
    'OPERATOR_CONCAT',
    'OPERATOR_ALTERNATING',
    'OPERATOR_RANDOM',
]

# constants
INCREASING_LITERALS = 'increasing'
RANDOM_LITERALS     = 'random'

LITERAL_TYPES = [
    INCREASING_LITERALS,
    RANDOM_LITERALS,
]

MEMBER_IN          = 'in'
MEMBER_NOT_IN      = 'not-in'
MEMBER_ALTERNATING = 'alternating'
MEMBER_RANDOM      = 'random'

MEMBERSHIP_TYPES = [
    MEMBER_IN,
    MEMBER_NOT_IN,
    MEMBER_ALTERNATING,
    MEMBER_RANDOM,
]

OPERATOR_STAR   = 's'
OPERATOR_PLUS   = 'p'
OPERATOR_UNION  = 'u'
OPERATOR_INTER  = 'i'
OPERATOR_CONCAT = 'c'

OPERATOR_LIST = [
    OPERATOR_STAR,
    OPERATOR_PLUS,
    OPERATOR_UNION,
    OPERATOR_INTER,
    OPERATOR_CONCAT,
]

OPERATOR_ALTERNATING = 'alternating'
OPERATOR_RANDOM      = 'random'

OPERATOR_TYPES = [
    OPERATOR_ALTERNATING,
    OPERATOR_RANDOM,
]

# global config
# NOTE:
#      using globals because it's annoying to pass around a bunch of variables
_cursor       = 0
_literal_type = None
_literal_min  = 1
_literal_max  = 1

# helpers
def fill_string(character, length):
    return character * length

def get_char_and_advance():
    global _cursor
    character = ALPHABET[_cursor]
    _cursor   = (_cursor + 1) % len(ALPHABET)
    return character

def make_regex_string(min_length, max_length):
    global _literal_type

    chosen_length = random.randint(min_length, max_length)

    # use a fixed-length string of one character, each time using
    # the next character from the alphabet
    if _literal_type == INCREASING_LITERALS:
        filler = get_char_and_advance()
        string = fill_string(filler, chosen_length)

    # generate a random string
    elif _literal_type == RANDOM_LITERALS:
        string = random_string(chosen_length)

    return smt_str_to_re(smt_str_lit(string))

def make_random_term(depth, operator_index):
    if depth == 0:
        return make_regex_string(_literal_min, _literal_max)

    if _operator_type == OPERATOR_ALTERNATING:
        next_operator_index = operator_index + 1
    else:
        next_operator_index = random.randrange(len(_operator_list))

    operator = get_operator_at_index(operator_index)
    subterm = make_random_term(depth - 1, next_operator_index)

    if operator == OPERATOR_STAR:
        return smt_regex_star(subterm)

    if operator == OPERATOR_PLUS:
        return smt_regex_plus(subterm)

    if operator == OPERATOR_UNION:
        second_subterm = make_random_term(depth - 1, next_operator_index)
        return smt_regex_union(subterm, second_subterm)

    if operator == OPERATOR_INTER:
        second_subterm = make_random_term(depth - 1, next_operator_index)
        return smt_regex_inter(subterm, second_subterm)

    if operator == OPERATOR_CONCAT:
        second_subterm = make_random_term(depth - 1, next_operator_index)
        return smt_regex_concat(subterm, second_subterm)

def make_random_terms(num_terms, depth):
    if _operator_type == OPERATOR_ALTERNATING:
        terms = [make_random_term(depth, 0) for i in range(num_terms)]
    else:
        terms = [make_random_term(depth, random.randrange(len(_operator_list))) for i in range(num_terms)]

    regex = join_terms_with(terms, smt_regex_concat)
    return regex

def toggle_membership_type(t):
    if t == MEMBER_IN:
        return MEMBER_NOT_IN
    return MEMBER_IN

def get_operator_at_index(index):
    global _operator_list

    return _operator_list[index % len(_operator_list)]

def make_constraint(variable, r):
    global _configured_membership
    global _current_membership

    # if random, set the membership type randomly
    if _configured_membership == MEMBER_RANDOM:
        if coin_toss():
            _current_membership = MEMBER_IN
        else:
            _current_membership = MEMBER_NOT_IN

    # if toggle, toggle membership type
    elif _configured_membership == MEMBER_ALTERNATING:
        _current_membership = toggle_membership_type(_current_membership)

    # create constraint
    constraint = smt_regex_in(variable, r)

    # negate it if required
    if _current_membership == MEMBER_NOT_IN:
        constraint = smt_not(constraint)

    return constraint

def make_regex(
    num_regexes,
    num_terms,
    literal_min,
    literal_max,
    term_depth,
    literal_type,
    membership_type,
    reset_alphabet,
    max_var_length,
    min_var_length,
    operators,
    operator_type,
):

    # check args
    if num_regexes < 1:
        raise ValueError('number of regexes must be greater than 0')

    if num_terms < 1:
        raise ValueError('number of terms must be greater than 0')

    if literal_min < 1:
        raise ValueError('min literal length must be greater than 0')

    if literal_max < 1:
        raise ValueError('max literal length must be greater than 0')

    if literal_max < literal_min:
        raise ValueError('max literal length must not be less than min literal length')

    if term_depth < 0:
        raise ValueError('depths of terms must not be less than 0')

    if literal_type not in LITERAL_TYPES:
        raise ValueError('unknown literal type: {!r}'.format(literal_type))

    if membership_type not in MEMBERSHIP_TYPES:
        raise ValueError('unknown membership type: {!r}'.format(membership_type))

    if min_var_length is not None and min_var_length < 0:
        raise ValueError('min variable length must not be less than 0')

    if max_var_length is not None and max_var_length < 0:
        raise ValueError('max variable length must not be less than 0')

    if len(operators) < 1 or any(map(lambda x: x not in OPERATOR_LIST, operators)):
        raise ValueError('invalid operators: {!r}'.format(operators))

    if operator_type not in OPERATOR_TYPES:
        raise ValueError('unknown operator type: {!r}'.format(operator_type))

    # set globals
    global _cursor
    global _literal_type
    global _configured_membership
    global _current_membership
    global _literal_min
    global _literal_max
    global _operator_list
    global _operator_type

    _cursor                = 0
    _literal_type          = literal_type
    _configured_membership = membership_type
    _current_membership    = _configured_membership
    _literal_min           = literal_min
    _literal_max           = literal_max
    _operator_list         = []
    _operator_type         = operator_type

    # parse operator list in order, in case user wants a custom alternation order
    for c in operators:
        if c not in _operator_list:
            _operator_list.append(c)

    # create variable
    matched = smt_new_var()

    # create regexes
    regexes = []
    for i in range(num_regexes):

        # reset alphabet for every regex if required
        if reset_alphabet is True:
            _cursor = 0

        new_regex = make_random_terms(num_terms, term_depth)
        regexes.append(new_regex)

    # create regex constraints
    expressions = []
    for r in regexes:
        constraint = make_constraint(matched, r)
        expressions.append(smt_assert(constraint))

    # create length constraints if required
    if min_var_length is not None:
        min_bound = smt_int_lit(min_var_length)
        equality  = smt_lte(min_bound, smt_len(matched))
        expressions.append(smt_assert(equality))

    if max_var_length is not None:
        max_bound = smt_int_lit(max_var_length)
        equality  = smt_lte(smt_len(matched), max_bound)
        expressions.append(smt_assert(equality))

    # add sat check
    expressions.append(smt_check_sat())

    # create declarations
    declarations = [
        smt_declare_var(matched)
    ]

    return declarations + expressions

# public API
def regex(*args, **kwargs):
    smt_reset_counters()
    return make_regex(*args, **kwargs)
