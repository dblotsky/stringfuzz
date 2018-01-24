'''
Reversing every string literal
'''

from stringfuzz.ast import StringLitNode, ConcatNode, ReConcatNode
from stringfuzz.ast_walker import ASTWalker
from stringfuzz.transformers.strip import strip

__all__ = [
    'reverse',
]

class ReverseTransformer(ASTWalker):
    def __init__(self, ast):
        super(ReverseTransformer, self).__init__(ast)

    def exit_literal(self, literal, parent):
        if isinstance(literal, StringLitNode):
            literal.value = literal.value[::-1]
    
    def exit_expression(self, expr, parent):
        if isinstance(expr, (ConcatNode, ReConcatNode)):
            expr.body = reversed(expr.body)

# public API
def reverse(ast):
    ast = strip(ast)
    transformed = ReverseTransformer(ast).walk()
    return transformed
