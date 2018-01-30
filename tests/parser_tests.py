import unittest

from stringfuzz.scanner import SMT_20, SMT_20_STRING, SMT_25_STRING
from stringfuzz.parser import parse, parse_file

class TestParser(unittest.TestCase):

    def test_no_file(self):
        self.assertRaises(IOError, parse_file, '', SMT_20)

    def test_empty(self):
        self.assertListEqual([], parse('', SMT_20))

    def test_bad_language(self):
        self.assertRaises(ValueError, parse, '', '')

    def test_good_languages(self):
        self.assertListEqual([], parse('', SMT_20))
        self.assertListEqual([], parse('', SMT_20_STRING))
        self.assertListEqual([], parse('', SMT_25_STRING))

    def test_trivial(self):
        expressions = parse('(check-sat)', SMT_20)
        self.assertEqual(len(expressions), 1)
        self.assertEqual(expressions[0].symbol.name, 'check-sat')
        self.assertTupleEqual(expressions[0].body, ())

    def test_simple_smt_20(self):
        expressions = parse('''
            (declare-fun X () String)
            (assert (= X "solution"))
            (check-sat)
        ''', SMT_20_STRING)

        self.assertEqual(len(expressions), 3)

        self.assertEqual(expressions[0].symbol.name, 'declare-fun')
        self.assertEqual(expressions[0].body[0].name, 'X')
        self.assertEqual(expressions[0].body[2].name, 'String')

        self.assertEqual(expressions[1].symbol.name, 'assert')
        self.assertEqual(expressions[1].body[0].symbol.name, '=')
        self.assertEqual(expressions[1].body[0].body[0].name, 'X')
        self.assertEqual(expressions[1].body[0].body[1].value, 'solution')

        self.assertEqual(expressions[2].symbol.name, 'check-sat')

    def test_simple_smt_25(self):
        expressions = parse('''
            (declare-fun X () String)
            (assert (= X "solution"))
            (check-sat)
        ''', SMT_25_STRING)

        self.assertEqual(len(expressions), 3)

        self.assertEqual(expressions[0].symbol.name, 'declare-fun')
        self.assertEqual(expressions[0].body[0].name, 'X')
        self.assertEqual(expressions[0].body[2].name, 'String')

        self.assertEqual(expressions[1].symbol.name, 'assert')
        self.assertEqual(expressions[1].body[0].symbol.name, '=')
        self.assertEqual(expressions[1].body[0].body[0].name, 'X')
        self.assertEqual(expressions[1].body[0].body[1].value, 'solution')

        self.assertEqual(expressions[2].symbol.name, 'check-sat')

if __name__ == '__main__':
    unittest.main()
