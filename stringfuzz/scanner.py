import re
import string

from stringfuzz.constants import *

__all__ = [
    'scan',
    'scan_file',
    'ScanningError',
    'ALPHABET',
    'WHITESPACE',
]

# data structures
class ScanningError(ValueError):
    pass

class Token(object):

    def __init__(self, name, value, position):
        self.name = name
        self.value = value
        self.position = position

    def __str__(self):
        return self.value

    def __repr__(self):
        return '{} {!r} @ {}'.format(self.name, self.value, self.position)

# helpers
def strip_quotes(string_literal):
    return string_literal[1:-1]

def unescape(string_literal):
    return string_literal.encode().decode('unicode_escape')

def replace_double_quotes(string_literal):
    return string_literal.replace("\"\"", "\"")

# token functions
def make_whitespace(s, w): return Token('WHITESPACE', w,       s.match.start())
def make_identifier(s, w): return Token('IDENTIFIER', w,       s.match.start())
def make_lparen(s, w):     return Token('LPAREN',     w,       s.match.start())
def make_rparen(s, w):     return Token('RPAREN',     w,       s.match.start())
def make_setting(s, w):    return Token('SETTING',    w,       s.match.start())
def make_bool_lit(s, w):   return Token('BOOL_LIT',   w,       s.match.start())
def make_int_lit(s, w):    return Token('INT_LIT',    w,       s.match.start())
def make_sym(s, w):        return Token('IDENTIFIER', w,       s.match.start())

def make_string_lit(s, w):
    literal = unescape(strip_quotes(w))
    return Token('STRING_LIT', literal, s.match.start())

def make_string_lit_25(s, w):
    literal = replace_double_quotes(unescape(strip_quotes(w)))
    return Token('STRING_LIT', literal, s.match.start())

# specific symbol tokens
def make_meta_expr(s, w):        return Token('META_EXPR',   w, s.match.start())
def make_declare_fun(s, w):      return Token('DECLARE_FUN', w, s.match.start())
def make_define_fun(s, w):       return Token('DEFINE_FUN',  w, s.match.start())
def make_contains(s, w):         return Token('CONTAINS',    w, s.match.start())
def make_concat(s, w):           return Token('CONCAT',      w, s.match.start())
def make_at(s, w):               return Token('AT',          w, s.match.start())
def make_indexof_var_args(s, w): return Token('INDEXOFVAR',  w, s.match.start())
def make_indexof_2_args(s, w):   return Token('INDEXOF',     w, s.match.start())
def make_indexof_3_args(s, w):   return Token('INDEXOF2',    w, s.match.start())
def make_prefixof(s, w):         return Token('PREFIXOF',    w, s.match.start())
def make_suffixof(s, w):         return Token('SUFFIXOF',    w, s.match.start())
def make_replace(s, w):          return Token('REPLACE',     w, s.match.start())
def make_substring(s, w):        return Token('SUBSTRING',   w, s.match.start())
def make_str_from_int(s, w):     return Token('FROM_INT',    w, s.match.start())
def make_str_to_int(s, w):       return Token('TO_INT',      w, s.match.start())
def make_length(s, w):           return Token('LENGTH',      w, s.match.start())
def make_in_re(s, w):            return Token('IN_RE',       w, s.match.start())
def make_str_to_re(s, w):        return Token('STR_TO_RE',   w, s.match.start())
def make_re_allchar(s, w):       return Token('RE_ALLCHAR',  w, s.match.start())
def make_re_concat(s, w):        return Token('RE_CONCAT',   w, s.match.start())
def make_re_star(s, w):          return Token('RE_STAR',     w, s.match.start())
def make_re_plus(s, w):          return Token('RE_PLUS',     w, s.match.start())
def make_re_range(s, w):         return Token('RE_RANGE',    w, s.match.start())
def make_re_union(s, w):         return Token('RE_UNION',    w, s.match.start())

# constants
ALPHABET     = string.digits + string.ascii_letters + string.punctuation
WHITESPACE   = string.whitespace
ID_CHAR      = r'[\w._\+\-\*\=%?!$_~&^<>@/|:\\]'
SETTING_CHAR = r'[\w._\+\-\*\=%?!$_~&^<>@/|:]'

# token lists
# NOTE:
#      more specific patterns (e.g. reserved words) have to come before more
#      general patterns (e.g. identifiers) because otherwise the more general
#      pattern will match before the more specific one
SMT_20_TOKENS = [

    # Boolean functions
    (r'ite', make_sym),
    (r'not', make_sym),
    (r'and', make_sym),
    (r'or',  make_sym),

    # commands
    (r'set-logic',        make_meta_expr),
    (r'set-option',       make_meta_expr),
    (r'set-info',         make_meta_expr),
    (r'declare-sort',     make_sym),
    (r'define-sort',      make_sym),
    (r'declare-fun',      make_declare_fun),
    (r'define-fun',       make_define_fun),
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

    # math operators
    (r'\+',  make_sym),
    (r'-',   make_sym),
    (r'\*',  make_sym),
    (r'=',   make_sym),
    (r'<=',  make_sym),
    (r'<',   make_sym),
    (r'>=',  make_sym),
    (r'>',   make_sym),
    (r'div', make_sym),

    # whitespace
    (r'\s+', make_whitespace),

    # parens
    (r'\(', make_lparen),
    (r'\)', make_rparen),

    # boolean literals
    (r'true',  make_bool_lit),
    (r'false', make_bool_lit),

    # int literals: digits not followed by identifier characters
    (r'\d+(?!' + ID_CHAR + r')', make_int_lit),

    # comments
    (r';[^\n]*', make_whitespace),
    (r'//[^\n]*', make_whitespace),

    # settings: can use most characters, and start with colons
    (r':' + SETTING_CHAR + r'+', make_setting),

    # identifiers: can use most characters, but can't start with digits
    (ID_CHAR + r'(?<![\d])' + ID_CHAR + r'*', make_identifier),
]

SMT_20_STRING_TOKENS = [

    # string
    (r'Concat',     make_concat),
    (r'CharAt',     make_at),
    (r'Contains',   make_contains),
    (r'Length',     make_length),
    (r'Indexof2',   make_indexof_3_args),
    (r'IndexOf2',   make_indexof_3_args),
    (r'StartsWith', make_prefixof),
    (r'EndsWith',   make_suffixof),
    (r'Replace',    make_replace),
    (r'Substring',  make_substring),

    # regex
    (r'Str2Reg',        make_str_to_re),
    (r'RegexIn',        make_in_re),
    (r'RegexStar',      make_re_star),
    (r'RegexConcat',    make_re_concat),
    (r'RegexPlus',      make_re_plus),
    (r'RegexCharRange', make_re_range),
    (r'RegexUnion',     make_re_union),

    # unique
    (r'Indexof',     make_indexof_2_args),
    (r'IndexOf',     make_indexof_2_args),
    (r'RegexDigit',  make_sym),
    (r'LastIndexOf', make_sym),
    (r'LastIndexof', make_sym),

    # quotes
    (r'"(?:\\.|[^\\"])*"', make_string_lit),
]

SMT_25_STRING_TOKENS = [

    # string
    (r'str\.\+\+',     make_concat),
    (r'str\.at',       make_at),
    (r'str\.contains', make_contains),
    (r'str\.len',      make_length),
    (r'str\.indexof',  make_indexof_var_args),
    (r'str\.prefixof', make_prefixof),
    (r'str\.suffixof', make_suffixof),
    (r'str\.replace',  make_replace),
    (r'str\.substr',   make_substring),

    # regex
    (r'str\.to\.re',   make_str_to_re),
    (r'str\.in\.re',   make_in_re),
    (r're\.\*',        make_re_star),
    (r're\.\+\+',      make_re_concat),
    (r're\.\+',        make_re_plus),
    (r're\.range',     make_re_range),
    (r're\.union',     make_re_union),
    (r're\.allchar',   make_re_allchar),
    (r're\.all',       make_re_allchar),

    # integer
    (r'str\.from\.int', make_str_from_int),
    (r'str\.to\.int',   make_str_to_int),

    # quotes
    (r'"(?:""|[^"])*"', make_string_lit_25),
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
        raise ScanningError('invalid language: {!r}'.format(language))

    if len(remainder) > 0:
        token_context = '\n'.join('    {} {!r}'.format(t.name, t.value) for t in tokens[-5:])
        text_context  = remainder[:100]
        raise ScanningError('scanning error:\n{}\n    {!r}...'.format(token_context, text_context))

    return [t for t in tokens if t.name != 'WHITESPACE']

def scan_file(path, language):
    with open(path, 'r') as file:
        return scan(file.read(), language)
