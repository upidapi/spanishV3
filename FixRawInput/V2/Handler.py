"""
controls the controller
"""
from FixRawInput.V2.Entry import Controller, Entry


class Handler:
    def __init__(self, screen, lan_s: tuple[str, str]):
        self.controller = Controller(screen)

        self.lan_s = lan_s

    def populate_entries(self, data):
        for d1, d2 in zip(*data):
            text_1, text_2 = d1['text'], d2['text']
            pos = d1['x'], d1['y']

            Entry(self.controller, pos=pos, text=text_1, o_text=text_2)

    def merge_pairs(self):
        if not self.controller.non_pairs:
            for pair in self.controller.pairs:
                pair.sort(key=lambda x: x.pos[0])

