'''
Reversing every string literal
'''

from stringfuzz.ast import StringLitNode, ConcatNode, ReConcatNode
from stringfuzz.ast_walker import ASTWalker
from stringfuzz.parser import parse

__all__ = [
    'reverse',
]

class ReverseTransformer(ASTWalker):
    def __init__(self, ast):
        super(ReverseTransformer, self).__init__(ast)

    @property
    def ast(self):
        return self._ASTWalker__ast

    def exit_literal(self, literal):
        if isinstance(literal, StringLitNode):
            literal.value = literal.value[::-1]
    
    def exit_expression(self, expr):
        if isinstance(expr, (ConcatNode, ReConcatNode)):
            expr.body = reversed(expr.body)

# public API
def reverse(s, language):
    expressions = parse(s, language)
    transformer = ReverseTransformer(expressions).walk()
    return transformer.ast
