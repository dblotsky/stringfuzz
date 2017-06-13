import string

'''
The AST is a list of ASTNodes.
'''

__all__ = [
    'ASTNode',
    'LiteralNode',
    'BoolLitNode',
    'IntLitNode',
    'StringLitNode',
    'SortNode',
    'SettingNode',
    'IdentifierNode',
    'ArgsNode',
    'ExpressionNode',
    'ConcatNode',
]

# constants
LITERAL_CHARS = set(string.ascii_letters + string.punctuation + string.digits)

# helpers
def needs_encoding(c):
    return c not in LITERAL_CHARS

def smt_encode_char(c):
    if needs_encoding(c):
        return '\\x{:0>2x}'.format(ord(c))
    return c

def smt_encode_string(s):
    return ''.join(map(smt_encode_char, s))

# data structures
class ASTNode(object):
    pass

class LiteralNode(ASTNode):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

    def __repr__(self):
        return 'Literal({})'.format(self.value)

class BoolLitNode(LiteralNode):

    def __str__(self):
        if self.value == True:
            return 'true'
        else:
            return 'false'

    def __repr__(self):
        return 'BoolLit({})'.format(self.value)

class IntLitNode(LiteralNode):

    def __str__(self):
        return self.value

    def __repr__(self):
        return 'IntLit({})'.format(self.value)

class StringLitNode(LiteralNode):

    def __str__(self):
        return '\"{}\"'.format(smt_encode_string(self.value))

    def __len__(self):
        return len(self.value)

    def __repr__(self):
        return 'StringLit({!r})'.format(self.value)

class SortNode(ASTNode):

    def __init__(self, sort):
        self.sort = sort

    def __str__(self):
        return self.sort

    def __repr__(self):
        return 'Sort({})'.format(self.sort)

class SettingNode(ASTNode):

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return 'Setting({})'.format(self.name)

class IdentifierNode(ASTNode):

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return 'Identifier({})'.format(self.name)

class ArgsNode(ASTNode):

    def __init__(self):
        pass

    def __str__(self):
        return '()'

    def __repr__(self):
        return 'Args()'

class ExpressionNode(ASTNode):

    def __init__(self, symbol, body):
        assert symbol is not None
        self.symbol = symbol
        self.body   = body

    def __repr__(self):

        contents = self.symbol

        node_name = self.__class__.__name__.replace('Node', '')

        if len(self.body) > 0:
            contents += ' ' + ' '.join(map(repr, self.body))

        return '{}({})'.format(node_name, contents)

class ConcatNode(ExpressionNode):

    def __init__(self, a, b):
        super(ConcatNode, self).__init__('Concat', [a, b])
