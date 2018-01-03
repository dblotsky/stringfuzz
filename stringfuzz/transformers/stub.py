import random

from stringfuzz.ast import *
from stringfuzz.ast_walker import ASTWalker
from stringfuzz.generators import random_text
from stringfuzz.parser import parse

__all__ = [
    'stub',
]

PROBABILITY = 0.1
MAX_SIZE = 10

class StubTransformer(ASTWalker):
    def __init__(self, ast):
        super(StubTransformer, self).__init__(ast)

    @property
    def ast(self):
        return self._ASTWalker__ast

    def enter_expression(self, expr):
        for i in range(len(expr.body)):
            if isinstance(expr.body[i], ConcatNode):
                if random.random() <= PROBABILITY:
                    length = random.randint(0, MAX_SIZE)
                    expr.body[i] = StringLitNode(random_text(length))
            if isinstance(expr.body[i], StringReplaceNode):
                if random.random() <= PROBABILITY:
                    length = random.randint(0, MAX_SIZE)
                    expr.body[i] = StringLitNode(random_text(length))
            if isinstance(expr.body[i], SubstringNode):
                if random.random() <= PROBABILITY:
                    length = random.randint(0, MAX_SIZE)
                    expr.body[i] = StringLitNode(random_text(length))

# public API
def stub(s, language):
    expressions = parse(s, language)
    transformer = StubTransformer(expressions).walk()
    return transformer.ast
