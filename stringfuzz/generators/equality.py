import random

from stringfuzz.scanner import ALPHABET
from stringfuzz.smt import *

__all__ = [
    'equality',
]

def random_string(size):
    return ''.join(random.choice(ALPHABET) for i in range(size))

def get_length(max_length, randomise):
    if randomise is False:
        return max_length
    return random.randint(0, max_length)

def concat_terms(terms):

    # initialise result to the last term (i.e. first in reversed list)
    reversed_terms = reversed(terms)
    result         = next(reversed_terms)

    # keep concatenating preceding terms to the result
    for term in reversed_terms:
        result = smt_concat(term, result)

    return result

def randomly_add_infix(probability):
    return random.random() < probability

def make_equality(num_expressions, num_terms, prefix_length, suffix_length, add_infixes, infix_length, randomise_lengths, infix_probability):

    # check args
    if num_expressions < 1:
        raise ValueError('the number of expressions must be at least 1')

    if num_terms < 2:
        raise ValueError('the number of terms per expression must be at least 2')

    if infix_probability < 0.0 or 1.0 < infix_probability:
        raise ValueError('the probability of infixes must be between 0.0 and 1.0')

    # result values
    expressions = []
    variables   = []
    heads       = []

    # create expressions
    for i in range(num_expressions):

        # create head, prefix, and suffix
        head   = smt_new_var()
        prefix = smt_str_lit(random_string(get_length(prefix_length, randomise_lengths)))
        suffix = smt_str_lit(random_string(get_length(suffix_length, randomise_lengths)))

        # keep track of new variables
        new_variables = [head]
        heads.append(head)

        # create middle
        middle = []
        for i in range(num_terms - 2):

            # if infixes are enabled
            if add_infixes is True and randomly_add_infix(infix_probability) is True:
                new_term = smt_str_lit(random_string(get_length(infix_length, randomise_lengths)))

            # otherwise, just add variables
            else:
                new_term = smt_new_var()
                new_variables.append(new_term)

            middle.append(new_term)

        # compose full expression
        terms    = [prefix] + middle + [suffix]
        concat   = concat_terms(terms)
        equality = smt_assert(smt_equal(head, concat))

        # remember variables and expressions
        variables += new_variables
        expressions.append(equality)

    # finally, create equality between all expressions
    first_head = heads[0]
    for other_head in heads[1:]:
        head_equality = smt_assert(smt_equal(first_head, other_head))
        expressions.append(head_equality)

    # add check sat
    expressions.append(smt_sat())

    # create variable declarations
    # NOTE:
    #      heads are already present in the list of variables
    declarations = []
    for v in variables:
        declarations.append(smt_declare_var(v))

    return declarations + expressions

# public API
def equality(*args, **kwargs):
    smt_reset_counters()
    return make_equality(*args, **kwargs)
