'''
The graft transform picks a subtree and a leaf at random
and swaps them for each type.
'''

import random

from stringfuzz.ast import *
from stringfuzz.types import *
from stringfuzz.ast_walker import ASTWalker
from stringfuzz.generators import random_text
from stringfuzz.parser import parse

__all__ = [
    'graft',
]

class GraftTransformer(ASTWalker):
    def __init__(self, ast, pairs):
        super(GraftTransformer, self).__init__(ast)
        self.pairs = pairs

    @property
    def ast(self):
        return self._ASTWalker__ast

    def enter_expression(self, expr):
        for i in range(len(expr.body)):
            for pair in self.pairs:
                if expr.body[i] == pair[0]:
                    expr.body[i] = pair[1]
                elif expr.body[i] == pair[1]:
                    expr.body[i] = pair[0]

class GraftFinder(ASTWalker):
    def __init__(self, ast):
        super(GraftFinder, self).__init__(ast)
        #            expr, lit
        self.str  = [None, None]
        self.bool = [None, None]
        self.int  = [None, None]
        self.rx   = [None, None]

    @property
    def pairs(self):
        pairs = []
        if all(self.str):
            pairs.append(self.str)
        if all(self.bool):
            pairs.append(self.bool)
        if all(self.int):
            pairs.append(self.int)
        if all(self.rx):
            pairs.append(self.rx)
        return pairs

    def enter_literal(self, literal):
        replace = random.choice([True, False])
        if isinstance(literal, StringLitNode):
            if self.str[1]:
                if replace:
                    self.str[1] = literal
            else:
                self.str[1] = literal
        elif isinstance(literal, BoolLitNode):
            if self.bool[1]:
                if replace:
                    self.bool[1] = literal
            else:
                self.bool[1] = literal
        elif isinstance(literal, IntLitNode):
            if self.int[1]:
                if replace:
                    self.int[1] = literal
            else:
                self.int[1] = literal

    def enter_identifier(self, ident):
        #TODO How to check type of identifiers?
        # if self.str[1]:
        #     if random.random() < 0.5:
        #         self.str[1] = ident
        # else:
        #     self.str[1] = ident
        pass

    def enter_expression(self, expr):
        replace = random.choice([True, False])
        if isinstance(expr, StrToReNode):
            # take StrToReNode's to be literals for RX
            if self.rx[1]:
                if replace:
                    self.rx[1] = expr
            else:
                self.rx[1] = expr

        # assign expr part of pair
        elif any([isinstance(expr, C) for C in STR_RET]):
            if self.str[0]:
                if replace:
                    self.str[0] = expr
            else:
                self.str[0] = expr
        elif any([isinstance(expr, C) for C in INT_RET]):
            if self.int[0]:
                if replace:
                    self.int[0] = expr
            else:
                self.int[0] = expr
        elif any([isinstance(expr, C) for C in BOOL_RET]):
            if self.bool[0]:
                if replace:
                    self.bool[0] = expr
            else:
                self.bool[0] = expr
        elif any([isinstance(expr, C) for C in RX_RET]):
            if self.rx[0]:
                if replace:
                    self.rx[0] = expr
            else:
                self.rx[0] = expr


# public API
def graft(s, language):
    expressions = parse(s, language)
    finder = GraftFinder(expressions).walk()
    transformer = GraftTransformer(expressions, finder.pairs).walk()
    return transformer.ast
