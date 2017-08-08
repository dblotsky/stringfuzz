'''
Functions for creating ASTs.
'''

from stringfuzz.ast import *

__all__ = [
    'smt_var',
    'smt_const',
    'smt_new_var',
    'smt_new_const',
    'smt_str_lit',
    'smt_int_lit',
    'smt_assert',
    'smt_equal',
    'smt_gt',
    'smt_lt',
    'smt_concat',
    'smt_at',
    'smt_len',
    'smt_declare_var',
    'smt_declare_const',
    'smt_sat',
    'smt_model',
    'smt_reset_counters',
]

# constants
VAR_PREFIX   = 'var'
CONST_PREFIX = 'const'

# globals
var_counter   = 0
const_counter = 0

# functions
def smt_var(suffix):
    return IdentifierNode('{}{}'.format(VAR_PREFIX, suffix))

def smt_const(suffix):
    return IdentifierNode('{}{}'.format(CONST_PREFIX, suffix))

def smt_new_var():
    global var_counter
    returned = var_counter
    var_counter += 1
    return smt_var(returned)

def smt_new_const():
    global const_counter
    returned = const_counter
    const_counter += 1
    return smt_const(returned)

def smt_reset_counters():
    global const_counter
    global var_counter
    const_counter = 0
    var_counter = 0

def smt_str_lit(value):
    return StringLitNode(value)

def smt_int_lit(value):
    return IntLitNode(value)

def smt_assert(exp):
    return ExpressionNode('assert', [exp])

def smt_equal(a, b):
    return ExpressionNode('=', [a, b])

def smt_gt(a, b):
    return ExpressionNode('>', [a, b])

def smt_lt(a, b):
    return ExpressionNode('<', [a, b])

def smt_concat(a, b):
    return ConcatNode(a, b)

def smt_at(s, i):
    return AtNode(s, i)

def smt_len(a):
    return LengthNode(a)

def smt_declare_var(identifier):
    return ExpressionNode('declare-fun', [identifier, ArgsNode(), SortNode('String')])

def smt_declare_const(identifier):
    return ExpressionNode('declare-const', [identifier, SortNode('String')])

def smt_sat():
    return ExpressionNode('check-sat', [])

def smt_model():
    return ExpressionNode('get-model', [])
