import pygame as pg


class Entry:
    """
    features
        focusable

        drag
            hold right-click

        split
            ctrl s
            splits entry into two at cursor

        merge
            hold shift
            drag A -> B =>
                B.text += A.text
                A.remove()

        delete
            middle-click or "del" key

        savestate
            only save changes if user presses "return"
            otherwise revert changes
    """

    def __init__(self):
        self.text: str = ""
        self.o_text: str = ""

        self.pos: tuple[int, int] = (0, 0)

        self.save_state = None
        self.checkpoint()

    def checkpoint(self):
        a = vars(self)
        del a["save_state"]
        self.save_state = a

    def load_checkpoint(self):
        pass

class Controller:
    """
    singleton

    features
        hide all entry's
            ctrl + e

        change lan translation
            ctrl + q
            switch from one lan to another in all entry's

        display unique background
            ctrl + w
            change all background's to be a unique colour

    """

    def __new__(cls):
        # singleton
        if not hasattr(cls, 'instance'):
            cls.instance = super(Controller, cls).__new__(cls)

        # f u pycharm
        return cls.instance

    def __init__(self):


