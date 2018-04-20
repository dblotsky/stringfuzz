import itertools

from stringfuzz.ast import ExpressionNode, SortNode, IdentifierNode, FunctionDeclarationNode, SortedVarNode
from stringfuzz.ast_walker import ASTWalker

__all__ = [
    'simple'
]

def alternate_merge(asts, merged):
    for ast in asts:
        if ast:
            node = ast.pop(0)
            if not node in merged:
                merged.append(node)
    if any(asts):
        merged = alternate_merge(asts, merged)
    return merged

class RenameIDWalker(ASTWalker):
    def __init__(self, ast, suffix):
        super(RenameIDWalker, self).__init__(ast)
        self.suffix = suffix

    def exit_identifier(self, identifier, parent):
        identifier.name += "_{}".format(self.suffix)

def simple(asts, rename_ids):
    if rename_ids:
        for i in range(len(asts)):
            asts[i] = RenameIDWalker(asts[i], i).walk()
    merged = alternate_merge(asts, [])
    return merged
