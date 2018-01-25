'''
Multiplying every integer literal by n and repeating
every character in a string literal n times for some n
'''

from stringfuzz.ast import StringLitNode, IntLitNode, ReRangeNode
from stringfuzz.ast_walker import ASTWalker

__all__ = [
    'multiply',
]

class MultiplyTransformer(ASTWalker):
    def __init__(self, ast, factor, skip_re_range):
        super(MultiplyTransformer, self).__init__(ast)
        self.factor = factor
        self.skip_re_range = skip_re_range

    def exit_literal(self, literal, parent):
        if isinstance(literal, StringLitNode):
            if isinstance(parent, ReRangeNode) and self.skip_re_range:
                return
            new_val = ""
            for char in literal.value:
                new_val += char * self.factor
            literal.value = new_val
        elif isinstance(literal, IntLitNode):
            literal.value = literal.value * self.factor

# public API
def multiply(ast, factor, skip_re_range):
    transformed = MultiplyTransformer(ast, factor, skip_re_range).walk()
    return transformed
