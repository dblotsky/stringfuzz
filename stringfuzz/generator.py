import re

from stringfuzz.constants import SMT_20, SMT_20_STRING, SMT_25_STRING
from stringfuzz.scanner import scan, ALPHABET, WHITESPACE
from stringfuzz.ast import *

__all__ = [
    'generate',
    'generate_file',
]

# exceptions
class NotSupported(ValueError):
    def __init__(self, e, language):
        message = 'can\'t generate {!r} in language {!r}'.format(e, language)
        super(NotSupported, self).__init__(message)

# functions
def needs_encoding(c):
    return c not in ALPHABET

def encode_char(c, language):
    if c == '"':
        if language == SMT_25_STRING:
            return '""'
        else:
            return '\\"'
    elif c == '\\':
        return '\\\\'
    elif c in WHITESPACE:
        return repr(c)
    elif needs_encoding(c):
        return '\\x{:0>2x}'.format(ord(c))
    return c

def encode_string(s, language):
    encoded = ''.join(encode_char(c, language) for c in s)
    return '"' + encoded + '"'

def generate_node(node, language):

    # generate each known node
    if isinstance(node, ExpressionNode):
        return generate_expr(node, language)

    elif isinstance(node, LiteralNode):
        return generate_lit(node, language)

    elif isinstance(node, IdentifierNode):
        return node.name

    elif isinstance(node, SortNode):
        return node.sort

    elif isinstance(node, ArgsNode):
        return '()'

    elif isinstance(node, SettingNode):
        return ':{}'.format(node.name)

    elif isinstance(node, MetaDataNode):
        return node.value

    elif isinstance(node, ReAllCharNode):
        if language == SMT_25_STRING:
            return 're.allchar'
        else:
            raise NotSupported(node, language)

    # error out on all others
    else:
        raise NotImplementedError('no generator for {}'.format(type(node)))

def generate_lit(lit, language):
    if isinstance(lit, StringLitNode):
        return encode_string(lit.value, language)

    elif isinstance(lit, BoolLitNode):
        return str(lit.value).lower()

    elif isinstance(lit, IntLitNode):
        if (lit.value < 0):
            return '(- {})'.format(lit.value)
        return str(lit.value)

    else:
        raise NotImplementedError('unknown literal type {!r}'.format(lit))

def generate_expr(e, language):
    components = []

    # special expressions
    if isinstance(e, ConcatNode):
        if language == SMT_20_STRING:
            components.append('Concat')
        elif language == SMT_25_STRING:
            components.append('str.++')
        else:
            raise NotSupported(e, language)

    elif isinstance(e, ContainsNode):
        if language == SMT_20_STRING:
            components.append('Contains')
        elif language == SMT_25_STRING:
            components.append('str.contains')
        else:
            raise NotSupported(e, language)

    elif isinstance(e, AtNode):
        if language == SMT_20_STRING:
            components.append('CharAt')
        elif language == SMT_25_STRING:
            components.append('str.at')
        else:
            raise NotSupported(e, language)

    elif isinstance(e, LengthNode):
        if language == SMT_20_STRING:
            components.append('Length')
        elif language == SMT_25_STRING:
            components.append('str.len')
        else:
            raise NotSupported(e, language)

    elif isinstance(e, IndexOfNode):
        if language == SMT_20_STRING:
            components.append('IndexOf')
        elif language == SMT_25_STRING:
            components.append('str.indexof')
        else:
            raise NotSupported(e, language)

    elif isinstance(e, IndexOf2Node):
        if language == SMT_20_STRING:
            components.append('IndexOf2')
        elif language == SMT_25_STRING:
            components.append('str.indexof')
        else:
            raise NotSupported(e, language)

    elif isinstance(e, PrefixOfNode):
        if language == SMT_20_STRING:
            components.append('StartsWith')
        elif language == SMT_25_STRING:
            components.append('str.prefixof')
        else:
            raise NotSupported(e, language)

    elif isinstance(e, SuffixOfNode):
        if language == SMT_20_STRING:
            components.append('EndsWith')
        elif language == SMT_25_STRING:
            components.append('str.suffixof')
        else:
            raise NotSupported(e, language)

    elif isinstance(e, StringReplaceNode):
        if language == SMT_20_STRING:
            components.append('Replace')
        elif language == SMT_25_STRING:
            components.append('str.replace')
        else:
            raise NotSupported(e, language)

    elif isinstance(e, SubstringNode):
        if language == SMT_20_STRING:
            components.append('Substring')
        elif language == SMT_25_STRING:
            components.append('str.substr')
        else:
            raise NotSupported(e, language)

    elif isinstance(e, FromIntNode):
        if language == SMT_25_STRING:
            components.append('str.from.int')
        else:
            raise NotSupported(e, language)

    elif isinstance(e, ToIntNode):
        if language == SMT_25_STRING:
            components.append('str.to.int')
        else:
            raise NotSupported(e, language)

    elif isinstance(e, StrToReNode):
        if language == SMT_20_STRING:
            components.append('Str2Reg')
        elif language == SMT_25_STRING:
            components.append('str.to.re')
        else:
            raise NotSupported(e, language)

    elif isinstance(e, InReNode):
        if language == SMT_20_STRING:
            components.append('RegexIn')
        elif language == SMT_25_STRING:
            components.append('str.in.re')
        else:
            raise NotSupported(e, language)

    elif isinstance(e, ReConcatNode):
        if language == SMT_20_STRING:
            components.append('RegexConcat')
        elif language == SMT_25_STRING:
            components.append('re.++')
        else:
            raise NotSupported(e, language)

    elif isinstance(e, ReStarNode):
        if language == SMT_20_STRING:
            components.append('RegexStar')
        elif language == SMT_25_STRING:
            components.append('re.*')
        else:
            raise NotSupported(e, language)

    elif isinstance(e, RePlusNode):
        if language == SMT_20_STRING:
            components.append('RegexPlus')
        elif language == SMT_25_STRING:
            components.append('re.+')
        else:
            raise NotSupported(e, language)

    elif isinstance(e, ReRangeNode):
        if language == SMT_20_STRING:
            components.append('RegexCharRange')
        elif language == SMT_25_STRING:
            components.append('re.range')
        else:
            raise NotSupported(e, language)

    elif isinstance(e, ReUnionNode):
        if language == SMT_20_STRING:
            components.append('RegexUnion')
        elif language == SMT_25_STRING:
            components.append('re.union')
        else:
            raise NotSupported(e, language)

    # all other expressions
    else:
        components.append(e.symbol)

    # generate args
    components.extend(generate_node(node, language) for node in e.body)

    return '({})'.format(' '.join(components))

# public API
def generate_file(ast, language, path):
    with open(path, 'w+') as file:
        file.write(generate(ast, language))

def generate(ast, language):
    return '\n'.join(generate_expr(e, language) for e in ast)
