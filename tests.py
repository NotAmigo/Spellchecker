import unittest
import automata
import spellchecker
import tempfile
import json
import create_word_library


class MyTestCase(unittest.TestCase):
    def test_find_diff(self):
        str1 = 'тест1'
        str2 = 'тест2'
        self.assertEqual(spellchecker.find_diff(str1, str2), 4)

    def test_get_database(self):
        fp = tempfile.NamedTemporaryFile(mode='w+', suffix='.json')
        d = {'test': 1}
        json.dump(d, fp)
        fp.seek(0)
        self.assertIn('test', spellchecker.get_database(fp.name))

    def test_spellchecker(self):
        sp = spellchecker.Spellchecker('я съеl деда', 'package.json')
        sp.check_spell()
        self.assertIsNotNone(sp)

    def test_parse(self):
        ans = spellchecker.parse_args(['check', '-t', 'я', 'съеl', 'деда'])
        self.assertIsNotNone(ans)

    def test_spellchecker(self):
        sp = spellchecker.Spellchecker('seo', ['seof'])
        sp.check_spell()
        ans = str(sp)
        self.assertIn('seo', ans)

    def test_main(self):
        ans = spellchecker.main(['check', '-t', 'я', 'съеl', 'деда'])
        self.assertIsNone(ans)

    def test_special_rules(self):
        ans = spellchecker.main(['check', '-t', '1й'])
        self.assertIsNone(ans)

    def test_edit_rules(self):
        ans = spellchecker.main(['rules', '-t', '1й->жопа'])
        self.assertIsNone(ans)

    def test_edit_rules_path_to_file(self):
        ans = spellchecker.main(['rules', '-p', 'rules.txt'])
        self.assertIsNone(ans)

    def test_get_dict(self):
        fp = tempfile.NamedTemporaryFile(mode='w+', suffix='.json')
        d = {'test': 1}
        json.dump(d, fp)
        fp.seek(0)
        ans_dict = create_word_library.get_dict(fp.name)
        self.assertEqual(d, ans_dict)

    def test_get_words(self):
        fp = tempfile.NamedTemporaryFile(mode='+w', suffix='.txt')
        string = 'Я,...,!съел деда%('
        fp.write(string)
        fp.seek(0)
        ans = create_word_library.get_text(fp.name)
        self.assertEqual(ans, ['я', 'съел', 'деда'])

    def test_clear_json(self):
        fp = tempfile.NamedTemporaryFile(mode='+w', suffix='.json')
        d = {'test': 1}
        json.dump(d, fp)
        fp.seek(0)
        self.assertIsNotNone(fp.read())
        create_word_library.clean_json(fp.name)
        fp.seek(0)
        self.assertEqual(fp.read(), '{}')

    def test_rewrite_json(self):
        fp = tempfile.NamedTemporaryFile(mode='+w', suffix='.json')
        d = {'test': 1}
        json.dump(d, fp)
        fp.seek(0)
        self.assertIsNotNone(fp.read())
        create_word_library.rewrite_json(['test2'], fp.name)
        fp.seek(0)
        self.assertIn('test2', fp.read())

    def test_add_words_to_dict(self):
        fp = tempfile.NamedTemporaryFile(mode='+w', suffix='.json')
        d = {'test': 1}
        json.dump(d, fp)
        fp.seek(0)
        words = ['test2']
        ans = create_word_library.add_words_to_dict(words, fp.name)
        self.assertEqual({'test': 1, 'test2': 1}, ans)

    def test_automata(self):
        # It is test from automata.py written by author of the library
        words = [x.strip().lower() for x in
                 open('words_alpha.txt')]
        m = spellchecker.Matcher(words)
        self.assertEqual(len(list(automata.find_all_matches('food', 1, m))),
                         4)
        self.assertEqual(len(list(automata.find_all_matches('food', 2, m))),
                         15)


if __name__ == '__main__':
    unittest.main()
