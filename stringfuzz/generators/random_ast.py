import random
import inspect

from stringfuzz.ast import *
from stringfuzz.smt import smt_new_var, smt_reset_counters, smt_declare_var
from stringfuzz.util import random_string, coin_toss

__all__ = [
    'random_ast'
]

# constants
# nodes that have no inputs
TERMINALS = [
    ReAllCharNode,
]

# nodes that can take expressions
NONTERMINALS = [
    NotNode,
    GtNode,
    LtNode,
    GteNode,
    LteNode,
    ContainsNode,
    AtNode,
    LengthNode,
    # IndexOfNode,
    IndexOf2Node,
    PrefixOfNode,
    SuffixOfNode,
    StringReplaceNode,
    SubstringNode,
    InReNode,
    ReStarNode,
    RePlusNode,
    # FromIntNode,
    # ToIntNode,
]

# nodes that can take only terminals
ALMOST_TERMINALS = [
    StrToReNode,
    ReRangeNode,
]

N_ARY_NONTERMINALS = [
    ConcatNode,
    ReConcatNode,
    AndNode,
    OrNode,
    EqualNode,
    ReUnionNode,
    ReInterNode,
]

EXPRESSION_SORTS = DECLARABLE_SORTS + [REGEX_SORT]

# global config
_max_terms           = 0
_max_str_lit_length  = 0
_max_int_lit         = 0
_literal_probability = 0.0
_semantically_valid  = False

# helpers
def get_all_returning_a(sort, nodes):
    return list(filter(lambda node: node.returns(sort), nodes))

def get_terminals(nodes):
    return filter(lambda node: node.is_terminal(), nodes)

def make_random_literal(sort):
    if sort == STRING_SORT:
        return StringLitNode(random_string(_max_str_lit_length))

    if sort == INT_SORT:
        return IntLitNode(random.randint(0, _max_int_lit))

    if sort == BOOL_SORT:
        return BoolLitNode(coin_toss())

    raise ValueError('unknown sort {}'.format(sort))

def should_choose_literal():
    global _literal_probability
    return random.random() < _literal_probability

def make_random_terminal(variables, sort):
    
    if sort == REGEX_SORT:
        return ReAllCharNode()

    # randomly choose between a variable or a literal
    if should_choose_literal():
        return make_random_literal(sort)

    return random.choice(variables[sort])

def make_random_expression(variables, sort, depth):
    global _semantically_valid

    # if semantics are going to hell, then randomly reinvent the sort
    if _semantically_valid is False:
        sort = random.choice(EXPRESSION_SORTS)

    # at depth 0, make a terminal
    if depth < 1:
        return make_random_terminal(variables, sort)

    # randomly shrink the depth
    shrunken_depth = random.randint(0, depth - 1)

    # get random expression generator
    candidate_nodes = get_all_returning_a(sort, NONTERMINALS)
    expression_node = random.choice(candidate_nodes)
    signature       = expression_node.get_signature()
    num_args        = len(signature)

    # if the expression takes any sort, pick one
    if expression_node.accepts(ANY_SORT):
        collapsed_sort = random.choice(EXPRESSION_SORTS)
        signature      = [collapsed_sort for i in range(num_args)]

    # generate random arguments
    random_args = [make_random_expression(variables, arg_sort, shrunken_depth) for arg_sort in signature]

    # build expression
    expression = expression_node(*random_args)

    return expression

def generate_assert(variables, depth):
    expression = make_random_expression(variables, BOOL_SORT, depth)
    return AssertNode(expression)

def make_random_ast(num_vars, num_asserts, depth, max_terms, max_str_lit_length, max_int_lit, literal_probability, semantically_valid):
    global _max_terms
    global _max_str_lit_length
    global _max_int_lit
    global _literal_probability
    global _semantically_valid

    # set global config
    _max_terms           = max_terms
    _max_str_lit_length  = max_str_lit_length
    _max_int_lit         = max_int_lit
    _literal_probability = literal_probability
    _semantically_valid  = semantically_valid

    # create variables
    variables = {s: [smt_new_var() for i in range(num_vars)] for s in DECLARABLE_SORTS}

    # create declarations
    declarations = []
    for s in DECLARABLE_SORTS:
        new_declarations = [smt_declare_var(v, sort=s) for v in variables[s]]
        declarations.extend(new_declarations)

    # create asserts
    asserts = [generate_assert(variables, depth) for i in range(num_asserts)]

    # add check-sat
    expressions = asserts + [CheckSatNode()]

    return declarations + expressions

# public API
def random_ast(*args, **kwargs):
    smt_reset_counters()
    return make_random_ast(*args, **kwargs)
