import random

from stringfuzz.scanner import ALPHABET
from stringfuzz.ast import ConcatNode, ReConcatNode
from stringfuzz.ast import AssertNode, CheckSatNode, FunctionDeclarationNode

__all__ = [
    'coin_toss',
    'random_string',
    'join_terms_with',
    'split_ast',
    'all_same',
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

def split_ast(ast):
    head           = []
    declarations   = []
    asserts        = []
    tail           = []
    for e in ast:
        if isinstance(e, AssertNode):
            asserts.append(e)
        elif isinstance(e, CheckSatNode):
            tail.append(e)
        elif isinstance(e, FunctionDeclarationNode):
            declarations.append(e)
        else:
            head.append(e)
    return head, declarations, asserts, tail

# CREDIT:
#        https://stackoverflow.com/questions/3844801/check-if-all-elements-in-a-list-are-identical
def all_same(lst):
    return not lst or lst.count(lst[0]) == len(lst)
