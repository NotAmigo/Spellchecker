import json


def get_dict(path):
    with open(path, 'r', encoding="utf-8") as f:
        dictionary = json.load(f)
    return dictionary


def add_words_to_dict(path_json, text):
    dictionary = get_dict(path_json)
    for line in text.split('\n'):
        splitted_line = line.split('->')
        error, correct = splitted_line[0], splitted_line[1]
        if error not in dictionary.keys():
            dictionary[error] = [correct]
        else:
            if correct not in dictionary[error]:
                dictionary[error].append(correct)
    return dictionary


def rewrite_rules_json(path_text, path_json):
    dict_to_write = add_words_to_dict(path_json, path_text)
    with open(path_json, 'w', encoding="utf-8") as f:
        json.dump(dict_to_write, f, ensure_ascii=False, indent=4)


def clean_rules_json(path):
    with open(path, 'w', encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=4)
