import json


def load_data(files: list):
    full_data = []
    for file in files:
        with open(file) as jsonFile:
            full_data += json.load(jsonFile)
            jsonFile.close()

    return full_data


def clean(word, split_keys: tuple, remove_keys: tuple, remove_between_keys: tuple):
    """
    cleans up and splits the word

    :param word: the word to be cleaned
    :param split_keys: splits the words at all split_keys
    :param remove_keys: removes all instances of the remove_keys
    :param remove_between_keys:
    :return: the clean word(s) in a list
    """
    word.lower()

    # removes all instances of the remove_keys
    for key in remove_keys:
        word = word.replace(key, '')

    # removes anything between key[0] and key[1]
    for key in remove_between_keys:
        new_word = ""
        remove = False
        for letter in word:
            if letter == key[0]:
                remove = True
            elif letter == key[1]:
                remove = False
            elif not remove:
                new_word += letter
        word = new_word
    # splits the words at all split_keys
    word = [word]
    split_word = []
    for key in split_keys:
        for part in word:
            split_word += part.split(key)
        word += split_word
    word = word[1:]

    # removes the trailing and leading spaces
    for i, part in enumerate(word):
        word[i] = part.strip()

    return word


def find_alternative_translations(data: list):
    w1_to_w2 = []
    w2_to_w1 = []

    for translation in data:
        for word in translation[0]:
            if word in w1_to_w2:
                w1_to_w2.append({'word': word, 'translation': translation[1]})
            else:
                # the join(list) is to prevent multiple possible translations become multiple 'words'
                w1_to_w2.append({'word': ' / '.join(translation[0]), 'translation': translation[1]})

        for word in translation[1]:
            if word in w2_to_w1:
                w2_to_w1.append({'word': word, 'translation': translation[0]})
            else:
                # the join(list) is to prevent multiple possible translations become multiple 'words'
                w2_to_w1.append({'word': ' / '.join(translation[1]), 'translation': translation[0]})

    return w1_to_w2, w2_to_w1


def load_book_data(config, data_files):
    """
    book = {
        # (inside the file ->)
        "config_file": {
            "split_keys": [
                    ";"
                ],
            "remove_keys": [
                    "ung."
                ],
            "remove_between_keys": [
                    ["(", ")"],
                    ["/", "/"]
                ]
        },
        "data_files": [
            "file_path.json",
            "file_path.json",
            "file_path.json",
        ]
    }
    """

    book_data = []
    for file in data_files:
        with open(file) as jsonFile:
            book_data += json.load(jsonFile)
            jsonFile.close()

    with open(config) as jsonFile:
        config_data = json.load(jsonFile)
        jsonFile.close()

    for i, pair in enumerate(book_data):
        for j, word in enumerate(pair):
            book_data[i][j] = clean(word,
                                    split_keys=config_data["split_keys"],
                                    remove_keys=config_data["remove_keys"],
                                    remove_between_keys=config_data["remove_between_keys"])

    return book_data


def get_translate_data():
    from Data.FileBrowser import ask_for_files

    book_data = []

    books = ask_for_files()
    if books:
        for book in books:
            config_file = book["config_file"]
            data_files = book["data_files"]
            book_data += load_book_data(config_file, data_files)
            return find_alternative_translations(book_data)

    else:
        # temporary fix
        # if you don't select anything just bring it upp again
        get_translate_data()


def load_clean_data():
    from Data.FileBrowser import ask_for_files

    files = ask_for_files()

    all_data = load_data(files)

    for i, pair in enumerate(all_data):
        for j, word in enumerate(pair):
            all_data[i][j] = clean(word,
                                   split_keys=(';',),
                                   remove_keys=('ung.',),
                                   remove_between_keys=(('(', ')'), ('/', '/')))

    return find_alternative_translations(all_data)


def load_raw_data():
    def _get_data(file):
        # gets the New
        with open(file) as jsonFile:
            json_object = json.load(jsonFile)
            jsonFile.close()

        return json_object

    data_1 = _get_data(r'../Data/DataFiles/lan1_data.json')
    data_2 = _get_data(r'../Data/DataFiles/lan2_data.json')

    return data_1, data_2
