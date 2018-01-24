'''
Eliminate all settings and get-model
'''

from stringfuzz.ast import SettingNode, ExpressionNode

__all__ = [
    'strip',
]

GET_MODEL = "get-model"
SET_INFO  = "set-info"
TO_STRIP  = [GET_MODEL, SET_INFO]

def need_not_strip(expr):
    if isinstance(expr, SettingNode):
        return False
    if isinstance(expr, ExpressionNode):
        if expr.symbol in TO_STRIP:
            return False 
    return True

# public API
def strip(ast):
    ast = [expr for expr in ast if need_not_strip(expr)]
    return ast
