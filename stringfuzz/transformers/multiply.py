'''
Multiplying every integer literal by n and repeating
every character in a string literal n times for some n
'''

import random

from stringfuzz.ast import StringLitNode, IntLitNode
from stringfuzz.ast_walker import ASTWalker
from stringfuzz.parser import parse

__all__ = [
    'multiply',
]

class MultiplyTransformer(ASTWalker):
    def __init__(self, ast, factor):
        super(MultiplyTransformer, self).__init__(ast)
        self.factor = factor

    @property
    def ast(self):
        return self._ASTWalker__ast

    def exit_literal(self, literal):
        if isinstance(literal, StringLitNode):
            new_val = ""
            for char in literal.value:
                new_val += char * self.factor
            literal.value = new_val
        elif isinstance(literal, IntLitNode):
            literal.value = literal.value * self.factor

# public API
def multiply(ast, factor):
    transformer = MultiplyTransformer(ast, factor).walk()
    return transformer.ast
