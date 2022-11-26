#!/usr/bin/python
import argparse
from colorama import Fore
import sys
import string
import json
import automata
import bisect
from create_word_library import rewrite_json, clean_json, get_text
import difflib
from rules import get_dict, clean_rules_json, rewrite_rules_json

MAIN_JSON_PATH: str = 'package.json'
RULES_JSON_PATH: str = 'rules.json'


def check_special_rules(word: str):
    dictionary = get_dict(RULES_JSON_PATH)
    return dictionary[word] if word in dictionary else None


def find_diff(original: str, actual: str) -> str:
    d = difflib.Differ()
    diff_index = -1
    for i, step in enumerate(d.compare(original, actual)):
        if step[0] in '-+':
            diff_index = i
            break

    return diff_index


class Matcher:
    def __init__(self, db):
        self.db = db

    def __call__(self, w):
        pos = bisect.bisect_left(self.db, w)
        if pos < len(self.db):
            return self.db[pos]
        else:
            return None


class Spellchecker:
    def __init__(self, text, db):
        self.words_array = text \
            .translate(str.maketrans('', '', string.punctuation)) \
            .lower() \
            .split()
        self.answer = ''
        self.db = db

    def check_spell(self):
        for word in self.words_array:
            spell = Spell(word, self.db)
            spell.get_similar_words_list()
            self.answer += str(spell)

    def __str__(self): return self.answer

    def __call__(self): return self.answer


class Spell:
    def __init__(self, word, db):
        self.matcher = Matcher(db)
        self.word = word
        self.answer_array = []

    def __str__(self):
        if self.answer_array:
            self.edit_answer()
            res = f"Ошибка в слове \"{self.word}\", " \
                  f"возможно вы имели в виду:\n"
            res += ', '.join(self.answer_array)
            res += '\n'
        else:
            res = ''
        return res

    def edit_answer(self):
        ans_arr = []
        for word in self.answer_array:
            diff = find_diff(self.word, word)
            if ' ' in word:
                word = word.replace(' ', '_')
            if len(word) == diff:
                ans_arr.append(word + Fore.RED + '_' + Fore.RESET)
            elif len(word) < diff:
                ans_arr.append(word[:-1] + Fore.RED + word[-1] + Fore.RESET)
            else:
                ans_arr.append(word[:diff] +
                               Fore.RED + word[diff] + Fore.RESET + word[
                                                                    diff + 1:])
        self.answer_array = ans_arr

    def check_word(self, word, distance):
        a = automata.find_all_matches(word, distance, self.matcher)
        b = list(a)
        return list(automata.find_all_matches(word, distance, self.matcher))

    def get_similar_words_list(self):
        if self.check_word(self.word, 0):
            return
        for i in range(1, len(self.word)):
            word = self.word[:i]
            word_find = self.check_word(word, 0)
            if word_find:
                next_word = self.word[i:]
                next_word_find = self.check_word(next_word, 0)
                if next_word_find:
                    self.answer_array += [word_find[0] + ' ' +
                                          next_word_find[0]]
        self.answer_array += self.check_word(self.word, 1)
        special_rules_words = check_special_rules(self.word)
        if special_rules_words:
            self.answer_array += special_rules_words


def get_database(db):
    with open(db, 'r', encoding="utf-8") as f:
        words_database = sorted(list(json.load(f).keys()))
    return words_database


def check_spell(arguments):
    text = ''
    if arguments.text:
        text = ' '.join(arguments.text)
    if arguments.path:
        with open(arguments.path, 'r', encoding="utf-8") as f:
            text = f.read()
    if arguments.db:
        db_path = arguments
    else:
        db_path = MAIN_JSON_PATH
    db = get_database(db_path)
    spellchecker = Spellchecker(text, db)
    spellchecker.check_spell()
    print(spellchecker)


def edit_db(arguments):
    words = ''
    if arguments.add_path:
        words = get_text(arguments.add_path)
    if arguments.add_text:
        words = ' '.join(arguments.add_text)
    rewrite_json(words, MAIN_JSON_PATH)
    if arguments.clear:
        print('\033[91m' + "ARE YOU SURE?" + '\033[0m' + "y/n")
        sign = input()
        if sign.lower() == 'y':
            clean_json(MAIN_JSON_PATH)
        else:
            return


def edit_rules(arguments):
    words = ''
    if arguments.rules_path:
        f = open(arguments.rules_path, 'r', encoding='utf-8')
        words = f.read()
    if arguments.rules_text:
        words = arguments.rules_text
    if arguments.rules_clear:
        print('\033[91m' + "ARE YOU SURE?" + '\033[0m' + "y/n")
        sign = input()
        if sign.lower() == 'y':
            clean_rules_json(RULES_JSON_PATH)
        return
    rewrite_rules_json(words, RULES_JSON_PATH)


def parse_args(argus):
    parser = argparse.ArgumentParser(description=f'Welcome to the '
                                                 f'Spellchecker! Type '
                                                 f'\'-h\'for '
                                                 f'help')
    subparsers = parser.add_subparsers(title='commands',
                                       description='valid commands',
                                       required=True)
    check_parser = subparsers.add_parser('check', help='check text.txt')
    check_parser.add_argument('-t', '--text', dest='text',
                              help='text.txt to check',
                              type=str, nargs='+', metavar='')
    check_parser.add_argument('-p', '--path', dest='path', type=str,
                              help='path for file to check', metavar='')
    check_parser.add_argument('-d', '--database', dest='db', type=str,
                              help='path to custom .json database for '
                                   'Spellcheker',
                              metavar='')
    check_parser.set_defaults(function=check_spell)

    edit_parser = subparsers.add_parser('edit', help='edit database')
    edit_parser.add_argument('-p', '--path', dest='add_path', metavar='',
                             help='path for a file to add to database',
                             type=str)
    edit_parser.add_argument('-t', '--text', dest='add_text', metavar='',
                             help='text to add to database', nargs='+',
                             type=str)
    edit_group = edit_parser.add_mutually_exclusive_group()
    edit_group.add_argument('-c', '--clear', action='store_true',
                            help='clear database')
    edit_parser.set_defaults(function=edit_db)

    rules_parser = subparsers.add_parser('rules', help='add special rules')
    rules_parser.add_argument('-p', '--path', dest='rules_path', metavar='',
                              help='path for a file to add to database',
                              type=str)
    rules_parser.add_argument('-t', '--text', dest='rules_text', metavar='',
                              help='text to add to database',
                              type=str)
    rules_group = rules_parser.add_mutually_exclusive_group()
    rules_group.add_argument('-rc', '--rules_clear', action='store_true',
                             help='clear database')
    rules_group.set_defaults(function=edit_rules)
    return parser.parse_args(argus)


def main(args):
    arguments = parse_args(args)
    arguments.function(arguments)


if __name__ == '__main__':
    main(sys.argv[1:])
