import re

from smtfuzz.scanner import scan
from smtfuzz.ast import *

__all__ = [
    'parse',
    'parse_file',
    'parse_tokens',
]

# data structures
class Stream(object):

    def __init__(self, tokens):
        self.current = None
        self.stream = (t for t in tokens)

    def advance(self):
        self.current = next(self.stream, None)

    def accept(self, name):
        if self.current is not None and self.current.name == name:
            self.advance()
            return True
        return False

    def peek(self):
        return self.current

    def expect(self, expected):
        previous = self.current
        if self.accept(expected):
            return previous
        raise IndexError('expected {}, got {!r}'.format(expected, self.current))

# parsers
def get_expression(s):

    # empty parens case
    if s.accept('RPAREN'):
        return ExpressionNode(None, [])

    # expression case
    body = []
    name = s.expect('EXPRESSION').value

    while True:
        arg = s.peek()

        # nested expression
        if s.accept('LPAREN'):
            body.append(get_expression(s))

        # literal
        elif s.accept('BOOL_LIT'):
            if arg == 'true':
                body.append(BoolLitNode(True))
            elif arg == 'false':
                body.append(BoolLitNode(False))
        elif s.accept('INT_LIT'):
            body.append(IntLitNode(int(arg.value)))
        elif s.accept('STRING_LIT'):
            body.append(StringLitNode(arg.value))

        # others
        elif s.accept('IDENTIFIER'):
            body.append(IdentifierNode(arg.value))
        elif s.accept('SORT'):
            body.append(SortNode(arg.value))
        elif s.accept('SETTING'):
            body.append(SettingNode(arg.value))

        # end of expression
        else:
            s.expect('RPAREN')
            break

    return ExpressionNode(name, body)

def get_expressions(s):

    expressions = []
    s.advance()

    while s.peek() is not None:
        s.expect('LPAREN')
        expressions.append(get_expression(s))

    return expressions

# public API
def parse_file(path, language):
    with open(path, 'r') as file:
        return parse(file.read(), language)

def parse(string, language):
    return parse_tokens(scan(string, language), language)

def parse_tokens(tokens, language):
    return get_expressions(Stream(tokens))
