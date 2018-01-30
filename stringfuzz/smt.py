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
    'smt_bool_lit',
    'smt_assert',
    'smt_equal',
    'smt_gt',
    'smt_lt',
    'smt_gte',
    'smt_lte',
    'smt_concat',
    'smt_at',
    'smt_len',
    'smt_declare_var',
    'smt_declare_const',
    'smt_check_sat',
    'smt_get_model',
    'smt_reset_counters',
    'smt_str_to_re',
    'smt_regex_in',
    'smt_regex_concat',
    'smt_regex_star',
    'smt_regex_plus',
    'smt_regex_range',
    'smt_regex_union',
    'smt_and',
    'smt_or',
    'smt_not',
    'smt_string_logic',
    'smt_is_sat',
    'smt_is_unsat',
]

# constants
VAR_PREFIX   = 'var'
CONST_PREFIX = 'const'

# globals
var_counter   = 0
const_counter = 0

# helper functions
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

# leaf expressions
def smt_str_lit(value):
    return StringLitNode(value)

def smt_int_lit(value):
    return IntLitNode(value)

def smt_bool_lit(value):
    return BoolLitNode(value)

# node expressions
def smt_and(a, b):
    return AndNode(a, b)

def smt_or(a, b):
    return OrNode(a, b)

def smt_not(a):
    return NotNode(a)

def smt_equal(a, b):
    return RelationExpressionNode(IdentifierNode('='), a, b)

def smt_gt(a, b):
    return RelationExpressionNode(IdentifierNode('>'), a, b)

def smt_lt(a, b):
    return RelationExpressionNode(IdentifierNode('<'), a, b)

def smt_gte(a, b):
    return RelationExpressionNode(IdentifierNode('>='), a, b)

def smt_lte(a, b):
    return RelationExpressionNode(IdentifierNode('<='), a, b)

def smt_concat(a, b):
    return ConcatNode(a, b)

def smt_at(s, i):
    return AtNode(s, i)

def smt_len(a):
    return LengthNode(a)

def smt_str_to_re(s):
    return StrToReNode(s)

def smt_regex_in(s, r):
    return InReNode(s, r)

def smt_regex_concat(a, b):
    return ReConcatNode(a, b)

def smt_regex_plus(a):
    return RePlusNode(a)

def smt_regex_range(a, b):
    return ReRangeNode(a, b)

def smt_regex_star(a):
    return ReStarNode(a)

def smt_regex_union(a, b):
    return ReUnionNode(a, b)

# commands
def smt_assert(exp):
    return AssertNode(exp)

def smt_declare_var(identifier):
    return FunctionDeclarationNode(identifier, BracketsNode([]), AtomicSortNode('String'))

def smt_declare_const(identifier):
    return ConstantDeclarationNode(identifier, AtomicSortNode('String'))

def smt_check_sat():
    return CheckSatNode()

def smt_get_model():
    return GetModelNode()

def _smt_status(status):
    return MetaCommandNode(IdentifierNode('set-info'), [SettingNode('status'), MetaDataNode(status)])

def smt_is_sat():
    return _smt_status('sat')

def smt_is_unsat():
    return _smt_status('unsat')

def smt_string_logic():
    return MetaCommandNode(IdentifierNode('set-logic'), [IdentifierNode('QF_S')])
