import random

from stringfuzz.generator import generate

__all__ = [
    'random_ast'
]

# functions
def make_random_ast():
    return []

# public API
def random_ast(language, *args, **kwargs):
    return generate(make_random_ast(*args, **kwargs), language)
