import itertools
import re

from stringfuzz.ast import ExpressionNode, SortNode, IdentifierNode, FunctionDeclarationNode, SortedVarNode, CheckSatNode
from stringfuzz.ast_walker import ASTWalker
from stringfuzz.util import split_ast

__all__ = [
    'DISJOINT_RENAME',
    'INTERSECTING_RENAME',
    'NO_RENAME',
    'simple'
]

# constants
DISJOINT_RENAME     = 'disjoint'
INTERSECTING_RENAME = 'intersecting'
NO_RENAME           = 'none'

# helpers
def merge_asts(asts):

    # resulting parts
    all_heads        = []
    all_declarations = []
    all_asserts      = []
    all_tails        = []

    # accumulate each AST's parts
    for ast in asts:
        head, declarations, asserts, tail = split_ast(ast)

        all_heads        += head
        all_declarations += declarations
        all_asserts      += asserts
        all_tails        += tail

    # de-dupe each set
    all_heads        = list(set(all_heads))
    all_declarations = list(set(all_declarations))
    all_asserts      = list(set(all_asserts))
    all_tails        = list(set(all_tails))

    # sort the declarations
    by_name          = sorted(all_declarations, key=lambda x: x.body[0].name)
    by_name_and_sort = sorted(by_name, key=lambda x: x.body[2].name)

    # return resulting AST
    return all_heads + by_name_and_sort + all_asserts + all_tails

def increment_name(name, suffix):

    # check if the name has a numeric suffix
    match = re.match(r'(^.*?)(\d+)$', name)
    if match is not None:

        # if it does, increment the suffix
        prefix, numeric_suffix = match.groups()
        next_number = int(numeric_suffix) + 1
        next_suffix = str(next_number)
        return prefix + next_suffix

    # otherwise, just add the suffix
    return name + '_{}'.format(suffix)

def find_fresh_name(old_name, taboo, suffix):

    # if the name doesn't collide, we're good
    if old_name not in taboo:
        return old_name

    # start with the old name
    new_name = old_name

    # keep incrementing the old name until we hit a non-colliding one
    while new_name in taboo:
        new_name = increment_name(new_name, suffix)

    return new_name

class RenameIDWalker(ASTWalker):
    def __init__(self, ast, suffix, taboo):
        super().__init__(ast)

        self.suffix   = suffix
        self.taboo    = set(taboo)
        self.name_map = {}

    def exit_identifier(self, identifier, parent):
        old_name = identifier.name

        # if it's already mapped, use the mapping
        if old_name in self.name_map:
            new_name = self.name_map[old_name]

        # not mapped, but also not colliding
        elif old_name not in self.taboo:
            new_name = old_name
            self.name_map[old_name] = old_name
            self.taboo.add(new_name)

        # otherwise, figure out new name
        else:
            new_name = find_fresh_name(identifier.name, self.taboo, self.suffix)
            self.name_map[old_name] = new_name
            self.taboo.add(new_name)

        # update the name
        identifier.name = new_name

def simple(asts, rename_type):
    if rename_type != NO_RENAME:

        # keep track of all variable names
        all_names = set()

        for i in range(len(asts)):

            # create a walker and walk the tree
            walker  = RenameIDWalker(asts[i], suffix=i, taboo=all_names)
            asts[i] = walker.walk()

            # add all resulting names to set of all names
            ast_names = walker.name_map.values()
            all_names = all_names.union(ast_names)

    return merge_asts(asts)
