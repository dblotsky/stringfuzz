'''
Combining two problems
'''

from stringfuzz.ast import ExpressionNode, SortNode
from stringfuzz.ast_walker import ASTWalker
from stringfuzz.smt import smt_string_logic, smt_sat

DECLARATIONS = ["declare-fun", "declare-const"]

__all__ = [
    'merge',
]

class RenameIDWalker(ASTWalker):
    def __init__(self, ast, suffix):
        super(RenameIDWalker, self).__init__(ast)
        self.suffix = suffix

    def exit_identifier(self, identifier, parent):
        identifier.name += self.suffix

def assertion(expr):
    return isinstance(expr, ExpressionNode) and expr.symbol == "assert"

def declaration(expr):
    return isinstance(expr, ExpressionNode) and expr.symbol in DECLARATIONS

def sort(expr):
    return isinstance(expr, SortNode)

# public API
def merge(first_ast, second_ast, rename_ids):
    if rename_ids:
        first_ast  = RenameIDWalker(first_ast, "1").walk()
        second_ast = RenameIDWalker(second_ast, "2").walk()

    combined     = set(first_ast + second_ast)
    declarations = list(filter(declaration, combined))
    sorts        = list(filter(sort, combined))
    assertions   = list(filter(assertion, combined))
    transformed  = [smt_string_logic()] + declarations + sorts + assertions + [smt_sat()]
    return transformed
