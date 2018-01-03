import random

from stringfuzz.ast import *
from stringfuzz.ast_walker import ASTWalker
from stringfuzz.parser import parse

__all__ = [
    'extend',
]

PROBABILITY = 0.2

class ExtendTransformer(ASTWalker):
    def __init__(self, ast):
        super(ExtendTransformer, self).__init__(ast)
        self.bool_extension = None
        self.string_extension = None
        self.int_extension = None

    @property
    def ast(self):
        return self._ASTWalker__ast

    def enter_expression(self, expr):
        if bool_type(expr):
            self.bool_extension = expr
        elif string_type(expr):
            self.string_extension = expr
        elif int_type(expr):
            self.int_extension = expr

    def exit_expression(self, expr):
        for i in range(len(expr.body)):
            if isinstance(expr.body[i], StringLitNode) and self.string_extension:
                if random.random() <= PROBABILITY:
                    expr.body[i] = self.string_extension
            elif isinstance(expr.body[i], BoolLitNode) and self.bool_extension:
                if random.random() <= PROBABILITY:
                    expr.body[i] = self.bool_extension
            elif isinstance(expr.body[i], IntLitNode) and self.int_extension:
                if random.random() <= PROBABILITY:
                    expr.body[i] = self.int_extension

def bool_type(expr):
    if isinstance(expr, ContainsNode):
        return True
    elif isinstance(expr, PrefixOfNode):
        return True
    elif isinstance(expr, SuffixOfNode):
        return True
    elif isinstance(expr, InReNode):
        return True
    return False

def string_type(expr):
    if isinstance(expr, ConcatNode):
        return True
    elif isinstance(expr, AtNode):
        return True
    elif isinstance(expr, StringReplaceNode):
        return True
    elif isinstance(expr, FromIntNode):
        return True
    elif isinstance(expr, SubstringNode):
        return True
    return False

def int_type(expr):
    if isinstance(expr, LengthNode):
        return True
    elif isinstance(expr, IndexOfNode):
        return True
    elif isinstance(expr, IndexOf2Node):
        return True
    elif isinstance(expr, ToIntNode):
        return True
    return False

# public API
def extend(s, language):
    expressions = parse(s, language)
    transformer = ExtendTransformer(expressions).walk()
    return transformer.ast
