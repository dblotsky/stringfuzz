import random

from stringfuzz.smt import *

__all__ = [
    'random_ast'
]

# functions
def make_random_ast():
    return []

# public API
def random_ast(*args, **kwargs):
    smt_reset_counters()
    return make_random_ast(*args, **kwargs)
