def split_str_list(word_list: list[str], key: str):
    # if type(word_list) is str:
    #     word_list = [word_list]

    split_word = []
    for word in word_list:
        split_word += word.split(key)

    return split_word


def clean(word, split_keys: tuple, remove_keys: tuple, remove_between_keys: tuple):
    """
    cleans up and splits the word

    :param word: the word to be cleaned
    :param split_keys: splits the words at all split_keys
    :param remove_keys: removes all instances of the remove_keys
    :param remove_between_keys:
    :return: the clean word(s) in a list
    """

    # adds to optional if the amount of characters between start key and end key is less than remove_ken
    word_list = [word]
    for key in split_keys:
        word_list = split_str_list(word_list, key)

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
