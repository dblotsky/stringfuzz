from stringfuzz.generator import generate
from stringfuzz.smt import smt_model

__all__ = [
    'call_generate',
]

def call_generate(ast, language, produce_models):
    if produce_models is True:
        ast.append(smt_model())
    return generate(ast, language)
