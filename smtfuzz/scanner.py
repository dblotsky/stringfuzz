import re

from smtfuzz.constants import *

__all__ = [
    'scan',
    'scan_file',
]

# data structures
class Token(object):

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __str__(self):
        return self.value

    def __repr__(self):
        return '{} {!r}'.format(self.name, self.value)

# token functions
def make_whitespace(s, w): return Token('WHITESPACE', w)
def make_identifier(s, w): return Token('IDENTIFIER', w)
def make_lparen(s, w):     return Token('LPAREN', w)
def make_rparen(s, w):     return Token('RPAREN', w)
def make_expr(s, w):       return Token('EXPRESSION', w)
def make_setting(s, w):    return Token('SETTING', w)
def make_sort(s, w):       return Token('SORT', w)
def make_string_lit(s, w): return Token('STRING_LIT', w[1:-1])
def make_bool_lit(s, w):   return Token('BOOL_LIT', w)
def make_int_lit(s, w):    return Token('INT_LIT', w)

# token lists
SMT_20_TOKENS = [
    (r'Int',  make_sort),
    (r'Bool', make_sort),

    (r'ite', make_expr),
    (r'not', make_expr),
    (r'and', make_expr),
    (r'or',  make_expr),

    (r'set-logic',        make_expr),
    (r'set-option',       make_expr),
    (r'set-info',         make_expr),
    (r'declare-sort',     make_expr),
    (r'define-sort',      make_expr),
    (r'declare-fun',      make_expr),
    (r'define-fun',       make_expr),
    (r'declare-const',    make_expr),
    (r'define-const',     make_expr),
    (r'declare-variable', make_expr),
    (r'define-variable',  make_expr),
    (r'push',             make_expr),
    (r'pop',              make_expr),
    (r'assert',           make_expr),
    (r'check-sat',        make_expr),
    (r'get-assertions',   make_expr),
    (r'get-proof',        make_expr),
    (r'get-model',        make_expr),
    (r'get-unsat-core',   make_expr),
    (r'get-value',        make_expr),
    (r'get-assignment',   make_expr),
    (r'get-option',       make_expr),
    (r'get-info',         make_expr),
    (r'exit',             make_expr),

    (r'\+',  make_expr),
    (r'-',   make_expr),
    (r'\*',  make_expr),
    (r'=',   make_expr),
    (r'<=',  make_expr),
    (r'<',   make_expr),
    (r'>=',  make_expr),
    (r'>',   make_expr),
    (r'div', make_expr),

    (r'\s+', make_whitespace),
    (r'\(', make_lparen),
    (r'\)', make_rparen),
    (r'[\w\d_]+', make_identifier),
    (r'true', make_bool_lit),
    (r'false', make_bool_lit),
    (r'\d+', make_int_lit),
    (r':[\w_-]+', make_setting),
]

SMT_20_STRING_TOKENS = [
    (r'String', make_sort),

    (r'CharAt',      make_expr),
    (r'Concat',      make_expr),
    (r'Contains',    make_expr),
    (r'EndsWith',    make_expr),
    (r'IndexOf',     make_expr),
    (r'Length',      make_expr),
    (r'RegexIn',     make_expr),
    (r'RegexConcat', make_expr),
    (r'Replace',     make_expr),
    (r'StartsWith',  make_expr),
    (r'Str2Reg',     make_expr),
    (r'Substring',   make_expr),

    (r'"(?:\\\"|[^"])*"', make_string_lit),
]

SMT_25_STRING_TOKENS = [
    (r'String', make_sort),

    (r'str\.to-int',   make_expr),
    (r'str\.from-int', make_expr),
    (r'str\.\+\+',     make_expr),
    (r'str\.at',       make_expr),
    (r'str\.contains', make_expr),
    (r'str\.from-int', make_expr),
    (r'str\.in\.re',   make_expr),
    (r'str\.indexof',  make_expr),
    (r'str\.len',      make_expr),
    (r'str\.prefixof', make_expr),
    (r'str\.replace',  make_expr),
    (r'str\.substr',   make_expr),
    (r'str\.suffixof', make_expr),
    (r'str\.to-int',   make_expr),
    (r'str\.to\.re',   make_expr),
    (r're\.\*',        make_expr),
    (r're\.\+',        make_expr),
    (r're\.\+\+',      make_expr),
    (r're\.range',     make_expr),
    (r're\.union',     make_expr),

    (r'"(?:""|[^"])*"', make_string_lit),
]

# lexicons
SMT_20_LEXICON        = SMT_20_TOKENS
SMT_20_STRING_LEXICON = SMT_20_STRING_TOKENS + SMT_20_LEXICON
SMT_25_STRING_LEXICON = SMT_25_STRING_TOKENS + SMT_20_LEXICON

# scanners
smt_20_scanner        = re.Scanner(SMT_20_LEXICON)
smt_20_string_scanner = re.Scanner(SMT_20_STRING_LEXICON)
smt_25_string_scanner = re.Scanner(SMT_25_STRING_LEXICON)

# public API
def scan(string, language):
    if language == SMT_20:
        tokens, remainder = smt_20_scanner.scan(string)
    elif language == SMT_20_STRING:
        tokens, remainder = smt_20_string_scanner.scan(string)
    elif language == SMT_25_STRING:
        tokens, remainder = smt_25_string_scanner.scan(string)
    else:
        raise ValueError('invalid language: {!r}'.format(language))

    if len(remainder) > 0:
        token_context = '\n'.join('    {} {!r}'.format(t.name, t.value) for t in tokens[-5:])
        text_context  = remainder[:100]
        raise IndexError('scanning error:\n{}\n    {!r}...'.format(token_context, text_context))

    return [t for t in tokens if t.name != 'WHITESPACE']

def scan_file(path, language):
    with open(path, 'r') as file:
        return scan(file.read(), language)
