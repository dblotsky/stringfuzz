import re
import sys
import random
import string

from stringfuzz.ast import ExpressionNode, StringLitNode
from stringfuzz.parser import parse

__all__ = [
    'unprintable',
]

EXCLUDED_CHARS    = '\n\t\x00'
UNPRINTABLE_CHARS = [chr(i) for i in range(32) if chr(i) not in EXCLUDED_CHARS]
ALL_CHARS         = string.printable

# TODO:
#      sanity check that the transformation should not inject
# if len(UNPRINTABLE_CHARS) < len(ALL_CHARS):
#     print("REALLY BAD ERROR: 'unprintable' transformation loses data", file=sys.stderr)
#     exit(1)

# TODO:
#      fix pick_unprintable to pick without replacement
def pick_unprintable():
    return random.choice(UNPRINTABLE_CHARS)

def make_charmap():
    return {c : pick_unprintable() for c in ALL_CHARS}

def make_unprintable_string(s, charmap):
    return ''.join(charmap[c] for c in s)

def make_unprintable_expression(expression, charmap):

    for i in range(len(expression.body)):

        arg = expression.body[i]

        # recurse down expressions
        if isinstance(arg, ExpressionNode):
            make_unprintable_expression(arg, charmap)

        # replace string literals
        elif isinstance(arg, StringLitNode):

            # create new string
            old_string = arg.value
            new_string = make_unprintable_string(old_string, charmap)

            # assign new literal
            expression.body[i] = StringLitNode(new_string)

# public API
def unprintable(s, language):
    expressions = parse(s, language)
    charmap     = make_charmap()

    for expression in expressions:
        make_unprintable_expression(expression, charmap)

    return expressions
