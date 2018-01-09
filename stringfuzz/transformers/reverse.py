'''
Reversing every string literal
'''

from stringfuzz.ast import StringLitNode, ConcatNode, ReConcatNode
from stringfuzz.ast_walker import ASTWalker

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
def reverse(ast):
    transformer = ReverseTransformer(ast).walk()
    return transformer.ast
