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

from stringfuzz.ast import IntLitNode, StringLitNode
from stringfuzz.types import REPLACEABLE_OPS
from stringfuzz.ast_walker import ASTWalker
from stringfuzz.generators import random_text

__all__ = [
    'fuzz',
]

class LitTransformer(ASTWalker):
    def __init__(self, ast):
        super(LitTransformer, self).__init__(ast)

    def exit_literal(self, literal, parent):
        if isinstance(literal, IntLitNode):
            literal.value = random.randint(-literal.value, literal.value)
        elif isinstance(literal, StringLitNode):
            new_val = ""
            for c in literal.value:
                # With equal probability replace, keep, or delete.
                choice = random.randint(1,3)
                if choice == 1:
                    # replace it with a sequence
                    length = len(literal.value)
                    length = random.randint(1, length)
                    new_val += random_text(length)
                elif choice == 2:
                    new_val += c
                else:
                    #delete it
                    pass
            literal.value = new_val
    
    def exit_expression(self, expr, parent):
        for type_list in REPLACEABLE_OPS:
            for i in range(len(expr.body)):
                # Check if its a replaceable type, if so, randomly replace it
                replaceable = [isinstance(expr.body[i], C) for C in type_list]
                if any(replaceable):
                    choice = random.choice(type_list)
                    expr.body[i] = choice(*expr.body[i].body)

# public API
def fuzz(ast):
    transformed = LitTransformer(ast).walk()
    return transformed
