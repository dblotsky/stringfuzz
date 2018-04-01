import re

from stringfuzz.constants import SMT_20, SMT_20_STRING, SMT_25_STRING
from stringfuzz.scanner import scan, ALPHABET, WHITESPACE
from stringfuzz.ast import *

__all__ = [
    'generate',
    'generate_file',
    'NotSupported',
]

# exceptions
class NotSupported(ValueError):
    def __init__(self, e, language):
        message = 'can\'t generate {!r} in language {!r}'.format(e, language)
        super().__init__(message)

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

    if isinstance(node, SortedVarNode):
        return '({} {})'.format(generate_node(node.name, language), generate_node(node.sort, language))

    if isinstance(node, LiteralNode):
        return generate_lit(node, language)

    if isinstance(node, IdentifierNode):
        return node.name

    if isinstance(node, AtomicSortNode):
        return node.name

    if isinstance(node, CompoundSortNode):
        return '({} {})'.format(generate_node(node.symbol, language), ' '.join(generate_node(s, language) for s in node.sorts))

    if isinstance(node, BracketsNode):
        return '({})'.format(' '.join(generate_node(s, language) for s in node.body))

    if isinstance(node, SettingNode):
        return '{}'.format(generate_node(node.name, language))

    if isinstance(node, MetaDataNode):
        return node.value

    if isinstance(node, ReAllCharNode):
        if language == SMT_25_STRING:
            return 're.allchar'
        else:
            raise NotSupported(node, language)

    if isinstance(node, str):
        return node

    # error out on all others
    raise NotImplementedError('no generator for {}'.format(type(node)))

def generate_lit(lit, language):
    if isinstance(lit, StringLitNode):
        return encode_string(lit.value, language)

    if isinstance(lit, BoolLitNode):
        return str(lit.value).lower()

    if isinstance(lit, IntLitNode):
        if (lit.value < 0):
            return '(- {})'.format(lit.value)
        return str(lit.value)

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

    elif isinstance(e, ReInterNode):
        if language == SMT_20_STRING:
            # I don't think intersection is even defined for 2.0
            components.append('RegexInter')
        elif language == SMT_25_STRING:
            components.append('re.inter')
        else:
            raise NotSupported(e, language)

    # all other expressions
    else:
        components.append(generate_node(e.symbol, language))

    # generate args
    components.extend(generate_node(n, language) for n in e.body)

    return '({})'.format(' '.join(components))

# public API
def generate_file(ast, language, path):
    with open(path, 'w+') as file:
        file.write(generate(ast, language))

def generate(ast, language):
    return '\n'.join(generate_node(e, language) for e in ast)
