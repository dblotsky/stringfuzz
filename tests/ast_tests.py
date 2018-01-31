import unittest

from stringfuzz.ast import *

class TestAST(unittest.TestCase):

    def test_no_ast_node(self):
        self.assertRaises(NameError, lambda: ASTNode)

    # literals
    def test_literal_bool(self):
        true = BoolLitNode(True)
        false = BoolLitNode(False)

        self.assertIs(true.value, True)
        self.assertIs(false.value, False)
        self.assertRaises(AssertionError, BoolLitNode, 1)
        self.assertRaises(AssertionError, BoolLitNode, 0)
        self.assertRaises(AssertionError, BoolLitNode, 'true')

    def test_literal_int(self):
        five = IntLitNode(5)

        self.assertEqual(five.value, 5)
        self.assertRaises(AssertionError, IntLitNode, True)
        self.assertRaises(AssertionError, IntLitNode, '5')

    def test_literal_string(self):
        hello = StringLitNode('hello')

        self.assertEqual(hello.value, 'hello')
        self.assertRaises(AssertionError, StringLitNode, True)
        self.assertRaises(AssertionError, StringLitNode, 5)

if __name__ == '__main__':
    unittest.main()
