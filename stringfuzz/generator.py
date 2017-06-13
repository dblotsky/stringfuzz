import re

from stringfuzz.constants import SMT_20, SMT_20_STRING, SMT_25_STRING
from stringfuzz.scanner import scan
from stringfuzz.ast import ExpressionNode, ConcatNode

__all__ = [
    'generate',
    'generate_file',
]

def generate_node(e, language):

    # expressions
    if isinstance(e, ExpressionNode):
        return generate_expr(e, language)

    # everything else
    else:
        return str(e)

def generate_expr(e, language):
    body = []

    # special expressions
    if isinstance(e, ConcatNode):
        if language == SMT_20_STRING:
            body.append('Concat')
        elif language == SMT_25_STRING:
            body.append('str.++')
        else:
            raise ValueError('can\'t generate {!r} from {!r}'.format(language, e))

    # all other expressions
    else:
        body.append(e.symbol)

    # generate args
    body.extend(generate_node(node, language) for node in e.body)

    return '({})'.format(' '.join(body))

# public API
def generate_file(ast, path, language):
    with open(path, 'r') as file:
        file.write(generate(ast, language))

def generate(ast, language):
    return '\n'.join(generate_expr(e, language) for e in ast)
