import random
import string

from stringfuzz.ast import *
from stringfuzz.ast_walker import ASTWalker

__all__ = [
    'rotate',
]

class ASTTransformer(ASTWalker):
    def __init__(self, ast):
        super(ASTTransformer, self).__init__(ast)

    @property
    def ast(self):
        return self._ASTWalker__ast

    def exit_expression(self, expr):
        if isinstance(expr, ConcatNode):
            if isinstance(expr.body[0], ConcatNode):
                # rotate clockwise ll, lr, r
                temp = expr.body[1]
                expr.body[1] = expr.body[0].body[0]
                expr.body[0].body[0] = expr.body[0].body[1]
                expr.body[0].body[1] = temp
            if isinstance(expr.body[1], ConcatNode):
                # rotate clockwise l, rl, rr
                temp = expr.body[0]
                expr.body[0] = expr.body[1].body[0]
                expr.body[1].body[0] = expr.body[1].body[1]
                expr.body[1].body[1] = temp   
        elif isinstance(expr, ReConcatNode):
            if isinstance(expr.body[0], ReConcatNode):
                # rotate clockwise ll, lr, r
                temp = expr.body[1]
                expr.body[1] = expr.body[0].body[0]
                expr.body[0].body[0] = expr.body[0].body[1]
                expr.body[0].body[1] = temp
            if isinstance(expr.body[1], ReConcatNode):
                # rotate clockwise l, rl, rr
                temp = expr.body[0]
                expr.body[0] = expr.body[1].body[0]
                expr.body[1].body[0] = expr.body[1].body[1]
                expr.body[1].body[1] = temp
        elif isinstance(expr, ReUnionNode):
            if isinstance(expr.body[0], ReUnionNode):
                # rotate clockwise ll, lr, r
                temp = expr.body[1]
                expr.body[1] = expr.body[0].body[0]
                expr.body[0].body[0] = expr.body[0].body[1]
                expr.body[0].body[1] = temp
            if isinstance(expr.body[1], ReUnionNode):
                # rotate clockwise l, rl, rr
                temp = expr.body[0]
                expr.body[0] = expr.body[1].body[0]
                expr.body[1].body[0] = expr.body[1].body[1]
                expr.body[1].body[1] = temp
        elif isinstance(expr, InReNode):
            if isinstance(expr.body[0], InReNode):
                # rotate clockwise ll, lr, r
                temp = expr.body[1]
                expr.body[1] = expr.body[0].body[0]
                expr.body[0].body[0] = expr.body[0].body[1]
                expr.body[0].body[1] = temp
            if isinstance(expr.body[1], InReNode):
                # rotate clockwise l, rl, rr
                temp = expr.body[0]
                expr.body[0] = expr.body[1].body[0]
                expr.body[1].body[0] = expr.body[1].body[1]
                expr.body[1].body[1] = temp


# public API
def rotate(expressions):
    transformer = ASTTransformer(expressions).walk()
    return transformer.ast
