import string
import numbers

'''
The AST is a list of ASTNodes.
'''

__all__ = [
    'STRING_SORT',
    'INT_SORT',
    'BOOL_SORT',
    'REGEX_SORT',
    'UNIT_SORT',
    'ANY_SORT',
    'DECLARABLE_SORTS',

    'LiteralNode',
    'BoolLitNode',
    'IntLitNode',
    'StringLitNode',
    'AtomicSortNode',
    'CompoundSortNode',
    'SettingNode',
    'MetaDataNode',
    'IdentifierNode',
    'FunctionDeclarationNode',
    'FunctionDefinitionNode',
    'ConstantDeclarationNode',
    'SortedVarNode',
    'BracketsNode',
    'ExpressionNode',
    'GenericExpressionNode',
    'MetaCommandNode',
    'AssertNode',
    'CheckSatNode',
    'GetModelNode',
    'AndNode',
    'OrNode',
    'NotNode',
    'EqualNode',
    'GtNode',
    'LtNode',
    'GteNode',
    'LteNode',
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
    'ReInterNode',
    'ReAllCharNode',
]

# constants
STRING_SORT = 'String'
INT_SORT    = 'Int'
BOOL_SORT   = 'Bool'
REGEX_SORT  = 'Regex'
UNIT_SORT   = 'Unit'
ANY_SORT    = '*'

UNIT_SIGNATURE      = []
UNCHECKED_SIGNATURE = None

DECLARABLE_SORTS = [
    STRING_SORT,
    INT_SORT,
    BOOL_SORT,
]

SORT_TYPE      = str
SIGNATURE_TYPE = list

# helpers
def with_spaces(terms):
    return ' '.join(map(repr, terms))

# data structures
class _ASTNode(object):
    def __eq__(self, other):
        return repr(self) == repr(other)

    def __hash__(self):
        return hash(repr(self))

# "atoms"
class SortNode(_ASTNode):
    pass

class AtomicSortNode(SortNode):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return 'Sort<{}>'.format(self.name)

class CompoundSortNode(SortNode):
    def __init__(self, constructor, sorts):
        self.constructor = constructor
        self.sorts = sorts

    def __repr__(self):
        return 'Sort<{} {}>'.format(self.symbol, with_spaces(self.sorts))

class SettingNode(_ASTNode):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return 'Setting<{}>'.format(self.name)

class MetaDataNode(_ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return 'MetaData<{}>'.format(self.value)

class IdentifierNode(_ASTNode):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return 'Id<{}>'.format(self.name)

class SortedVarNode(_ASTNode):
    def __init__(self, var_name, var_sort):
        self.var_name = var_name
        self.var_sort = var_sort

    def __repr__(self):
        return 'Decl<{} {}>'.format(self.var_name, self.var_sort)

class ReAllCharNode(_ASTNode):
    def __repr__(self):
        return 'ReAllChar<.>'

class BracketsNode(_ASTNode):
    def __init__(self, body):
        self.body = body

    def __repr__(self):
        return '({})'.format(with_spaces(self.body))

# NOTE:
#      sort-wise, we're treating everything as a function; even literals
class _SortedASTNode(_ASTNode):
    _signature = NotImplemented
    _sort      = NotImplemented

    def __init__(self):
        assert isinstance(self._sort, SORT_TYPE)
        assert self._signature == UNCHECKED_SIGNATURE or isinstance(self._signature, SIGNATURE_TYPE)

    @classmethod
    def get_signature(cls):
        return cls._signature

    @classmethod
    def get_sort(cls):
        return cls._sort

    @classmethod
    def is_terminal(cls):
        return cls._signature == UNIT_SIGNATURE

    @classmethod
    def accepts(cls, sort):
        if cls._signature == UNCHECKED_SIGNATURE:
            return False
        return sort in cls._signature

    @classmethod
    def returns(cls, sort):
        return sort == cls._sort

# literals
class LiteralNode(_SortedASTNode):
    _signature = UNIT_SIGNATURE

    def __init__(self, value):
        super().__init__()
        self.value = value

    def __repr__(self):
        return '{}<{}>'.format(self.get_sort(), self.value)

class BoolLitNode(LiteralNode):
    _sort = BOOL_SORT

    def __init__(self, value):
        assert isinstance(value, bool)
        super().__init__(value)

class IntLitNode(LiteralNode):
    _sort = INT_SORT

    def __init__(self, value):
        assert isinstance(value, numbers.Real) and not isinstance(value, bool)
        super().__init__(value)

class StringLitNode(LiteralNode):
    _sort = STRING_SORT

    def __init__(self, value):
        assert isinstance(value, str)
        super().__init__(value)

    def __len__(self):
        return len(self.value)

# expressions
class ExpressionNode(_ASTNode):
    _symbol = NotImplemented

    def __init__(self, body):
        if isinstance(self._symbol, str):
            self._symbol = IdentifierNode(self._symbol)
        self.body = body

    @classmethod
    def get_symbol(cls):
        return cls._symbol

    @property
    def symbol(self):
        return self._symbol

    def __repr__(self):
        return '(\'{}\' {})'.format(self.symbol, with_spaces(self.body))

class _SortedExpressionNode(ExpressionNode, _SortedASTNode):
    def __init__(self, body):
        # TODO:
        #      enforce that the arguments are of correct types
        _SortedASTNode.__init__(self)
        ExpressionNode.__init__(self, body)

class _NullaryExpression(_SortedExpressionNode):
    def __init__(self):
        super().__init__([])

class _UnaryExpression(_SortedExpressionNode):
    def __init__(self, a):
        super().__init__([a])

class _BinaryExpression(_SortedExpressionNode):
    def __init__(self, a, b):
        super().__init__([a, b])

class _TernaryExpression(_SortedExpressionNode):
    def __init__(self, a, b, c):
        super().__init__([a, b, c])

class _QuaternaryExpression(_SortedExpressionNode):
    def __init__(self, a, b, c, d):
        super().__init__([a, b, c, d])

class _NaryExpression(_SortedExpressionNode):
    def __init__(self, *args):
        super().__init__(list(args))

class _RelationExpressionNode(_BinaryExpression):
    _signature = [INT_SORT, INT_SORT]
    _sort      = BOOL_SORT

class GenericExpressionNode(_NaryExpression):
    _signature = UNCHECKED_SIGNATURE
    _sort      = UNIT_SORT

    def __init__(self, symbol, *args):
        self._symbol = symbol
        super().__init__(*args)

# commands
class _CommandNode(_SortedASTNode):
    _sort = UNIT_SORT

class MetaCommandNode(_CommandNode, _NaryExpression):
    _signature = UNCHECKED_SIGNATURE

    def __init__(self, symbol, *args):
        self._symbol = symbol
        super().__init__(*args)

class AssertNode(_CommandNode, _UnaryExpression):
    _signature = [BOOL_SORT]
    _symbol    = 'assert'

class CheckSatNode(_CommandNode, _NullaryExpression):
    _signature = UNIT_SIGNATURE
    _symbol    = 'check-sat'

class GetModelNode(_CommandNode, _NullaryExpression):
    _signature = UNIT_SIGNATURE
    _symbol    = 'get-model'

class FunctionDeclarationNode(_CommandNode, _TernaryExpression):
    _signature = UNCHECKED_SIGNATURE
    _symbol    = 'declare-fun'

class FunctionDefinitionNode(_CommandNode, _QuaternaryExpression):
    _signature = UNCHECKED_SIGNATURE
    _symbol    = 'define-fun'

class ConstantDeclarationNode(_CommandNode, _BinaryExpression):
    _signature = UNCHECKED_SIGNATURE
    _symbol    = 'declare-const'

# boolean expressions
class AndNode(_BinaryExpression):
    _signature = [BOOL_SORT, BOOL_SORT]
    _sort      = BOOL_SORT
    _symbol    = 'and'

class OrNode(_BinaryExpression):
    _signature = [BOOL_SORT, BOOL_SORT]
    _sort      = BOOL_SORT
    _symbol    = 'or'

class NotNode(_UnaryExpression):
    _signature = [BOOL_SORT]
    _sort      = BOOL_SORT
    _symbol    = 'not'

# relations
class EqualNode(_RelationExpressionNode):
    _signature = [ANY_SORT, ANY_SORT]
    _symbol    = '='

class GtNode(_RelationExpressionNode):
    _symbol = '>'

class LtNode(_RelationExpressionNode):
    _symbol = '<'

class GteNode(_RelationExpressionNode):

    _symbol = '>='

class LteNode(_RelationExpressionNode):

    _symbol = '<='

# functions
class ConcatNode(_BinaryExpression):
    _signature = [STRING_SORT, STRING_SORT]
    _sort      = STRING_SORT
    _symbol    = 'Concat'

class ContainsNode(_BinaryExpression):
    _signature = [STRING_SORT, STRING_SORT]
    _sort      = BOOL_SORT
    _symbol    = 'Contains'

class AtNode(_BinaryExpression):
    _signature = [STRING_SORT, INT_SORT]
    _sort      = STRING_SORT
    _symbol    = 'At'

class LengthNode(_UnaryExpression):
    _signature = [STRING_SORT]
    _sort      = INT_SORT
    _symbol    = 'Length'

class IndexOfNode(_BinaryExpression):
    _signature = [STRING_SORT, STRING_SORT]
    _sort      = INT_SORT
    _symbol    = 'IndexOf'

class IndexOf2Node(_TernaryExpression):
    _signature = [STRING_SORT, STRING_SORT, INT_SORT]
    _sort      = INT_SORT
    _symbol    = 'IndexOf2'

class PrefixOfNode(_BinaryExpression):
    _signature = [STRING_SORT, STRING_SORT]
    _sort      = BOOL_SORT
    _symbol    = 'PrefixOf'

class SuffixOfNode(_BinaryExpression):
    _signature = [STRING_SORT, STRING_SORT]
    _sort      = BOOL_SORT
    _symbol    = 'SuffixOf'

class StringReplaceNode(_TernaryExpression):
    _signature = [STRING_SORT, STRING_SORT, STRING_SORT]
    _sort      = STRING_SORT
    _symbol    = 'Replace'

class SubstringNode(_TernaryExpression):
    _signature = [STRING_SORT, INT_SORT, INT_SORT]
    _sort      = STRING_SORT
    _symbol    = 'Substring'

class FromIntNode(_UnaryExpression):
    _signature = [INT_SORT]
    _sort      = STRING_SORT
    _symbol    = 'FromInt'

class ToIntNode(_UnaryExpression):
    _signature = [STRING_SORT]
    _sort      = INT_SORT
    _symbol    = 'ToInt'

class InReNode(_BinaryExpression):
    _signature = [STRING_SORT, REGEX_SORT]
    _sort      = BOOL_SORT
    _symbol    = 'InRegex'

class StrToReNode(_UnaryExpression):
    _signature = [STRING_SORT]
    _sort      = REGEX_SORT
    _symbol    = 'Str2Re'

class ReConcatNode(_BinaryExpression):
    _signature = [REGEX_SORT, REGEX_SORT]
    _sort      = REGEX_SORT
    _symbol    = 'ReConcat'

class ReStarNode(_UnaryExpression):
    _signature = [REGEX_SORT]
    _sort      = REGEX_SORT
    _symbol    = 'ReStar'

class RePlusNode(_UnaryExpression):
    _signature = [REGEX_SORT]
    _sort      = REGEX_SORT
    _symbol    = 'RePlus'

class ReRangeNode(_BinaryExpression):
    _signature = [STRING_SORT, STRING_SORT]
    _sort      = REGEX_SORT
    _symbol    = 'ReRange'

    def __init__(self, a, b):
        # TODO:
        #      assert that arguments are literals
        super().__init__(a, b)

class ReUnionNode(_BinaryExpression):
    _signature = [REGEX_SORT, REGEX_SORT]
    _sort      = REGEX_SORT
    _symbol    = 'ReUnion'

class ReInterNode(_BinaryExpression):
    _signature = [REGEX_SORT, REGEX_SORT]
    _sort      = REGEX_SORT
    _symbol    = 'ReInter'
