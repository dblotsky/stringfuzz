import unittest

from stringfuzz.constants import SMT_20, SMT_20_STRING, SMT_25_STRING
from stringfuzz.scanner import scan, scan_file

class TestScanner(unittest.TestCase):

    def test_constants(self):
        self.assertEqual(SMT_20, 'smt2')
        self.assertEqual(SMT_20_STRING, 'smt20')
        self.assertEqual(SMT_25_STRING, 'smt25')

    def test_no_file(self):
        self.assertRaises(IOError, scan_file, '', SMT_20)

    def test_empty(self):
        self.assertListEqual([], scan('', SMT_20))

    def test_bad_language(self):
        self.assertRaises(ValueError, scan, '', '')

    def test_good_languages(self):
        self.assertListEqual([], scan('', SMT_20))
        self.assertListEqual([], scan('', SMT_20_STRING))
        self.assertListEqual([], scan('', SMT_25_STRING))

    def test_simple(self):
        tokens = scan('(check-sat)', SMT_20)
        self.assertEqual(len(tokens), 3)
        self.assertEqual(tokens[0].name, 'LPAREN')
        self.assertEqual(tokens[0].value, '(')
        self.assertEqual(tokens[1].name, 'SYMBOL')
        self.assertEqual(tokens[1].value, 'check-sat')
        self.assertEqual(tokens[2].name, 'RPAREN')
        self.assertEqual(tokens[2].value, ')')

if __name__ == '__main__':
    unittest.main()
