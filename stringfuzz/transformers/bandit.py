'''
The bandit transformer takes in an instance and an operator, and inserts a new 
occurence of the operator into the instance.
'''

import sys

import random

from stringfuzz.types import STR_RET, INT_RET, BOOL_RET, RX_RET
from stringfuzz.ast_walker import ASTWalker

from stringfuzz.ast import FunctionDeclarationNode, ConstantDeclarationNode

from stringfuzz.generators.random_ast import make_random_expression

ALL_SUPPORTED = STR_RET + INT_RET + BOOL_RET + RX_RET
OPERATORS = [x.get_symbol() for x in ALL_SUPPORTED]

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
        self.variables = {}
        self.exists = False
        self.defs = {}

    def enter_identifier(self, identifier, parent):
        sort = self.defs[identifier.name]
        if sort not in self.variables:
            self.variables[sort] = []
        
        if identifier not in self.variables[sort]:
            self.variables[sort].append(identifier)

    def enter_expression(self, expr, parent):
        if isinstance(expr, FunctionDeclarationNode):
            ident = expr.body[0].name
            sort = expr.body[2].name
            self.defs[ident] = sort
            return

        if isinstance(expr, ConstantDeclarationNode):
            ident = expr.body[0].name
            sort = expr.body[1].name
            self.defs[ident] = sort
            return

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
    sig     = op_node.get_signature()
    old_sig = old_expr.get_signature()
    args    = []

    for j in range(len(sig)):
        s = sig[j]
        found = False
        for i in range(len(old_expr.body)):
            index = (i+j) % len(old_expr.body)
            e = old_expr.body[index]
            if old_sig[index] == s:
                args.append(e)
                found = True
                break
        if not found:
            args.append(make_random_expression(variables, s, depth))

    return [old_expr, op_node(*args)]

# public API
def bandit(ast, op, depth):

    tmp = find_node(op)
    if tmp is None:
        print("NOT SUPPORTED: " + op, file=sys.stderr)
        return ast 

    op = tmp
    finder = BanditFinder(ast, op)
    while finder.target == None:
        finder.walk()
        if not finder.exists:
            return ast
    pair = gen_pair(op, finder.target, finder.variables, depth)
    transformed = BanditTransformer(ast, pair).walk()
    return transformed
