'''
Permuting the alphabet in every string literal.
'''

import random
import string

from stringfuzz.ast import StringLitNode
from stringfuzz.ast_walker import ASTWalker
from stringfuzz.parser import parse

__all__ = [
    'translate',
]

class TranslateTransformer(ASTWalker):
    def __init__(self, ast):
        super(TranslateTransformer, self).__init__(ast)
        shuffled = list(string.ascii_letters)
        random.shuffle(shuffled)
        shuffled = ''.join(shuffled)
        self.table = str.maketrans(string.ascii_letters, shuffled)

    @property
    def ast(self):
        return self._ASTWalker__ast

    def exit_literal(self, literal):
        if isinstance(literal, StringLitNode):
            literal.value = literal.value.translate(self.table)

# public API
def translate(s, language):
    expressions = parse(s, language)
    transformer = TranslateTransformer(expressions).walk()
    return transformer.ast
