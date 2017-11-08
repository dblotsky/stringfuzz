import re

from stringfuzz.scanner import scan
from stringfuzz.ast import *

__all__ = [
    'parse',
    'parse_file',
    'parse_tokens',
]

# data structures
class Stream(object):

    def __init__(self, tokens):
        self.current_token = None
        self.stream = (t for t in tokens)

    def advance(self):
        self.current_token = next(self.stream, None)

    def accept(self, name):
        if self.current_token is not None and self.current_token.name == name:
            self.advance()
            return True
        return False

    def peek(self):
        return self.current_token

    def expect(self, expected):
        previous = self.current_token
        if self.accept(expected):
            return previous
        raise IndexError('expected {}, got {!r}'.format(expected, self.current_token))

# parsers
def get_arg(s):
    arg = s.peek()

    # nested expression
    if s.accept('LPAREN'):
        return get_expression(s)

    # literal
    elif s.accept('BOOL_LIT'):
        if arg == 'true':
            return BoolLitNode(True)
        elif arg == 'false':
            return BoolLitNode(False)
    elif s.accept('INT_LIT'):
        return IntLitNode(int(arg.value))
    elif s.accept('STRING_LIT'):
        return StringLitNode(arg.value)

    # others
    elif s.accept('RE_ALLCHAR'):
        return ReAllCharNode()
    elif s.accept('IDENTIFIER'):
        return IdentifierNode(arg.value)
    elif s.accept('SORT'):
        return SortNode(arg.value)
    elif s.accept('SETTING'):
        return SettingNode(arg.value)

    else:
        return None

def expect_arg(s):
    result = get_arg(s)

    if result is None:
        raise IndexError('expected an argument, got {!r}'.format(s.peek()))

    return result

def get_expression(s):

    # empty parens case
    if s.accept('RPAREN'):
        return ArgsNode()

    # special expression cases
    if s.accept('CONCAT'):
        a = expect_arg(s)
        b = expect_arg(s)
        s.expect('RPAREN')
        return ConcatNode(a, b)

    elif s.accept('CONTAINS'):
        a = expect_arg(s)
        b = expect_arg(s)
        s.expect('RPAREN')
        return ContainsNode(a, b)

    elif s.accept('AT'):
        a = expect_arg(s)
        b = expect_arg(s)
        s.expect('RPAREN')
        return AtNode(a, b)

    elif s.accept('LENGTH'):
        a = expect_arg(s)
        s.expect('RPAREN')
        return LengthNode(a)

    elif s.accept('INDEXOF'):
        a = expect_arg(s)
        b = expect_arg(s)
        s.expect('RPAREN')
        return IndexOfNode(a, b)

    elif s.accept('INDEXOF2'):
        a = expect_arg(s)
        b = expect_arg(s)
        c = expect_arg(s)
        s.expect('RPAREN')
        return IndexOf2Node(a, b, c)

    elif s.accept('PREFIXOF'):
        a = expect_arg(s)
        b = expect_arg(s)
        s.expect('RPAREN')
        return PrefixOfNode(a, b)

    elif s.accept('SUFFIXOF'):
        a = expect_arg(s)
        b = expect_arg(s)
        s.expect('RPAREN')
        return SuffixOfNode(a, b)

    elif s.accept('REPLACE'):
        a = expect_arg(s)
        b = expect_arg(s)
        c = expect_arg(s)
        s.expect('RPAREN')
        return StringReplaceNode(a, b, c)

    elif s.accept('SUBSTRING'):
        a = expect_arg(s)
        b = expect_arg(s)
        c = expect_arg(s)
        s.expect('RPAREN')
        return SubstringNode(a, b, c)

    elif s.accept('FROM_INT'):
        a = expect_arg(s)
        s.expect('RPAREN')
        return FromIntNode(a)

    elif s.accept('TO_INT'):
        a = expect_arg(s)
        s.expect('RPAREN')
        return ToIntNode(a)

    elif s.accept('IN_RE'):
        a = expect_arg(s)
        b = expect_arg(s)
        s.expect('RPAREN')
        return InReNode(a, b)

    elif s.accept('STR_TO_RE'):
        a = expect_arg(s)
        s.expect('RPAREN')
        return StrToReNode(a)

    elif s.accept('RE_CONCAT'):
        a = expect_arg(s)
        b = expect_arg(s)
        s.expect('RPAREN')
        return ReConcatNode(a, b)

    elif s.accept('RE_STAR'):
        a = expect_arg(s)
        s.expect('RPAREN')
        return ReStarNode(a)

    elif s.accept('RE_PLUS'):
        a = expect_arg(s)
        s.expect('RPAREN')
        return RePlusNode(a)

    elif s.accept('RE_RANGE'):
        a = expect_arg(s)
        b = expect_arg(s)
        s.expect('RPAREN')
        return ReRangeNode(a, b)

    elif s.accept('RE_UNION'):
        a = expect_arg(s)
        b = expect_arg(s)
        s.expect('RPAREN')
        return ReUnionNode(a, b)

    # expression case
    body   = []
    symbol = s.expect('SYMBOL').value

    # consume args
    while True:
        arg = get_arg(s)

        # break on no arg
        if arg is None:
            break

        body.append(arg)

    s.expect('RPAREN')

    return ExpressionNode(symbol, body)

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
