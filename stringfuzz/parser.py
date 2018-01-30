import re

from stringfuzz.scanner import scan
from stringfuzz.ast import *
from stringfuzz.util import join_terms_with

__all__ = [
    'parse',
    'parse_file',
    'parse_tokens',
    'ParsingError',
]

# constants
MAX_ERROR_SIZE = 200
UNDERLINE      = '-'

MESSAGE_FORMAT = '''Parsing error on line {number}:

{context}{actual_value}
{underline}^
{filler}expected {expected}, got {actual_type} {actual_value!r}'''

# data structures
class Stream(object):

    def __init__(self, tokens, text):
        self.text = text
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
        raise ParsingError(expected, self)

class ParsingError(IndexError):
    def __init__(self, expected, stream):

        # compute actual value
        actual_token = stream.current_token
        if actual_token is not None:
            actual_type  = actual_token.name
            actual_value = actual_token.value
            error_index  = actual_token.position
        else:
            actual_type  = 'nothing'
            actual_value = ''
            error_index  = len(stream.text) - 1

        # get error context
        parsed_text = stream.text[0:error_index]
        context     = parsed_text[-MAX_ERROR_SIZE:]

        if len(context) < len(parsed_text):
            context = '... ' + context

        # find row and column of error
        try:
            latest_newline_index = parsed_text.rindex('\n')
        except ValueError as e:
            latest_newline_index = 0

        error_row    = parsed_text.count('\n') + 1
        error_column = error_index - latest_newline_index - 1

        # compose message
        message = MESSAGE_FORMAT.format(
            number       = error_row,
            context      = context,
            underline    = (UNDERLINE * error_column),
            filler       = (' ' * error_column),
            expected     = expected,
            actual_type  = actual_type,
            actual_value = actual_value,
        )

        # pass message to superclass
        super().__init__(message)

# parsers
def accept_arg(s):
    token = s.peek()

    # nested expression
    if s.accept('LPAREN'):
        expression = expect_expression(s)
        s.expect('RPAREN')
        return expression

    # literal
    if s.accept('BOOL_LIT'):
        if token.value == 'true':
            return BoolLitNode(True)
        elif token.value == 'false':
            return BoolLitNode(False)

    if s.accept('INT_LIT'):
        return IntLitNode(int(token.value))

    if s.accept('STRING_LIT'):
        return StringLitNode(token.value)

    # others
    if s.accept('RE_ALLCHAR'):
        return ReAllCharNode()

    if s.accept('IDENTIFIER'):
        return IdentifierNode(token.value)

    if s.accept('SETTING'):
        return SettingNode(token.value)

    return None

def accept_meta_arg(s):
    arg = s.peek()

    if (
        s.accept('BOOL_LIT') or
        s.accept('INT_LIT') or
        s.accept('STRING_LIT') or
        s.accept('IDENTIFIER')
    ):
        return MetaDataNode(arg.value)

    if s.accept('SETTING'):
        return SettingNode(arg.value)

    return None

def expect_identifier(s):
    token = s.expect('IDENTIFIER')
    return IdentifierNode(token.value)

def expect_arg(s):
    result = accept_arg(s)

    if result is None:
        raise ParsingError('an argument', s)

    return result

def expect_sort(s):
    result = accept_sort(s)

    if result is None:
        raise ParsingError('a sort', s)

    return result

def repeat_star(s, getter):
    terms = []

    while True:
        term = getter(s)

        # break on no term
        if term is None:
            break

        terms.append(term)

    return terms

def accept_sort(s):

    # compound sort
    if s.accept('LPAREN'):
        symbol = expect_identifier(s)
        sorts  = [expect_sort(s)]
        sorts += repeat_star(s, accept_sort)
        s.expect('RPAREN')
        return CompoundSortNode(symbol, sorts)

    # atomic sort
    token = s.peek()
    if s.accept('IDENTIFIER'):
        return AtomicSortNode(token.value)

    return None

def accept_sorted_var(s):
    if s.accept('LPAREN'):
        name = expect_identifier(s)
        sort = expect_sort(s)
        s.expect('RPAREN')
        return SortedVarNode(name, sort)

    return None

def expect_expression(s):

    # declarations and definitions
    if s.accept('DECLARE_FUN'):
        name = expect_identifier(s)

        s.expect('LPAREN')
        signature = repeat_star(s, accept_sort)
        s.expect('RPAREN')

        return_sort = expect_sort(s)

        return FunctionDeclarationNode(name, BracketsNode(signature), return_sort)

    if s.accept('DEFINE_FUN'):
        name = expect_identifier(s)

        s.expect('LPAREN')
        signature = repeat_star(s, accept_sorted_var)
        s.expect('RPAREN')

        return_sort = expect_sort(s)

        s.expect('LPAREN')
        body = expect_expression(s)
        s.expect('RPAREN')

        return FunctionDefinitionNode(name, BracketsNode(signature), return_sort, body)

    if s.accept('DECLARE_CONST'):
        name        = expect_identifier(s)
        return_sort = expect_sort(s)
        return ConstantDeclarationNode(name, return_sort)

    # special expression cases
    if s.accept('CONCAT'):

        # first two args are mandatory
        a = expect_arg(s)
        b = expect_arg(s)

        # more args are optional
        other_args = repeat_star(s, accept_arg)

        # re-format n-ary concats into binary concats
        concat = join_terms_with([a, b] + other_args, ConcatNode)

        return concat

    if s.accept('CONTAINS'):
        a = expect_arg(s)
        b = expect_arg(s)
        return ContainsNode(a, b)

    if s.accept('AT'):
        a = expect_arg(s)
        b = expect_arg(s)
        return AtNode(a, b)

    if s.accept('LENGTH'):
        a = expect_arg(s)
        return LengthNode(a)

    if s.accept('INDEXOFVAR'):

        # two arguments are expected
        a = expect_arg(s)
        b = expect_arg(s)

        # the third argument may or may not be there
        c = accept_arg(s)

        if c is not None:
            return IndexOf2Node(a, b, c)

        return IndexOfNode(a, b)

    if s.accept('INDEXOF'):
        a = expect_arg(s)
        b = expect_arg(s)
        return IndexOfNode(a, b)

    if s.accept('INDEXOF2'):
        a = expect_arg(s)
        b = expect_arg(s)
        c = expect_arg(s)
        return IndexOf2Node(a, b, c)

    if s.accept('PREFIXOF'):
        a = expect_arg(s)
        b = expect_arg(s)
        return PrefixOfNode(a, b)

    if s.accept('SUFFIXOF'):
        a = expect_arg(s)
        b = expect_arg(s)
        return SuffixOfNode(a, b)

    if s.accept('REPLACE'):
        a = expect_arg(s)
        b = expect_arg(s)
        c = expect_arg(s)
        return StringReplaceNode(a, b, c)

    if s.accept('SUBSTRING'):
        a = expect_arg(s)
        b = expect_arg(s)
        c = expect_arg(s)
        return SubstringNode(a, b, c)

    if s.accept('FROM_INT'):
        a = expect_arg(s)
        return FromIntNode(a)

    if s.accept('TO_INT'):
        a = expect_arg(s)
        return ToIntNode(a)

    if s.accept('IN_RE'):
        a = expect_arg(s)
        b = expect_arg(s)
        return InReNode(a, b)

    if s.accept('STR_TO_RE'):
        a = expect_arg(s)
        return StrToReNode(a)

    if s.accept('RE_CONCAT'):

        # first two args are mandatory
        a = expect_arg(s)
        b = expect_arg(s)

        # more args are optional
        other_args = repeat_star(s, accept_arg)

        # re-format n-ary concats into binary concats
        concat = join_terms_with([a, b] + other_args, ReConcatNode)

        return concat

    if s.accept('RE_STAR'):
        a = expect_arg(s)
        return ReStarNode(a)

    if s.accept('RE_PLUS'):
        a = expect_arg(s)
        return RePlusNode(a)

    if s.accept('RE_RANGE'):
        a = expect_arg(s)
        b = expect_arg(s)
        return ReRangeNode(a, b)

    if s.accept('RE_UNION'):

        # first two args are mandatory
        a = expect_arg(s)
        b = expect_arg(s)

        # more args are optional
        other_args = repeat_star(s, accept_arg)

        # re-format n-ary concats into binary concats
        union = join_terms_with([a, b] + other_args, ReUnionNode)

        return union

    token = s.peek()
    if s.accept('META_COMMAND'):
        body = repeat_star(s, accept_meta_arg)
        return MetaCommandNode(token.value, body)

    # generic expression case
    name = expect_identifier(s)
    body = repeat_star(s, accept_arg)

    return ExpressionNode(name, body)

def get_expressions(s):

    expressions = []
    s.advance()

    while s.peek() is not None:
        s.expect('LPAREN')
        expressions.append(expect_expression(s))
        s.expect('RPAREN')

    return expressions

# public API
def parse_file(path, language):
    with open(path, 'r') as file:
        return parse(file.read(), language)

def parse(text, language):
    return parse_tokens(scan(text, language), language, text)

def parse_tokens(tokens, language, text):
    return get_expressions(Stream(tokens, text))
