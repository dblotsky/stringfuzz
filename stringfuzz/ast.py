import string
import numbers

'''
The AST is a list of ASTNodes.
'''

__all__ = [
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
    'CommandNode',
    'MetaCommandNode',
    'AssertNode',
    'CheckSatNode',
    'GetModelNode',
    'AndNode',
    'OrNode',
    'NotNode',
    'RelationExpressionNode',
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

# constants
STRING_SORT = 'String'
INT_SORT    = 'Int'
BOOL_SORT   = 'Bool'
REGEX_SORT  = 'Regex'
UNIT_SORT   = 'Unit'
ANY_SORT    = '*'

UNIT_SIGNATURE      = []
UNCHECKED_SIGNATURE = [None]

ATOMIC_SORTS = [
    STRING_SORT,
    INT_SORT,
    BOOL_SORT,
    REGEX_SORT,
]

SORT_TYPE      = str
SIGNATURE_TYPE = list

# helpers
def with_spaces(terms):
    return ' '.join(map(repr, terms))

# data structures
class _ASTNode(object):
    pass

class _SortedASTNode(_ASTNode):

    # NOTE:
    #      treating everything as a function; even literals
    def __init__(self, signature, sort):
        assert isinstance(sort, SORT_TYPE)
        assert isinstance(signature, SIGNATURE_TYPE)
        self.signature = signature
        self.sort      = sort

# literals
class LiteralNode(_SortedASTNode):
    def __init__(self, value, sort):
        super().__init__(UNIT_SIGNATURE, sort)
        self.value = value

    def __repr__(self):
        return 'Literal<{}>'.format(self.value)

class BoolLitNode(LiteralNode):
    def __init__(self, value):
        assert isinstance(value, bool)
        super().__init__(value, BOOL_SORT)

    def __repr__(self):
        return 'BoolLit<{}>'.format(self.value)

class IntLitNode(LiteralNode):
    def __init__(self, value):
        assert isinstance(value, numbers.Real) and not isinstance(value, bool)
        super().__init__(value, INT_SORT)

    def __repr__(self):
        return 'IntLit<{}>'.format(self.value)

class StringLitNode(LiteralNode):
    def __init__(self, value):
        assert isinstance(value, str)
        super().__init__(value, STRING_SORT)

    def __len__(self):
        return len(self.value)

    def __repr__(self):
        return 'StringLit<{!r}>'.format(self.value)

# sorts
class SortNode(_ASTNode):
    pass

class AtomicSortNode(SortNode):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return 'Sort<{}>'.format(self.name)

class CompoundSortNode(SortNode):
    def __init__(self, symbol, sorts):
        self.symbol = symbol
        self.sorts = sorts

    def __repr__(self):
        return 'CSort<{} {}>'.format(self.symbol, with_spaces(self.sorts))

# commands
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

# other atoms
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

# expressions
class ExpressionNode(_ASTNode):
    def __init__(self, symbol, body):
        assert symbol is not None
        self.symbol = symbol
        self.body   = body

    def __repr__(self):
        contents = with_spaces([self.symbol] + self.body)
        return 'Expr<{}>'.format(contents)

class _SortedExpressionNode(ExpressionNode, _SortedASTNode):
    def __init__(self, symbol, body, signature, sort):
        # TODO:
        #      enforce that the arguments are of correct types
        # NOTE:
        #      use None to denote a signature that doesn't need to checked
        ExpressionNode.__init__(self, symbol, body)
        _SortedASTNode.__init__(self, signature, sort)

class _SpecificExpression(_SortedExpressionNode):
    def __repr__(self):
        contents = with_spaces(self.body)
        return '{}<{}>'.format(self.symbol, contents)

# commands
class CommandNode(_SortedExpressionNode):
    def __init__(self, symbol, body, signature):
        super().__init__(symbol, body, signature, UNIT_SORT)

class MetaCommandNode(CommandNode):
    def __init__(self, symbol, body):
        super().__init__(symbol, body, UNCHECKED_SIGNATURE)

class AssertNode(CommandNode):
    def __init__(self, expression):
        super().__init__('assert', [expression], [BOOL_SORT])

class CheckSatNode(CommandNode):
    def __init__(self):
        super().__init__('check-sat', [], UNIT_SIGNATURE)

class GetModelNode(CommandNode):
    def __init__(self):
        super().__init__('get-model', [], UNIT_SIGNATURE)

class FunctionDeclarationNode(CommandNode):
    def __init__(self, name, function_signature, return_sort):
        self.name               = name
        self.function_signature = function_signature
        self.return_sort        = return_sort
        super().__init__(
            'declare-fun',
            [name, function_signature, return_sort],
            UNCHECKED_SIGNATURE
        )

    def __repr__(self):
        return 'FunDecl<{}: ({}) -> {}>'.format(
            self.name,
            with_spaces(self.function_signature.body),
            self.return_sort
        )

class FunctionDefinitionNode(CommandNode):
    def __init__(self, name, function_signature, return_sort, definition):
        self.name               = name
        self.function_signature = function_signature
        self.return_sort        = return_sort
        self.definition         = definition
        super().__init__(
            'define-fun',
            [name, function_signature, return_sort, definition],
            UNCHECKED_SIGNATURE
        )

    def __repr__(self):
        return 'FunDef<{}: ({}) -> {} | {}>'.format(
            self.name,
            with_spaces(self.function_signature.body),
            self.return_sort,
            self.definition
        )

class ConstantDeclarationNode(CommandNode):
    def __init__(self, name, return_sort):
        self.name        = name
        self.return_sort = return_sort
        super().__init__('declare-const', [name, return_sort], UNIT_SIGNATURE)

# specific expressions
class AndNode(_SortedExpressionNode):
    def __init__(self, a, b):
        super().__init__('and', [a, b], [BOOL_SORT, BOOL_SORT], BOOL_SORT)

class OrNode(_SortedExpressionNode):
    def __init__(self, a, b):
        super().__init__('or', [a, b], [BOOL_SORT, BOOL_SORT], BOOL_SORT)

class NotNode(_SortedExpressionNode):
    def __init__(self, a):
        super().__init__('not', [a], [BOOL_SORT], BOOL_SORT)

class RelationExpressionNode(_SortedExpressionNode):
    def __init__(self, symbol, a, b):
        super().__init__(symbol, [a, b], [ANY_SORT, ANY_SORT], BOOL_SORT)

class ConcatNode(_SpecificExpression):
    def __init__(self, a, b):
        super().__init__('Concat', [a, b], [STRING_SORT, STRING_SORT], STRING_SORT)

class ContainsNode(_SpecificExpression):
    def __init__(self, a, b):
        super().__init__('Contains', [a, b], [STRING_SORT, STRING_SORT], BOOL_SORT)

class AtNode(_SpecificExpression):
    def __init__(self, a, b):
        super().__init__('At', [a, b], [STRING_SORT, INT_SORT], STRING_SORT)

class LengthNode(_SpecificExpression):
    def __init__(self, a):
        super().__init__('Length', [a], [STRING_SORT], INT_SORT)

class IndexOfNode(_SpecificExpression):
    def __init__(self, haystack, needle):
        super().__init__('IndexOf', [haystack, needle], [STRING_SORT, STRING_SORT], INT_SORT)

class IndexOf2Node(_SpecificExpression):
    def __init__(self, haystack, needle, start):
        super().__init__('IndexOf2', [haystack, needle, start], [STRING_SORT, STRING_SORT, INT_SORT], INT_SORT)

class PrefixOfNode(_SpecificExpression):
    def __init__(self, a, b):
        super().__init__('PrefixOf', [a, b], [STRING_SORT, STRING_SORT], BOOL_SORT)

class SuffixOfNode(_SpecificExpression):
    def __init__(self, a, b):
        super().__init__('SuffixOf', [a, b], [STRING_SORT, STRING_SORT], BOOL_SORT)

class StringReplaceNode(_SpecificExpression):
    def __init__(self, a, b, c):
        super().__init__('Replace', [a, b, c], [STRING_SORT, STRING_SORT, STRING_SORT], STRING_SORT)

class SubstringNode(_SpecificExpression):
    def __init__(self, a, b, c):
        super().__init__('Substring', [a, b, c], [STRING_SORT, INT_SORT, INT_SORT], STRING_SORT)

class FromIntNode(_SpecificExpression):
    def __init__(self, a):
        super().__init__('FromInt', [a], [INT_SORT], STRING_SORT)

class ToIntNode(_SpecificExpression):
    def __init__(self, a):
        super().__init__('ToInt', [a], [STRING_SORT], INT_SORT)

class InReNode(_SpecificExpression):
    def __init__(self, a, b):
        super().__init__('InRegex', [a, b], [STRING_SORT, REGEX_SORT], BOOL_SORT)

class StrToReNode(_SpecificExpression):
    def __init__(self, a):
        super().__init__('Str2Re', [a], [STRING_SORT], REGEX_SORT)

class ReConcatNode(_SpecificExpression):
    def __init__(self, a, b):
        super().__init__('ReConcat', [a, b], [REGEX_SORT, REGEX_SORT], REGEX_SORT)

class ReStarNode(_SpecificExpression):
    def __init__(self, a):
        super().__init__('ReStar', [a], [REGEX_SORT], REGEX_SORT)

class RePlusNode(_SpecificExpression):
    def __init__(self, a):
        super().__init__('RePlus', [a], [REGEX_SORT], REGEX_SORT)

class ReRangeNode(_SpecificExpression):
    def __init__(self, a, b):
        # TODO:
        #      assert that arguments are literals
        super().__init__('ReRange', [a, b], [STRING_SORT, STRING_SORT], REGEX_SORT)

class ReUnionNode(_SpecificExpression):
    def __init__(self, a, b):
        super().__init__('ReUnion', [a, b], [REGEX_SORT, REGEX_SORT], REGEX_SORT)

