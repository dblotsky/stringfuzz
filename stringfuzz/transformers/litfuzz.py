import random

from stringfuzz.ast import IntLitNode, StringLitNode
from stringfuzz.scanner import ALPHABET, WHITESPACE
from stringfuzz.ast_walker import ASTWalker

__all__ = [
    'litfuzz',
]

ALL_CHARS = ALPHABET + WHITESPACE
PROBABILITY = 0.25


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
                    #delete it
                    pass
                else:
                    if random.random() <= PROBABILITY:
                        new_val += c
                    else:
                        # replace it with a sequence
                        length = len(literal.value)
                        length = random.randint(1, length)
                        new_val += ''.join(random.choice(ALL_CHARS) for i in range(length))
            literal.value = new_val

# public API
def litfuzz(expressions):
    transformer = LitTransformer(expressions).walk()
    return transformer.ast
