import random

from stringfuzz.scanner import ALPHABET
from stringfuzz.ast import ConcatNode, ReConcatNode

__all__ = [
    'coin_toss',
    'random_string',
    'join_terms_with',
]

# public API
def coin_toss():
    return random.choice([True, False])

def random_string(length):
    return ''.join(random.choice(ALPHABET) for i in range(length))

def join_terms_with(terms, concatenator):
    assert len(terms) > 0

    # initialise result to the last term (i.e. first in reversed list)
    reversed_terms = reversed(terms)
    result         = next(reversed_terms)

    # keep appending preceding terms to the result
    for term in reversed_terms:
        result = concatenator(term, result)

    return result
