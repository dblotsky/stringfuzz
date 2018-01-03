import random
import string

from stringfuzz.ast import *
from stringfuzz.ast_walker import ASTWalker
from stringfuzz.parser import parse

__all__ = [
    'rotate',
]

class RotateTransformer(ASTWalker):
    def __init__(self, ast):
        super(RotateTransformer, self).__init__(ast)

    @property
    def ast(self):
        return self._ASTWalker__ast

    def exit_expression(self, expr):
        for uniform in [ALL_INT_ARGS, ALL_RX_ARGS, ALL_STR_ARGS]:
            # need at least two top level children
            if any([isinstance(expr, C) for C in uniform]) and len(expr.body) > 1:
                for i in range(len(expr.body)):
                    if any([isinstance(expr.body[i], C) for C in uniform]):
                        # rotate clockwise
                        # j is the other top level child
                        if i == len(expr.body)-1:
                            j = 0
                        else:
                            j = len(expr.body)-1
                        temp = expr.body[j]
                        expr.body[j] = expr.body[i].body[0]
                        new_body = expr.body[i].body[1:] + [temp]
                        expr.body[i].body = new_body

# public API
def rotate(s, language):
    expressions = parse(s, language)
    transformer = RotateTransformer(expressions).walk()
    return transformer.ast
