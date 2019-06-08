'''
The bandit transformer takes in an instance and an operator, and inserts a new 
occurence of the operator into the instance.
'''

import random

from stringfuzz.types import STR_RET, INT_RET, BOOL_RET, RX_RET
from stringfuzz.ast_walker import ASTWalker

from stringfuzz.generators.random_ast import make_random_expression

OPERATORS = ['=', '>', '<', '>=', '<=', 'Concat', 'Contains', 'At', 'Length', 'IndexOf', 'IndexOf2', 'PrefixOf', 'SuffixOf', 'Replace', 'ReInter', 'ReUnion', 'ReRange', 'RePlus', 'ReStar', 'ReConcat', 'Str2Re', 'InRegex', 'ToInt', 'FromInt', 'Substring']

ALL_SUPPORTED = STR_RET + INT_RET + BOOL_RET + RX_RET

__all__ = [
    'bandit',
]

class BanditTransformer(ASTWalker):
    def __init__(self, ast, pair):
        super().__init__(ast)
        self.pair = pair

    def enter_expression(self, expr, parent):
        for i in range(len(expr.body)):
            if expr.body[i] == self.pair[0]:
                expr.body[i] = self.pair[1]

class BanditFinder(ASTWalker):
    def __init__(self, ast, op):
        super().__init__(ast)
        self.op     = op
        self.target = None
        self.variables = []
        self.exists = False

    def enter_identifier(self, identifier, parent):
        if identifier not in self.variables:
            self.variables.append(identifier)

    def enter_expression(self, expr, parent):
        replace = random.choice([True, False])
        if self.op.get_symbol() == expr.get_symbol():
            return

        if self.op in STR_RET and any([isinstance(expr, C) for C in STR_RET]):
            self.exists = True
            if replace:
                self.target = expr
        elif self.op in INT_RET and any([isinstance(expr, C) for C in INT_RET]):
            self.exists = True
            if replace:
                self.target = expr
        elif self.op in BOOL_RET and any([isinstance(expr, C) for C in BOOL_RET]):
            self.exists = True
            if replace:
                self.target = expr
        elif self.op in RX_RET and any([isinstance(expr, C) for C in RX_RET]):
            self.exists = True
            if replace:
                self.target = expr

def find_node(op):
    for node in ALL_SUPPORTED:
        if node.get_symbol() == op:
            return node
    return None

def gen_pair(op_node, old_expr, variables, depth):
    sig = op_node.get_signature()
    args = []

    for j in range(len(sig)):
        s = sig[j]
        found = False
        for i in range(len(old_expr.body)):
            e = old_expr.body[(i+j) % len(old_expr.body)]
            if e.get_sort() == s:
                args.append(e)
                found = True
                break
        if not found:
            args.append(make_random_expression(variables, s, depth))

    return [old_expr, op_node(*args)]

# public API
def bandit(ast, op, depth):
    op = find_node(op)
    finder = BanditFinder(ast, op)
    while finder.target == None:
        finder.walk()
        if not finder.exists:
            return ast
    pair = gen_pair(op, finder.target, finder.variables, depth)
    transformed = BanditTransformer(ast, pair).walk()
    return transformed