import re

from collections import namedtuple
from stringfuzz.ast_walker import ASTWalker

__all__ = [
    'analyse',
]

ZERO_DEPTH = 1

# NOTE:
#      depth   - depth in tree
#      nesting - nesting of the same expression in tree
Point = namedtuple('Point', ('expression', 'parent', 'depth', 'nesting'))

class StatsWalker(ASTWalker):

    def __init__(self, ast):
        super(StatsWalker, self).__init__(ast)

        # bookkeeping
        self.expr_stack    = []
        self.point_stack   = []
        self.nesting_stack = []

        self.depth = ZERO_DEPTH

        # results
        self.points    = []
        self.variables = set()
        self.literals  = []

    def make_point(self, expression):
        return Point(
            expression = expression,
            parent     = self.parent,
            depth      = self.depth,
            nesting    = self.nesting,
        )

    @property
    def expression(self):
        assert len(self.expr_stack) > 0
        return self.expr_stack[-1]

    @property
    def point(self):
        assert len(self.point_stack) > 0
        return self.point_stack[-1]

    @property
    def parent(self):
        if len(self.expr_stack) > 1:
            return self.expr_stack[-2]
        return None

    @property
    def nesting(self):
        assert len(self.nesting_stack) > 0
        return self.nesting_stack[-1]

    def enter_expression(self, expression):

        # push nesting if we're at least one expression deep
        if self.depth > 1:

            if self.expression.symbol == expression.symbol:
                new_nesting = self.nesting + 1
            else:
                new_nesting = ZERO_DEPTH

            self.nesting_stack.append(new_nesting)

        # otherwise, start off with no nesting
        else:
            self.nesting_stack.append(ZERO_DEPTH)

        # create a new point
        point = self.make_point(expression)
        self.points.append(point)

        # push point and expression
        self.point_stack.append(point)
        self.expr_stack.append(expression)

        # increase depth
        self.depth += 1

    def exit_expression(self, expression):

        # decrease depth
        self.depth -= 1

        # pop all stacks
        self.point_stack.pop()
        self.expr_stack.pop()
        self.nesting_stack.pop()

    def enter_literal(self, literal):
        assert self.point is not None
        self.literals.append(literal)

    def enter_identifier(self, variable):
        assert self.point is not None
        self.variables.add(variable.name)

def analyse(ast):
    walker = StatsWalker(ast)
    walker.walk()
    return walker.points, walker.variables, walker.literals
