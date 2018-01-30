from stringfuzz.ast import *

__all__ = [
    'ASTWalker'
]

class ASTWalker(object):

    def __init__(self, ast):
        super().__init__()
        self.__ast = ast

    # public API
    def walk(self):
        for expression in self.__ast:
            self.walk_expression(expression, None)

        return self.__ast

    # walks
    def walk_expression(self, expression, parent):

        self.enter_expression(expression, parent)

        for sub_expression in expression.body:
            if isinstance(sub_expression, ExpressionNode):
                self.walk_expression(sub_expression, expression)

            if isinstance(sub_expression, IdentifierNode):
                self.walk_identifier(sub_expression, expression)

            if isinstance(sub_expression, LiteralNode):
                self.walk_literal(sub_expression, expression)

        self.exit_expression(expression, parent)

    def walk_literal(self, literal, parent):
        self.enter_literal(literal, parent)
        self.exit_literal(literal, parent)

    def walk_identifier(self, identifier, parent):
        self.enter_identifier(identifier, parent)
        self.exit_identifier(identifier, parent)

    # enters/exits
    def enter_expression(self, expression, parent):
        pass

    def exit_expression(self, expression, parent):
        pass

    def enter_literal(self, literal, parent):
        pass

    def exit_literal(self, literal, parent):
        pass

    def enter_identifier(self, identifier, parent):
        pass

    def exit_identifier(self, identifier, parent):
        pass

