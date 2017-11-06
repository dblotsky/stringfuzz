import re
import string

from stringfuzz.constants import *

__all__ = [
    'scan',
    'scan_file',
    'ALPHABET',
    'WHITESPACE',
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
def make_setting(s, w):    return Token('SETTING', w)
def make_sort(s, w):       return Token('SORT', w)
def make_string_lit(s, w): return Token('STRING_LIT', w[1:-1])
def make_bool_lit(s, w):   return Token('BOOL_LIT', w)
def make_int_lit(s, w):    return Token('INT_LIT', w)
def make_sym(s, w):        return Token('SYMBOL', w)

# specific symbol tokens
def make_contains(s, w):   return Token('CONTAINS', w)
def make_concat(s, w):     return Token('CONCAT', w)
def make_at(s, w):         return Token('AT', w)
def make_length(s, w):     return Token('LENGTH', w)
def make_in_re(s, w):      return Token('IN_RE', w)
def make_str_to_re(s, w):  return Token('STR_TO_RE', w)
def make_re_allchar(s, w): return Token('RE_ALLCHAR', w)
def make_re_concat(s, w):  return Token('RE_CONCAT', w)
def make_re_star(s, w):    return Token('RE_STAR', w)
def make_re_plus(s, w):    return Token('RE_PLUS', w)
def make_re_range(s, w):   return Token('RE_RANGE', w)
def make_re_union(s, w):   return Token('RE_UNION', w)

# constants
ALPHABET   = string.digits + string.ascii_letters + string.punctuation
WHITESPACE = string.whitespace

# token lists
SMT_20_TOKENS = [
    (r'Int',  make_sort),
    (r'Bool', make_sort),

    (r'ite', make_sym),
    (r'not', make_sym),
    (r'and', make_sym),
    (r'or',  make_sym),

    (r'set-logic',        make_sym),
    (r'set-option',       make_sym),
    (r'set-info',         make_sym),
    (r'declare-sort',     make_sym),
    (r'define-sort',      make_sym),
    (r'declare-fun',      make_sym),
    (r'define-fun',       make_sym),
    (r'declare-const',    make_sym),
    (r'define-const',     make_sym),
    (r'declare-variable', make_sym),
    (r'define-variable',  make_sym),
    (r'push',             make_sym),
    (r'pop',              make_sym),
    (r'assert',           make_sym),
    (r'check-sat',        make_sym),
    (r'get-assertions',   make_sym),
    (r'get-proof',        make_sym),
    (r'get-model',        make_sym),
    (r'get-unsat-core',   make_sym),
    (r'get-value',        make_sym),
    (r'get-assignment',   make_sym),
    (r'get-option',       make_sym),
    (r'get-info',         make_sym),
    (r'exit',             make_sym),

    (r'\+',  make_sym),
    (r'-',   make_sym),
    (r'\*',  make_sym),
    (r'=',   make_sym),
    (r'<=',  make_sym),
    (r'<',   make_sym),
    (r'>=',  make_sym),
    (r'>',   make_sym),
    (r'div', make_sym),

    (r'\s+',           make_whitespace),
    (r'\n?\s*;[^\n]*', make_whitespace),

    (r'\(',       make_lparen),
    (r'\)',       make_rparen),
    (r'[\w\d_]+', make_identifier),
    (r'true',     make_bool_lit),
    (r'false',    make_bool_lit),
    (r'\d+',      make_int_lit),
    (r':[\w_-]+', make_setting),
]

SMT_20_STRING_TOKENS = [
    (r'String', make_sort),

    (r'CharAt',      make_at),
    (r'Concat',      make_concat),
    (r'Contains',    make_contains),
    (r'EndsWith',    make_sym),
    (r'IndexOf',     make_sym),
    (r'Indexof',     make_sym),
    (r'Length',      make_length),
    (r'RegexIn',     make_in_re),
    (r'RegexStar',   make_re_star),
    (r'RegexPlus',   make_re_plus),
    (r'RegexConcat', make_re_concat),
    (r'RegexUnion',  make_re_union),
    (r'Replace',     make_sym),
    (r'StartsWith',  make_sym),
    (r'Str2Reg',     make_str_to_re),
    (r'Substring',   make_sym),

    (r'"(?:\\.|[^\\"])*"', make_string_lit),
]

SMT_25_STRING_TOKENS = [
    (r'String', make_sort),

    (r'str\.to-int',   make_sym),
    (r'str\.from-int', make_sym),
    (r'str\.\+\+',     make_concat),
    (r'str\.at',       make_at),
    (r'str\.contains', make_contains),
    (r'str\.from-int', make_sym),
    (r'str\.in\.re',   make_in_re),
    (r'str\.indexof',  make_sym),
    (r'str\.len',      make_length),
    (r'str\.prefixof', make_sym),
    (r'str\.replace',  make_sym),
    (r'str\.substr',   make_sym),
    (r'str\.suffixof', make_sym),
    (r'str\.to-int',   make_sym),
    (r'str\.to\.re',   make_str_to_re),
    (r're\.\*',        make_re_star),
    (r're\.\+\+',      make_re_concat),
    (r're\.\+',        make_re_plus),
    (r're\.range',     make_re_range),
    (r're\.union',     make_re_union),
    (r're\.allchar',   make_re_allchar),
    (r're\.all',       make_re_allchar),

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
