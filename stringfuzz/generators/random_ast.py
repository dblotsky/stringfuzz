import random

from stringfuzz.generators.util import call_generate

__all__ = [
    'random_ast'
]

# functions
def make_random_ast():
    return []

# public API
def random_ast(language, produce_models, *args, **kwargs):
    return call_generate(make_random_ast(*args, **kwargs), language, produce_models)
