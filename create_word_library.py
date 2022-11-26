import json
import regex


def get_dict(path):
    with open(path, 'r', encoding="utf-8") as f:
        dict = json.load(f)
    return dict


def get_text(path):
    with open(path, 'r', encoding="utf-8") as f:
        text = f.read().lower()
        words = regex.findall(r"[\p{L}-]+", text)
    return words


def add_words_to_dict(words, path):
    dictionary = get_dict(path)
    values_sorted_dict = {}
    for word in words:
        if word in dictionary.keys():
            dictionary[word] += 1
        else:
            dictionary[word] = 1
    sorted_keys = sorted(dictionary, key=dictionary.get, reverse=True)
    for w in sorted_keys:
        values_sorted_dict[w] = dictionary[w]
    return values_sorted_dict


def rewrite_json(words, path):
    dict_to_write = add_words_to_dict(words, path)
    with open(path, 'w', encoding="utf-8") as f:
        json.dump(dict_to_write, f, ensure_ascii=False, indent=4)


def clean_json(path):
    with open(path, 'w', encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=4)
