"""
controls the controller
"""

import pygame as pg

from FixRawInput.V2.Entry import Controller, Entry


class Handler:
    def __init__(self, screen, lan_s: tuple[str, str]):
        self.controller = Controller(screen)

        self.screen = screen
        # self.clock = clock

        self.lan_s = lan_s

        self.mode = 0

    def configure_screen(self):
        pass

    def populate_entries(self, data):
        for d1, d2 in zip(*data):
            text_1, text_2 = d1['text'], d2['text']
            pos = d1['x'], d1['y']

            Entry(self.controller, pos=pos, text=text_1, o_text=text_2)

    def merge_pairs(self):
        self.mode = 1

        if not self.controller.non_pairs:
            if not self.controller.primary_lan:
                self.controller.change_lan()

            for pair in self.controller.pairs:
                pair.sort(key=lambda x: x.pos[0])

                pair[0].o_text = pair[0].text
                pair[1].text = pair[1].o_text

    def next_mode(self):
        if self.mode == 0:
            self.merge_pairs()
            return

    def compute_frame(self, events):
        for event in events:
            self.controller.handle_event(event)
            if pg.key.get_mods() & pg.KMOD_CTRL:
                if pg.key == pg.K_RETURN:
                    self.next_mode()

        self.screen.fill((255, 255, 255))

        if self.controller.show_entries:
            self.controller.draw_entries()

            if self.mode == 0:
                self.controller.draw_connections()

        pg.display.flip()
