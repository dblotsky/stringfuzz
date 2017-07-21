import random

from stringfuzz.scanner import ALPHABET, WHITESPACE

__all__ = [
    'random_text',
]

# constants
ALL_CHARS = ALPHABET + WHITESPACE

# functions
def make_random_text(length):
    return ''.join(random.choice(ALL_CHARS) for i in range(length))

# public API
def random_text(*args, **kwargs):
    return make_random_text(*args, **kwargs)
