import random
from typing import Literal

# from Data import get_translate_data
from Quiz.other import end_screen


from Structure.Other import check_correct


def temp_func_3(_, data_files):
    import json
    book_data = []
    for file in data_files:
        with open(file) as jsonFile:
            book_data += json.load(jsonFile)
            jsonFile.close()

    # with open(config) as jsonFile:
    #     config_data = json.load(jsonFile)
    #     jsonFile.close()
    #
    # for i, pair in enumerate(book_data):
    #     for j, word in enumerate(pair):
    #         book_data[i][j] = clean(word,
    #                                 split_keys=config_data["split_keys"],
    #                                 remove_keys=config_data["remove_keys"],
    #                                 remove_between_keys=config_data["remove_between_keys"])
    return book_data


# temporary implementation to use Structure module instead of the old Data module
def temp_func_2(data: list) -> tuple[list[dict, ...], list[dict, ...]]:
    from Structure.Constructor import convert_linear_word, TempName
    from Structure.Helpers import OrStatement

    w1_to_w2 = []
    w2_to_w1 = []

    blueprint = (
        (TempName.between_greedy, (";",)),
        (TempName.between_optional, (("(", ")"),)),
        (TempName.between_permissive, ("/",)),
        (TempName.replace, (("a, -n", OrStatement("a", "n")),
                            ("o, -a, -as, -os", OrStatement("o", "a", "os", "as")),
                            ("o, -a", OrStatement("o", "a")),)),
        (TempName.optional, ("/ue/", "/ie/", "/de/", "... ", "de$")),
        (TempName.between_permissive, (",",)),
    )

    for pair in data:
        # todo make simular word translations combine
        #  [hej, tjena] => [hola]
        #  [halå, tjena] => [oye]
        #  =>
        #  [hej, tjena] => [hola, oye]
        #  [halå, tjena] => [hola, oye]

        w1_to_w2.append({'word': pair[0], 'translation': convert_linear_word(pair[1], blueprint)})
        w2_to_w1.append({'word': pair[1], 'translation': convert_linear_word(pair[0], blueprint)})
        # for word in pair[0]:
        #     w1_to_w2.append({'word': word, 'translation': pair[1]})
        #     # if word in w1_to_w2:
        #     #     w1_to_w2.append({'word': word, 'translation': pair[1]})
        #     # else:
        #     #     # the join(list) is to prevent multiple possible translations become multiple 'words'
        #     #     w1_to_w2.append({'word': ' / '.join(pair[0]), 'translation': pair[1]})
        #
        # for word in pair[1]:
        #     w2_to_w1.append({'word': word, 'translation': pair[0]})
        #     # if word in w2_to_w1:
        #     #     w2_to_w1.append({'word': word, 'translation': pair[0]})
        #     # else:
        #     #     # the join(list) is to prevent multiple possible translations become multiple 'words'
        #     #     w2_to_w1.append({'word': ' / '.join(pair[1]), 'translation': pair[0]})

    return w1_to_w2, w2_to_w1


def temp_func():
    # from Data.load_data import load_book_data
    from Data.FileBrowser import ask_for_files

    book_data = []

    books = ask_for_files()
    if books:
        for book in books:
            config_file = book["config_file"]
            data_files = book["data_files"]
            book_data += temp_func_3(config_file, data_files)
        return temp_func_2(book_data)

    else:
        # temporary fix
        # if you don't select anything just bring it upp again
        temp_func()


class WordData:
    def __init__(self, languishes):
        self.languishes = languishes

        self.right_answer = None
        self.wrong_answer = None
        self.set_translate_text = None

        self.all = temp_func()
        # self.all = get_translate_data()
        self.selected = []  # all selected words
        self.current = []  # all words left
        self.right = []
        self.wrong = []

        self.retry = False  # is true when you retry to type a word
        self.current_word = {'word': None, 'translation': None}

    def setup(self, right_answer, wrong_answer, set_translate_text):
        self.right_answer = right_answer
        self.wrong_answer = wrong_answer
        self.set_translate_text = set_translate_text

    def nothing_left(self):
        end_screen(self, self.languishes)

    # the cls is used so that the abstract methods gets called
    def next_word(self, first=False):
        if not first:
            self.current.remove(self.current_word)

        if len(self.current) == 0:
            self.nothing_left()
        else:
            self.current_word = random.choice(self.current)
            self.set_translate_text(self.current_word['word'])

    def get_new_words(self, select: Literal['wrong', 'right', 'same', 'lan1', 'lan2']):
        # this is never None
        new_data = None

        if select == 'wrong':
            new_data = self.wrong
        elif select == 'right':
            new_data = self.right
        elif select == 'same':
            new_data = self.selected
        elif select == 'lan1':
            new_data = self.all[0]
        elif select == 'lan2':
            new_data = self.all[1]

        # makes it possible to load the same data as last time
        self.selected = new_data.copy()
        self.current = new_data.copy()
        self.right = []
        self.wrong = []

    def check_correct(self, word):
        # correct = word in self.current_word['translation']
        correct = check_correct(word, self.current_word['translation'])
        if correct:
            # right
            if not self.retry:
                self.right.append(self.current_word)
            self.retry = False

            self.right_answer(self)

            self.next_word()  # force user to type it right before continuing

        else:
            # wrong
            self.wrong_answer(self)

            if not self.retry:
                self.wrong.append(self.current_word)
            self.retry = True
        # self.next_word()
