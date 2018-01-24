'''
Multiplying every integer literal by n and repeating
every character in a string literal n times for some n
'''

from stringfuzz.ast import StringLitNode, IntLitNode, ReRangeNode
from stringfuzz.ast_walker import ASTWalker
from stringfuzz.transformers.strip import strip

__all__ = [
    'multiply',
]

class MultiplyTransformer(ASTWalker):
    def __init__(self, ast, factor, re_range_flag):
        super(MultiplyTransformer, self).__init__(ast)
        self.factor = factor
        self.re_range_flag = re_range_flag

    def exit_literal(self, literal, parent):
        if isinstance(literal, StringLitNode):
            if isinstance(parent, ReRangeNode) and not self.re_range_flag:
                return
            new_val = ""
            for char in literal.value:
                new_val += char * self.factor
            literal.value = new_val
        elif isinstance(literal, IntLitNode):
            literal.value = literal.value * self.factor

# public API
def multiply(ast, factor, re_range_flag):
    ast = strip(ast)
    transformed = MultiplyTransformer(ast, factor, re_range_flag).walk()
    return transformed
