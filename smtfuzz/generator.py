import re

from smtfuzz.scanner import scan
from smtfuzz.ast import *

__all__ = [
    'generate',
    'generate_file',
]

def generate_expression():
    pass

# public API
def generate_file(ast, path, language):
    with open(path, 'r') as file:
        file.write(generate(ast, language))

def generate(ast, language):
    return '\n'.join(map(str, ast))
