'''
Permuting the alphabet in every string literal.
'''

import random
import string
import copy

from stringfuzz.ast import StringLitNode
from stringfuzz.ast_walker import ASTWalker
from stringfuzz import ALL_CHARS

__all__ = [
    'translate',
    'CHARACTER_SETS',
    'DEFAULT_CHARACTER_SET'
]

NON_INTEGERS = 'non-integers' 
LETTERS      = 'letters'
ALL_SYMBOLS  = 'all'

DEFAULT_CHARACTER_SET = NON_INTEGERS

CHARACTER_SETS = {
    NON_INTEGERS: [c for c in ALL_CHARS if not c.isdecimal()],
    LETTERS:      list(string.ascii_letters),
    ALL_SYMBOLS:  list(ALL_CHARS)
}

class TranslateTransformer(ASTWalker):
    def __init__(self, ast, character_set):
        super(TranslateTransformer, self).__init__(ast)
        shuffled = copy.copy(character_set)
        random.shuffle(shuffled)

        shuffled      = ''.join(shuffled)
        character_set = ''.join(character_set)

        self.table = str.maketrans(character_set, shuffled)

    @property
    def ast(self):
        return self._ASTWalker__ast

    def exit_literal(self, literal):
        if isinstance(literal, StringLitNode):
            literal.value = literal.value.translate(self.table)

# public API
def translate(ast, character_set):
    character_set = CHARACTER_SETS[character_set]
    transformer = TranslateTransformer(ast, character_set).walk()
    return transformer.ast
