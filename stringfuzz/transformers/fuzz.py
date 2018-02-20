'''
The Fuzz transformer performs two types of transformations.
The first is for literals. The second is for operators.

Literals are fuzzed to similar literals. For example,
an integer literal x will be replaced with x+r where
r is a random number between -x and x. String literals
are processed character by character. Each character can either
remain in the updated string, be replaced by a random string,
or be deleted with equal probability.

Operators are fuzzed, with 50% probability, to a new operator
with the same function type. For example, regex * can be fuzzed
to regex +.
'''

import random

from stringfuzz.ast import IntLitNode, StringLitNode, ReRangeNode
from stringfuzz.types import REPLACEABLE_OPS
from stringfuzz.ast_walker import ASTWalker
from stringfuzz.generators import random_text

__all__ = [
    'fuzz',
]

def fuzz_char(c):

    # with equal probability: replace, keep, add, or delete a character
    operation = random.randint(1,4)

    # replace it
    if operation == 1:
        return random_text(1)

    # keep it the same
    if operation == 2:
        return c

    # add a new character
    if operation == 3:
        return c + random_text(1)

    # delete it
    return ''

def fuzz_string(string):
    return ''.join(fuzz_char(c) for c in string)

class LitTransformer(ASTWalker):
    def __init__(self, ast, skip_re_range):
        super().__init__(ast)
        self.skip_re_range = skip_re_range

    def exit_literal(self, literal, parent):

        # int literal
        if isinstance(literal, IntLitNode):

            # maintain sign of literal
            literal.value += random.randint(-literal.value, literal.value)

        # string literal
        elif isinstance(literal, StringLitNode):

            # skip children of regex range if required
            if isinstance(parent, ReRangeNode) and self.skip_re_range:
                return

            # create new value for literal
            new_val = fuzz_string(literal.value)

            # replace old value with new value
            literal.value = new_val

    def exit_expression(self, expr, parent):
        for type_list in REPLACEABLE_OPS:
            for i in range(len(expr.body)):

                # check if it's a replaceable type; if so, randomly replace it
                replaceable = [isinstance(expr.body[i], C) for C in type_list]
                if any(replaceable):
                    choice       = random.choice(type_list)
                    expr.body[i] = choice(*expr.body[i].body)

# public API
def fuzz(ast, skip_re_range):
    transformed = LitTransformer(ast, skip_re_range).walk()
    return transformed
