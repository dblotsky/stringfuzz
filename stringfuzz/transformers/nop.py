from stringfuzz.parser import parse

__all__ = [
    'nop',
]

# public API
def nop(s, language):
    expressions = parse(s, language)
    return expressions