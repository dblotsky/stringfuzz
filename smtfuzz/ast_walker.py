from smtfuzz.ast import *

__all__ = [
    'ASTWalker'
]

class ASTWalker(object):

    def __init__(self, ast):
        super(ASTWalker, self).__init__()
        self.__ast = ast

    # public API
    def walk(self):
        for expression in self.__ast:
            self.walk_expression(expression)

        return self

    # walks
    def walk_expression(self, expression):

        self.enter_expression(expression)

        for sub_expression in expression.body:
            if isinstance(sub_expression, ExpressionNode):
                self.walk_expression(sub_expression)

            if isinstance(sub_expression, IdentifierNode):
                self.walk_identifier(sub_expression)

            if isinstance(sub_expression, LiteralNode):
                self.walk_literal(sub_expression)

        self.exit_expression(expression)

    def walk_literal(self, literal):
        self.enter_literal(literal)
        self.exit_literal(literal)

    def walk_identifier(self, identifier):
        self.enter_identifier(identifier)
        self.exit_identifier(identifier)

    # enters/exits
    def enter_expression(self, expression):
        pass

    def exit_expression(self, expression):
        pass

    def enter_literal(self, literal):
        pass

    def exit_literal(self, literal):
        pass

    def enter_identifier(self, identifier):
        pass

    def exit_identifier(self, identifier):
        pass

