import re
import random
import string

from stringfuzz.ast import IdentifierNode, ExpressionNode, StringLitNode, ConcatNode
from stringfuzz.generator import generate

__all__ = [
    'concats',
    'randomness',
    'nonsense'
]

# constants
RANDOM_CHARS = string.printable
VAR_PREFIX   = 'var'
CONST_PREFIX = 'const'

SYNTACTIC_DEPTH = 'syntactic'
SEMANTIC_DEPTH  = 'semantic'

# concats fuzzer
def _var(suffix):
    return IdentifierNode('{}{}'.format(VAR_PREFIX, suffix))

def _str_lit(value):
    return StringLitNode(value)

def _assert(exp):
    return ExpressionNode('assert', [exp])

def _equal(a, b):
    return ExpressionNode('=', [a, b])

def _concat(a, b):
    return ConcatNode(a, b)

def _declare_var(identifier):
    return ExpressionNode('declare-fun', [identifier, ExpressionNode('', []), 'String'])

def _declare_const(identifier):
    return ExpressionNode('declare-const', [identifier, ExpressionNode('', []), 'String'])

def _check_sat():
    return ExpressionNode('check-sat', [])

def set_concat(r, a, b):
    return _assert(_equal(r, _concat(a, b)))

def set_equal(a, b):
    return _assert(_equal(a, b))

def make_semantic_concats(depth):

    # compute number of variables
    num_vars = (depth + 1) * 2

    # make variable names
    variables = [_var(i) for i in range(num_vars)]

    # make concats
    expressions = []
    for i in range(0, len(variables) - 2, 2):
        expression = set_concat(variables[i], variables[i + 1], variables[i + 2])
        expressions.append(expression)

    return variables, [], expressions

def make_syntactic_concats(depth):

    def concats_helper(variables, depth):
        if depth < 1:
            return variables[0]
        return _concat(variables[0], concats_helper(variables[1:], depth - 1))

    # make variable names
    variables = [_var(i) for i in range(depth + 2)]

    # make deep concat
    if depth > 0:
        expressions = [_assert(_equal(variables[0], concats_helper(variables[1:], depth)))]
    else:
        expressions = []

    return variables, [], expressions

def make_concats(depth, depth_type, solution):

    # generate problem components
    if depth_type == SEMANTIC_DEPTH:
        variables, constants, expressions = make_semantic_concats(depth)

    else:
        variables, constants, expressions = make_syntactic_concats(depth)

    # create definitions
    definitions = []
    definitions.extend([_declare_var(v) for v in variables])
    definitions.extend([_declare_const(v) for v in constants])

    # set first variable to expected solution
    expressions.append(set_equal(variables[0], _str_lit(solution)))

    # add sat-check
    expressions.append(_check_sat())

    return definitions + expressions

# random fuzzer
def make_randomness(length):
    return ''.join(random.choice(RANDOM_CHARS) for i in range(length))

# nonsense
def make_nonsense():
    return []

# public API
def concats(language, *args, **kwargs):
    return generate(make_concats(*args, **kwargs), language)

def randomness(language, *args, **kwargs):
    return make_randomness(*args, **kwargs)

def nonsense(language, *args, **kwargs):
    return generate(make_nonsense(*args, **kwargs), language)
