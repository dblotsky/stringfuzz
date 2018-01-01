import random

from stringfuzz.ast import *
from stringfuzz.scanner import ALPHABET, WHITESPACE
from stringfuzz.ast_walker import ASTWalker
from stringfuzz.generators import random_text

__all__ = [
    'litfuzz',
]

ALL_CHARS = ALPHABET + WHITESPACE
PROBABILITY = 0.5


class LitTransformer(ASTWalker):
    def __init__(self, ast):
        super(LitTransformer, self).__init__(ast)

    @property
    def ast(self):
        return self._ASTWalker__ast

    def exit_literal(self, literal):
        if isinstance(literal, IntLitNode):
            literal.value = random.randint(-literal.value, literal.value)
        elif isinstance(literal, StringLitNode):
            new_val = ""
            for c in literal.value:
                if random.random() <= PROBABILITY:
                    # replace it with a sequence
                    length = len(literal.value)
                    length = random.randint(1, length)
                    new_val += random_text(length)
                else:
                    if random.random() <= PROBABILITY:
                        #delete it
                        pass
                    else:
                        new_val += c
            literal.value = new_val
    
    def exit_expression(self, expr):
        # Do some regix mixing
        for i in range(len(expr.body)):
            if isinstance(expr.body[i], ReConcatNode):
                if random.random() <= PROBABILITY:
                    expr.body[i] = ReUnionNode(*expr.body[i].body)
            elif isinstance(expr.body[i], ReUnionNode):
                if random.random() <= PROBABILITY:
                    expr.body[i] = ReConcatNode(*expr.body[i].body)
            elif isinstance(expr.body[i], RePlusNode):
                if random.random() <= PROBABILITY:
                    expr.body[i] = ReStarNode(*expr.body[i].body)
            elif isinstance(expr.body[i], ReStarNode):
                if random.random() <= PROBABILITY:
                    expr.body[i] = RePlusNode(*expr.body[i].body)

# public API
def litfuzz(expressions):
    transformer = LitTransformer(expressions).walk()
    return transformer.ast
