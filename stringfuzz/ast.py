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
    'ContainsNode',
    'AtNode',
    'LengthNode',
    'IndexOfNode',
    'IndexOf2Node',
    'PrefixOfNode',
    'SuffixOfNode',
    'StringReplaceNode',
    'SubstringNode',
    'FromIntNode',
    'ToIntNode',
    'InReNode',
    'StrToReNode',
    'ReConcatNode',
    'ReStarNode',
    'RePlusNode',
    'ReRangeNode',
    'ReUnionNode',
    'ReAllCharNode'
]

# data structures
class ASTNode(object):
    pass

class LiteralNode(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return 'Literal<{}>'.format(self.value)

class BoolLitNode(LiteralNode):
    def __repr__(self):
        return 'BoolLit<{}>'.format(self.value)

class IntLitNode(LiteralNode):
    def __repr__(self):
        return 'IntLit<{}>'.format(self.value)

class StringLitNode(LiteralNode):
    def __len__(self):
        return len(self.value)

    def __repr__(self):
        return 'StringLit<{!r}>'.format(self.value)

class SortNode(ASTNode):
    def __init__(self, sort):
        self.sort = sort

    def __repr__(self):
        return 'Sort<{}>'.format(self.sort)

class SettingNode(ASTNode):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return 'Setting<{}>'.format(self.name)

class IdentifierNode(ASTNode):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return 'Id<{}>'.format(self.name)

class ArgsNode(ASTNode):
    def __repr__(self):
        return 'Args<()>'

class ReAllCharNode(ASTNode):
    def __repr__(self):
        return 'ReAllChar<.>'

class ExpressionNode(ASTNode):
    def __init__(self, symbol, body):
        assert symbol is not None
        self.symbol = symbol
        self.body   = body

    def __repr__(self):
        contents = ' '.join(map(repr, [self.symbol] + self.body))
        return 'Expr<{}>'.format(contents)

class SpecificExpression(ExpressionNode):
    def __init__(self, symbol, body):
        super(SpecificExpression, self).__init__(symbol, body)

    def __repr__(self):
        contents = ' '.join(map(repr, self.body))
        return '{}<{}>'.format(self.symbol, contents)

class ConcatNode(SpecificExpression):
    def __init__(self, a, b):
        super(ConcatNode, self).__init__('Concat', [a, b])

class ContainsNode(SpecificExpression):
    def __init__(self, a, b):
        super(ContainsNode, self).__init__('Contains', [a, b])

class AtNode(SpecificExpression):
    def __init__(self, a, b):
        super(AtNode, self).__init__('At', [a, b])

class LengthNode(SpecificExpression):
    def __init__(self, a):
        super(LengthNode, self).__init__('Length', [a])

class IndexOfNode(SpecificExpression):
    def __init__(self, a, b):
        super(IndexOfNode, self).__init__('IndexOf', [a, b])

class IndexOf2Node(SpecificExpression):
    def __init__(self, a, b, c):
        super(IndexOf2Node, self).__init__('IndexOf2', [a, b, c])

class PrefixOfNode(SpecificExpression):
    def __init__(self, a, b):
        super(PrefixOfNode, self).__init__('PrefixOf', [a, b])

class SuffixOfNode(SpecificExpression):
    def __init__(self, a, b):
        super(SuffixOfNode, self).__init__('SuffixOf', [a, b])

class StringReplaceNode(SpecificExpression):
    def __init__(self, a, b, c):
        super(StringReplaceNode, self).__init__('Replace', [a, b, c])

class SubstringNode(SpecificExpression):
    def __init__(self, a, b, c):
        super(SubstringNode, self).__init__('Substring', [a, b, c])

class FromIntNode(SpecificExpression):
    def __init__(self, a):
        super(FromIntNode, self).__init__('FromInt', [a])

class ToIntNode(SpecificExpression):
    def __init__(self, a):
        super(ToIntNode, self).__init__('ToInt', [a])

class InReNode(SpecificExpression):
    def __init__(self, a, b):
        super(InReNode, self).__init__('InRegex', [a, b])

class StrToReNode(SpecificExpression):
    def __init__(self, a):
        super(StrToReNode, self).__init__('Str2Re', [a])

class ReConcatNode(SpecificExpression):
    def __init__(self, a, b):
        super(ReConcatNode, self).__init__('ReConcat', [a, b])

class ReStarNode(SpecificExpression):
    def __init__(self, a):
        super(ReStarNode, self).__init__('ReStar', [a])

class RePlusNode(SpecificExpression):
    def __init__(self, a):
        super(RePlusNode, self).__init__('RePlus', [a])

class ReRangeNode(SpecificExpression):
    def __init__(self, a, b):
        super(ReRangeNode, self).__init__('ReRange', [a, b])

class ReUnionNode(SpecificExpression):
    def __init__(self, a, b):
        super(ReUnionNode, self).__init__('ReUnion', [a, b])
