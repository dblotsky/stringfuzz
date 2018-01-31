from stringfuzz.types import ALL_INT_ARGS, ALL_RX_ARGS, ALL_STR_ARGS
from stringfuzz.ast_walker import ASTWalker

__all__ = [
    'rotate',
]

class RotateTransformer(ASTWalker):
    def __init__(self, ast):
        super().__init__(ast)

    def exit_expression(self, expr, parent):
        for uniform in [ALL_INT_ARGS, ALL_RX_ARGS, ALL_STR_ARGS]:
            # need at least two top level children
            uniform_expr = [isinstance(expr, C) for C in uniform]
            if any(uniform_expr) and len(expr.body) > 1:
                for i in range(len(expr.body)):
                    uniform_child = [isinstance(expr.body[i], C) for C in uniform]
                    if any(uniform_child):
                        # rotate clockwise
                        # j is the other top level child
                        if i == len(expr.body)-1:
                            j = 0
                        else:
                            j = len(expr.body)-1
                        temp = expr.body[j]
                        expr.body[j] = expr.body[i].body[0]
                        new_body = expr.body[i].body[1:] + [temp]
                        expr.body[i].body = new_body

# public API
def rotate(ast):
    transformed = RotateTransformer(ast).walk()
    return transformed
