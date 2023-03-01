from typing import Literal

import tkinter as tk

from Structure import check_correct

ModeType = Literal[
    "same",
    "wrong",
    "next_section",
    "lan_1",
    "lan_2"
]


class Word:
    def __init__(self, text, translation):
        self.switch = False

        self.lan_1_text = text
        self.lan_2_text = translation

        self.lan_1_node = text
        self.lan_2_node = translation

    @property
    def primary_text(self):
        if self.switch:
            return self.lan_2_text
        return self.lan_1_text

    @property
    def translation_text(self):
        if self.switch:
            return self.lan_1_text
        return self.lan_2_text

    @property
    def primary_node(self):
        if self.switch:
            return self.lan_2_node
        return self.lan_1_node

    @property
    def translation_node(self):
        if self.switch:
            return self.lan_1_node
        return self.lan_2_node


class Words:
    def __init__(self):
        self.all_words: list[Word] = []
        self.sections_left: list[Word] = []
        self.words_left: list[Word] = []

        self.last_section: list[Word] = []
        self.incorrect_words: list[Word] = []
        self.current_word: Word | None = None

        self.section_size: int | None = 10

        self.on_new_word = None
        self.on_correct = None
        self.on_wrong = None

        self.get_new_words()

    def get_available_modes(self) -> list[str]:

        available_modes = [
            "lan_1",
            "lan_2"
        ]

        if len(self.sections_left) and self.section_size:
            available_modes.append("next_section")

        if len(self.incorrect_words):
            available_modes.append("wrong")

        if len(self.last_section):
            available_modes.append("same")

        return available_modes

    def get_new_mode(self) -> ModeType | None:
        available_modes = self.get_available_modes()

        mode = None
        index = 0

        root = tk.Tk()
        width = 100
        height = len(available_modes) * 20
        root.geometry(f"{height}x{width}")

        def select(select_type):
            nonlocal mode
            mode = select_type

            root.destroy()

        def add_button(button_mode, text):
            nonlocal index
            if button_mode in available_modes:
                index += 1
                y_pos = 20 * index + 10
                button = tk.Button(root, text=text,
                                   command=lambda: select(button_mode))
                button.place(relx=0.5, y=y_pos, anchor=tk.CENTER)

        add_button("lan_1", "from lan_1 to lan_2")
        add_button("lan_2", "from lan_2 to lan_1")
        add_button("same", "the same words as last time")
        add_button("wrong", "the ones you got wrong")
        add_button("next_section", "the next section")

        return mode

    def get_new_words(self):
        mode = self.get_new_mode()
        if mode is None:
            mode = self.get_new_mode()

        if mode == "same":
            self.words_left = self.last_section.copy()

        elif mode == "wrong":
            self.words_left = self.incorrect_words.copy()

        elif mode == "next_section":
            self.words_left = self.sections_left[:self.section_size]

            del self.sections_left[:self.section_size]

        elif mode == "lan_1":
            for word in self.all_words:
                word.switch = False

            self.words_left = self.all_words.copy()

        elif mode == "lan_2":
            for word in self.all_words:
                word.switch = True

            self.words_left = self.all_words.copy()

        self.last_section = self.words_left.copy()

    def next_word(self):
        if not len(self.words_left):
            self.get_new_words()
            return

        self.current_word = self.words_left.pop(0)
        self.on_new_word(self.current_word)

    def temp_name(self, text):
        correct = check_correct(self.current_word.primary_node,
                                self.current_word.primary_text)

