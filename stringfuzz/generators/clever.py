import random
import copy

from stringfuzz.smt import *
from stringfuzz.ast import *
from stringfuzz.util import coin_toss, random_string
from stringfuzz.ast_walker import ASTWalker

__all__ = [
    'clever',
]

TREE_NONTERMINAL  = IfThenElseNode
EXPR_NONTERMINALS = [
    NotNode,
    GtNode,
    LtNode,
    GteNode,
    LteNode,
    ContainsNode,
    AtNode,
    LengthNode,
    IndexOf2Node,
    PrefixOfNode,
    SuffixOfNode,
    StringReplaceNode,
    SubstringNode, 
    ConcatNode,
    AndNode,
    OrNode,
    EqualNode
]

# global config
_max_str_lit_length  = 0
_max_int_lit         = 0
_literal_probability = 0.0

class LibInserter(ASTWalker):
    def __init__(self, ast, sort):
        super().__init__(ast)
        self.sort           = sort
        self.candidates     = {}

    def walk_expression(self, expression, parent, depth=0, pos_in_parent=-1):
        if expression.returns(self.sort) and pos_in_parent > -1:
            if not depth in self.candidates:
                self.candidates[depth] = []
            self.candidates[depth].append((parent, pos_in_parent))

        for i in sorted(range(len(expression.body)), key=lambda k: random.random()):
            sub_expression = expression.body[i]
            if isinstance(sub_expression, ExpressionNode):
                self.walk_expression(sub_expression, expression, depth+1, i)
    
    def insert_lib_calls(self, name, sig, variables, num_lib_calls):
        min_depth = -1
        for _ in range(num_lib_calls):
            depth = random.choice(list(self.candidates.keys()))
            c = random.choice(list(range(len(self.candidates[depth]))))
            parent, pos = self.candidates[depth][c]
            del self.candidates[depth][c]

            if self.candidates[depth] == []:
                del self.candidates[depth]

            if depth < min_depth or min_depth == -1:
                min_depth = depth

            parent.body[pos] = call_func(name, sig, variables)
        
        return min_depth


class LibRenamer(ASTWalker):
    def __init__(self, ast, old_name, new_name):
        super().__init__(ast)
        self.old_name = old_name
        self.new_name = new_name

    def enter_identifier(self, identifier, parent):
        if identifier.name == self.old_name:
            identifier.name = self.new_name

    def enter_expression(self, expression, parent):
        if expression._symbol.name == self.old_name:
            expression._symbol.name = self.new_name

def call_func(name, signature, variables):
    if isinstance(variables, dict):
        return GenericExpressionNode(name, *[random.choice(variables[s]) for s in signature])
    return GenericExpressionNode(name, *variables)

def get_all_returning_a(sort, nodes):
    return list(filter(lambda node: node.returns(sort), nodes))

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
    # randomly choose between a variable or a literal
    if should_choose_literal() or sort not in variables:
        return make_random_literal(sort)

    return random.choice(variables[sort])

def make_random_expression(variables, sort, depth):
    # at depth 0, make a terminal
    if depth < 1:
        return make_random_terminal(variables, sort)

    # randomly shrink the depth
    shrunken_depth = random.randint(0, depth - 1)

    # get random expression generator
    candidate_nodes = get_all_returning_a(sort, EXPR_NONTERMINALS)
    expression_node = random.choice(candidate_nodes)
    signature       = expression_node.get_signature()
    num_args        = len(signature)

    # if the expression takes any sort, pick one
    if expression_node.accepts(ANY_SORT):
        collapsed_sort = random.choice(DECLARABLE_SORTS)
        signature      = [collapsed_sort for i in range(num_args)]

    # generate random arguments
    random_args = [make_random_expression(variables, arg_sort, shrunken_depth) for arg_sort in signature]

    # build expression
    expression = expression_node(*random_args)

    return expression

def make_random_tree(variables, sort, tree_depth, expr_depth):
    # at depth 0, make a terminal
    if tree_depth < 1:
        return make_random_expression(variables, sort, expr_depth)

    # randomly shrink the depth
    shrunken_depth = random.randint(0, tree_depth - 1)

    # build expression
    signature   = [sort, sort]
    random_args = [make_random_tree(variables, arg_sort, shrunken_depth, expr_depth) for arg_sort in signature]
    random_args = [make_random_expression(variables, BOOL_SORT, expr_depth)] + random_args
    expression  = TREE_NONTERMINAL(*random_args)

    return expression

def make_clever(max_client_depth, num_client_vars, max_lib_depth, num_lib_vars, num_lib_calls, max_expr_depth, max_str_lit_length, max_int_lit, literal_probability, client_name="client", old_lib_name="old_lib", new_lib_name="new_lib"):

    # check args
    if max_client_depth < 1:
        raise ValueError('the maximum client depth must be at least 1')

    if max_expr_depth < 1:
        raise ValueError('the maximum expr depth must be at least 1')

    if num_lib_calls < 1:
        raise ValueError('the number of library calls must be at least 1')

    if max_lib_depth < 1:
        raise ValueError('the maximum library depth must be at least 1')

    global _max_str_lit_length
    global _max_int_lit
    global _literal_probability

    # set global config
    _max_str_lit_length  = max_str_lit_length
    _max_int_lit         = max_int_lit
    _literal_probability = literal_probability

    # create function definitions
    lib_sort    = random.choice(DECLARABLE_SORTS)
    lib_args    = [random.choice(DECLARABLE_SORTS) for s in range(num_lib_vars)]
    client_sort = random.choice(DECLARABLE_SORTS)
    client_args = [random.choice(DECLARABLE_SORTS) for s in range(num_client_vars)]

    # create variables
    variables = {s: [] for s in set(client_args)}
    decls = []
    for s in client_args:
        v = smt_new_var()
        variables[s].append(v)
        decls.append(smt_declare_var(v, sort=s))

    client_vars = {s: [] for s in set(client_args)}
    client_decls = []
    for s in client_args:
        v = smt_new_arg()
        client_vars[s].append(v)
        client_decls.append((v,s))
    # create variable declarations
    client_decls = smt_declare_args(client_decls)

    lib_vars = {s: [] for s in set(lib_args)}
    lib_decls = []
    for s in lib_args:
        v = smt_new_arg()
        lib_vars[s].append(v)
        lib_decls.append((v,s))
    # create variable declarations
    lib_decls = smt_declare_args(lib_decls)

    # Generate client and libs
    old_lib_body = make_random_tree(lib_vars, lib_sort, max_lib_depth, max_expr_depth)
    new_lib_body = make_random_tree(lib_vars, lib_sort, max_lib_depth, max_expr_depth)
    
    decls.append(smt_define_func(old_lib_name, lib_decls, lib_sort, old_lib_body))
    decls.append(smt_define_func(new_lib_name, lib_decls, lib_sort, new_lib_body))

    client_body = make_random_tree(client_vars, client_sort, max_client_depth, max_expr_depth)
    inserter = LibInserter([client_body], lib_sort)
    old_client_body = inserter.walk()[0]
    random_args = [make_random_expression(variables, arg_sort, max_expr_depth) for arg_sort in lib_args]
    lib_call_depth = inserter.insert_lib_calls(old_lib_name, lib_args, random_args, num_lib_calls)
    new_client_body = LibRenamer([copy.deepcopy(old_client_body)], old_lib_name, new_lib_name).walk()[0]

    decls.append(smt_define_func(client_name+"_old", client_decls, client_sort, old_client_body))
    decls.append(smt_define_func(client_name+"_new", client_decls, client_sort, new_client_body))

    print(";BEGIN STRINGFUZZ STATS")
    print("; max_client_depth", max_client_depth)
    print("; num_client_vars", num_client_vars)
    print("; max_lib_depth", max_lib_depth)
    print("; num_lib_vars", num_lib_vars)
    print("; num_lib_calls", num_lib_calls)
    print("; max_expr_depth", max_expr_depth)
    print("; lowest_lib_call_depth", lib_call_depth)
    print(";END STRINGFUZZ STATS")

    # assert that the client calling the old library is not equal to the client calling the new library
    asserts = [AssertNode(NotNode(EqualNode(call_func(client_name+"_old", client_args, variables), call_func(client_name+"_new", client_args, variables))))]

    # add check-sat
    expressions = asserts + [CheckSatNode()]

    return decls + expressions

# public API
def clever(*args, **kwargs):
    smt_reset_counters()
    return make_clever(*args, **kwargs)
