import random
import copy

from stringfuzz.smt import *
from stringfuzz.ast import *
from stringfuzz.util import coin_toss
from stringfuzz.ast_walker import ASTWalker

__all__ = [
    'clever',
]

CURR_LIB_CALLS   = 0
TARGET_LIB_CALLS = 0

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

def generate_clients(client_name, client_sig, client_sort, lib_sig, old_lib_name, new_lib_name, max_client_depth, clever_depth):
    # create variables
    global CURR_LIB_CALLS
    while CURR_LIB_CALLS != TARGET_LIB_CALLS:
        CURR_LIB_CALLS = 0
        variables = {s: [] for s in set(client_sig)}
        decls = []
        for s in client_sig:
            v = smt_new_arg()
            variables[s].append(v)
            decls.append((v,s))
        # create variable declarations
        arg_declaration = smt_declare_args(decls)

        old_body = make_random_expression(max_client_depth, variables, clever_depth, [old_lib_name]+lib_sig)
        
        old_client = smt_define_func(client_name+"_old", arg_declaration, client_sort, old_body)
        new_client = smt_define_func(client_name+"_new", arg_declaration, client_sort, LibRenamer([copy.deepcopy(old_body)], old_lib_name, new_lib_name).walk()[0])

    return [old_client, new_client]

def generate_lib(name, signature, sort, depth):
    # create variables
    variables = {s: [] for s in set(signature)}
    decls = []
    for s in signature:
        v = smt_new_arg()
        variables[s].append(v)
        decls.append((v,s))
    # create variable declarations
    arg_declaration = smt_declare_args(decls)

    body = make_random_expression(depth, variables)
    return smt_define_func(name, arg_declaration, sort, body)

def make_random_expression(depth, variables, clever_depth=None, func=None):
    global CURR_LIB_CALLS
    # at depth 0, make a terminal
    if depth < 1:
        if coin_toss():
            return random.choice(variables[BOOL_SORT])
        return BoolLitNode(coin_toss())

    # randomly shrink the depth
    shrunken_depth  = depth - 1 if coin_toss() else random.randint(0, depth - 1)

    # get random expression generator
    if clever_depth and func and CURR_LIB_CALLS < TARGET_LIB_CALLS and coin_toss() and depth == clever_depth:
        signature       = func[1:]
        expression_node = lambda *x: call_func(func[0], signature, x)
        CURR_LIB_CALLS += 1
    else:
        candidate_nodes = [AndNode, OrNode, NotNode, IfThenElseNode]
        expression_node = random.choice(candidate_nodes)
        signature       = expression_node.get_signature()
    
    num_args    = len(signature)
    # Make everything bool
    signature   = [BOOL_SORT for i in range(num_args)]
    # generate random arguments
    random_args = [make_random_expression(shrunken_depth, variables, clever_depth, func) for arg_sort in signature]
    # build expression
    expression  = expression_node(*random_args)

    return expression

def make_clever(max_client_depth, num_client_vars, max_lib_depth, num_lib_vars, clever_depth, num_lib_calls, client_name="client", old_lib_name="old_lib", new_lib_name="new_lib"):

    # check args
    if max_client_depth < 1:
        raise ValueError('the maximum depth must be at least 1')

    if num_lib_calls < 1:
        raise ValueError('the number of library calls must be at least 1')

    if max_lib_depth < 1:
        raise ValueError('the maximum depth must be at least 1')

    if num_lib_vars > num_client_vars:
        raise ValueError('the library must have fewer aruments than the client')

    global TARGET_LIB_CALLS
    TARGET_LIB_CALLS = num_lib_calls

    print(";BEGIN STRINGFUZZ STATS")
    print("; max_client_depth", max_client_depth)
    print("; num_client_vars", num_client_vars)
    print("; max_lib_depth", max_lib_depth)
    print("; num_lib_vars", num_lib_vars)
    print("; lib_call_depth", clever_depth)
    print("; num_lib_calls", num_lib_calls)
    print(";END STRINGFUZZ STATS")

    # create variables
    variables = {s: [smt_new_var() for i in range(num_client_vars)] for s in [BOOL_SORT]}

    # create variable declarations
    variable_declarations = []
    for s in [BOOL_SORT]:
        new_variable_declarations = [smt_declare_var(v, sort=s) for v in variables[s]]
        variable_declarations.extend(new_variable_declarations)

    # create function definitions
    lib_sig       = [BOOL_SORT for s in range(num_lib_vars)]
    lib_sort      = BOOL_SORT
    client_sort   = BOOL_SORT
    client_sig    = [BOOL_SORT for s in range(num_client_vars)]
    old_lib       = generate_lib(old_lib_name, lib_sig, lib_sort, max_lib_depth)
    new_lib       = generate_lib(new_lib_name, lib_sig, lib_sort, max_lib_depth)
    clients       = generate_clients(client_name, client_sig, client_sort, lib_sig, old_lib_name, new_lib_name, max_client_depth, clever_depth)
    variable_declarations += [old_lib, new_lib] + clients

    # assert that the client calling the old library is not equal to the client calling the new library
    asserts = [AssertNode(NotNode(EqualNode(call_func(client_name+"_old", client_sig, variables[BOOL_SORT]), call_func(client_name+"_new", client_sig, variables[BOOL_SORT]))))]

    # add check-sat
    expressions = asserts + [CheckSatNode()]

    return variable_declarations + expressions

# public API
def clever(*args, **kwargs):
    smt_reset_counters()
    return make_clever(*args, **kwargs)
