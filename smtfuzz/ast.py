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
    'ExpressionNode',
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

class BoolLitNode(LiteralNode):

    def __str__(self):
        if self.value == True:
            return 'true'
        else:
            return 'false'

class IntLitNode(LiteralNode):

    def __str__(self):
        return self.value

class StringLitNode(LiteralNode):

    def __str__(self):
        return '\"{}\"'.format(smt_encode_string(self.value))

    def __len__(self):
        return len(self.value)

class SortNode(ASTNode):

    def __init__(self, sort):
        self.sort = sort

    def __str__(self):
        return self.sort

class SettingNode(ASTNode):

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

class IdentifierNode(ASTNode):

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

class ExpressionNode(ASTNode):

    def __init__(self, name, body):
        self.name = name
        self.body = body

    def __repr__(self):

        contents = ''

        if self.name:
            contents += self.name

        if len(self.body) > 0:
            contents += ' ' + ' '.join(map(str, self.body))

        return '(' + contents + ')'
