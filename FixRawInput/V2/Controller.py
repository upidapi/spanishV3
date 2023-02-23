"""
controls the handler
"""

import pygame as pg

from Data import load_raw_data
from FixRawInput.V2.Entry import Handler, Entry


class Controller:
    def __init__(self, screen, lan_s: tuple[str, str]):
        self.handler = Handler(screen)

        self.screen = screen

        self.background = pg.image.load(r'../../Data/DataFiles/selected_image.jpg')

        self.lan_s = lan_s

        self.mode = 0

        data = load_raw_data()
        self.populate_entries(data)

    def configure_screen(self):
        pass

    def populate_entries(self, data):
        for d1, d2 in zip(*data):
            text_1, text_2 = d1['text'], d2['text']
            pos = d1['x'], d1['y']

            Entry(self.handler, pos=pos, text=text_1, o_text=text_2)

    def merge_pairs(self):
        if not self.handler.non_pairs:
            if not self.handler.primary_lan:
                self.handler.change_lan()

            for pair in self.handler.pairs:
                pair.sort(key=lambda x: x.pos[0])

                pair[0].o_text = pair[0].text
                pair[1].text = pair[1].o_text

            self.mode = 1

    def next_mode(self):
        if self.mode == 0:
            self.merge_pairs()
            return

    def compute_frame(self, events):
        for event in events:
            self.handler.handle_event(event)
            if event.type == pg.KEYDOWN:
                if pg.key.get_mods() & pg.KMOD_CTRL:
                    if event.key == pg.K_RETURN:
                        self.next_mode()

        self.screen.blit(self.background, (0, 0))

        if self.handler.show_entries:
            self.handler.draw_entries()

            if self.mode == 0:
                self.handler.draw_connections()

        pg.display.flip()
