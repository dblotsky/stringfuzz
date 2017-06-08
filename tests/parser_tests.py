import unittest

from smtfuzz.scanner import SMT_20, SMT_20_STRING, SMT_25_STRING
from smtfuzz.parser import parse, parse_file

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

    def test_simple(self):
        expressions = parse('(check-sat)', SMT_20)
        self.assertEqual(len(expressions), 1)
        self.assertEqual(expressions[0].name, 'check-sat')
        self.assertListEqual(expressions[0].body, [])

if __name__ == '__main__':
    unittest.main()
