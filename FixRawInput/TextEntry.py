import time

import pygame as pg


class TextEntry:
    def __init__(self, surface, font, pos=(0, 0), rel_pos=(0, 0)):
        self.font: pg.font = font
        self.surface: pg.Surface = surface

        self.text_colour = (0, 0, 0)

        self.pos = pos
        self.rel_pos = rel_pos

        self.size = (0, 0)

        self.text = ""
        self.cursor_pos = 0

        self.is_focused = False

    @property
    def bef_cursor(self):
        return self.text[:self.cursor_pos]

    @property
    def aft_cursor(self):
        return self.text[self.cursor_pos:]

    def on_text_change(self):
        pass

    def handle_text(self, event):
        character = event.unicode
        if character.isprintable() and character != '':
            self.text = self.bef_cursor + character + self.aft_cursor
            self.cursor_pos += 1
            self.on_text_change()

        if event.key == pg.K_BACKSPACE:
            if len(self.bef_cursor):
                self.text = self.bef_cursor[:-1] + self.aft_cursor
                self.cursor_pos -= 1
                self.on_text_change()

    def handle_events(self, events):
        if self.is_focused:
            for event in events:
                if event.type == pg.KEYDOWN:
                    self.handle_text(event)

    def draw_text(self):
        text_surface = self.font.render(
            self.text, True, self.text_colour)

        self.size = text_surface.get_size()

        self.surface.blit(text_surface,
                          (self.pos[0] + self.rel_pos[0],
                           self.pos[1] + self.rel_pos[1]))

    def draw_cursor(self):
        if time.time() % 1 > 0.5:
            w, h = self.font.size(self.bef_cursor)

            rect = pg.Rect(
                w + self.rel_pos[0],
                self.rel_pos[1],
                2, h
            )

            pg.draw.rect(self.surface, (0, 0, 0), rect)

    def draw(self):
        self.draw_text()
        if self.is_focused:
            self.draw_cursor()


