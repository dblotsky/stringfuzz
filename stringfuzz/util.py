from stringfuzz.ast import ConcatNode, ReConcatNode

__all__ = [
    'join_terms_with',
]

# public API
def join_terms_with(terms, concatenator):
    assert len(terms) > 0

    # initialise result to the last term (i.e. first in reversed list)
    reversed_terms = reversed(terms)
    result         = next(reversed_terms)

    # keep appending preceding terms to the result
    for term in reversed_terms:
        result = concatenator(term, result)

    return result
