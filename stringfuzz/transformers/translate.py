'''
Permuting the alphabet in every string literal.
'''

import random
import copy

from stringfuzz.ast import StringLitNode, ReRangeNode
from stringfuzz.ast_walker import ASTWalker
from stringfuzz import ALL_CHARS

__all__ = [
    'translate'
]

WITH_INTEGERS    = list(ALL_CHARS)
WITHOUT_INTEGERS = [c for c in ALL_CHARS if not c.isdecimal()]

class TranslateTransformer(ASTWalker):
    def __init__(self, ast, character_set, re_range_flag):
        super(TranslateTransformer, self).__init__(ast)
        self.table = self.make_table(character_set)
        self.re_range_flag = re_range_flag

    def make_table(self, character_set):
        shuffled = copy.copy(character_set)
        random.shuffle(shuffled)
        shuffled = ''.join(shuffled)
        character_set = ''.join(character_set)
        return str.maketrans(character_set, shuffled)

    def exit_literal(self, literal, parent):
        if isinstance(literal, StringLitNode):
            if isinstance(parent, ReRangeNode) and not self.re_range_flag:
                return
            literal.value = literal.value.translate(self.table)

# public API
def translate(ast, integer_flag, re_range_flag):
    if integer_flag:
        character_set = WITH_INTEGERS
    else:
        character_set = WITHOUT_INTEGERS
    transformed = TranslateTransformer(ast, character_set, re_range_flag).walk()
    return transformed
