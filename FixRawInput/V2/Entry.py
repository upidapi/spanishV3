from __future__ import annotations

import math
import random

import pygame as pg
from PIL import Image, ImageDraw

DEFAULT_BG = (255, 255, 255)
ENTRY_SIDE_WIDTH = 5


def get_n_good_colours(n):
    def hsv_to_rgb(h, s, v):
        i = math.floor(h * 6)
        f = h * 6 - i
        p = v * (1 - s)
        q = v * (1 - f * s)
        t = v * (1 - (1 - f) * s)

        r, g, b = [
            (v, t, p),
            (q, v, p),
            (p, v, t),
            (p, q, v),
            (t, p, v),
            (v, p, q),
        ][int(i % 6)]

        return r, b, g

    colours = [[x * 255 for x in hsv_to_rgb(i / (n + 1), 1, 1)] for i in range(n)]
    random.shuffle(colours)
    return colours


class Entry:
    """
    features
        focusable

        drag
            hold right-click

        split
            ctrl d
            splits entry into two at cursor

        merge
            hold shift
            drag A -> B =>
                B.text += A.text
                A.remove()

        delete
            middle-click or "del" key

        savestate
            force revert
                ctrl + z
            force save
                ctrl + s
            revert changes (load savestate) if user preses "esc"
            not ctrl + esc (handled by Controller)
    """

    def __init__(self,
                 handler: type(Controller),
                 pos: tuple[int, int] = (0, 0),
                 text: str = "",
                 o_text: str = "",
                 ):

        self.handler: Controller = handler
        self.handler.entries.append(self)

        self.background_colour = DEFAULT_BG

        self.text: str = text
        self.o_text: str = o_text

        self.pos: tuple[int, int] = pos
        self.size: tuple[int, int] = (0, 0)
        self.update_size()

        self.delta_drag_start: tuple[int, int] | None = None

        self.save_state = None
        self.checkpoint()

    @property
    def has_focus(self):
        return self.handler.focused_entry == self

    def delete(self):
        self.handler.entries.remove(self)
        self.handler.un_focus()

    def focus(self):
        self.handler.focus(self)

    def update_size(self):
        w, h = self.handler.font.size(self.text)
        w += ENTRY_SIDE_WIDTH * 2
        self.size = w, h

    def update_pos(self):
        """
        keeps the entry inside the screen
        """

        self.pos = (
            max(0, self.pos[0]),
            max(0, self.pos[1])
        )

        screen_size = self.handler.surface.get_size()

        to_right_side = screen_size[0] - (self.pos[0] + self.size[0])
        to_bottom_side = screen_size[1] - (self.pos[1] + self.size[1])

        move_left = min(0, to_right_side)
        move_up = min(0, to_bottom_side)

        self.pos = (
            self.pos[0] + move_left,
            self.pos[1] + move_up
        )

    # <editor-fold desc="savestate">
    def checkpoint(self):
        a = vars(self)
        del a["save_state"]
        self.save_state = a.copy()

    def load_checkpoint(self):
        for key in self.save_state.keys():
            self.__dict__[key] = self.save_state[key]
    # </editor-fold>

    def inside_hit_box(self, click_pos: tuple[int, int]) -> bool:
        if self.pos[0] <= click_pos[0] <= self.pos[0] + self.size[0]:
            if self.pos[1] <= click_pos[1] <= self.pos[1] + self.size[1]:
                return True
        return False

    def merge(self: Entry, other: Entry):
        """
        adds self to other
        """

        other.text += self.text
        other.o_text += self.o_text

        other.focus()
        other.update_size()
        self.delete()

    def split(self):
        # I have to implement the cursor first
        raise NotImplementedError(".split is not yet implemented")

    def handle_text(self, event):
        character = event.unicode
        if character.isprintable() and character != '':
            self.text += character
            self.update_size()
        if event.key == pg.K_BACKSPACE:
            self.text = self.text[:-1]
            self.update_size()

    # <editor-fold desc="drag">
    def start_drag(self, pos):
        self.handler.dragged_entry = self
        self.delta_drag_start = \
            (pos[0] - self.pos[0],
             pos[1] - self.pos[1])

    def drag(self, pos):
        if self.delta_drag_start is not None:
            self.pos = (pos[0] - self.delta_drag_start[0],
                        pos[1] - self.delta_drag_start[1])
    # </editor-fold>

    def handle_drag_event(self, event):
        shift = pg.key.get_mods() & pg.KMOD_SHIFT

        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 3:
                self.handler.handle_drag_event = self
                self.delta_drag_start = \
                    (event.pos[0] - self.pos[0],
                     event.pos[1] - self.pos[1])

        elif event.type == pg.MOUSEBUTTONUP:
            if event.button == 3:
                if shift:
                    over = self.handler.over_entries(event.pos)
                    over.remove(self)  # might cause problem

                    if len(over):
                        merge_with = over[0]

                        self.merge(merge_with)

                self.handler.dragged_entry = None

        elif event.type == pg.MOUSEMOTION:
            if pg.mouse.get_pressed()[2]:
                self.drag(pg.mouse.get_pos())

    def handle_event(self, event):
        ctrl = pg.key.get_mods() & pg.KMOD_CTRL

        if event.type == pg.KEYDOWN:
            if ctrl:
                if event.key == pg.K_s:
                    self.checkpoint()

                if event.key == pg.K_z:
                    self.load_checkpoint()

                if event.key == pg.K_d:
                    self.split()
            else:
                self.handle_text(event)

            if event.key == pg.K_DELETE:
                self.delete()

        # if event.type == pg.MOUSEBUTTONDOWN:
        #     if event.button == 2:  # middle click
        #         self.delete()

    def draw(self):
        text_colour = (0, 0, 0)
        if self in self.handler.non_pairs:
            text_colour = (255, 0, 0)

        if self.has_focus:
            text_colour = (0, 255, 0)

        rect = pg.Rect(self.pos, self.size)
        pg.draw.rect(self.handler.surface,
                     self.background_colour,
                     rect)

        text_surface = self.handler.font.render(
            self.text, True, text_colour)

        self.handler.surface.blit(text_surface,
                                  (self.pos[0] + ENTRY_SIDE_WIDTH,
                                   self.pos[1]))


class Controller:
    """
    Handles the entries.

    singleton

    features
        change lan translation
            ctrl + r
            switch from one lan to another in all entry's

        hide all entry's
            ctrl + q

        display unique background
            ctrl + w
            change all background's to be a unique colour

        display pair background
            ctrl + e
            change all background's to be a unique colour

    """

    def __new__(cls, *args, **kwargs):
        # singleton
        if not hasattr(cls, 'instance'):
            cls.instance = super(Controller, cls).__new__(cls)

        # f u pycharm
        # noinspection PyUnresolvedReferences
        return cls.instance

    def __init__(self, surface):
        self.surface: pg.Surface = surface
        self.font: pg.font = pg.font.SysFont('Comic Sans MS', 30)

        self.primary_lan = True  # if lan is switched or not
        self.focused_entry: Entry | None = None
        self.dragged_entry: Entry | None = None

        self.pairs: list[list[Entry, Entry]] = []
        self.non_pairs: list[Entry] = []

        self.entries: list[Entry] = []

        self.show_entries = True

    def over_entries(self, pos):
        over = []
        for entry in self.entries:
            if entry.inside_hit_box(pos):
                over.append(entry)
        return over

    def focus(self, entry):
        self.focused_entry = entry

    def un_focus(self):
        self.focused_entry = None

    def change_lan(self):
        self.primary_lan = not self.primary_lan
        for entry in self.entries:
            entry.text, entry.o_text = entry.o_text, entry.text
            entry.update_size()

    # <editor-fold desc="change backgrounds">
    def default_background(self):
        for entry in self.entries:
            entry.background_colour = DEFAULT_BG

    def unique_background(self):
        """
        gives etch entry a unique colour
        """
        colours = get_n_good_colours(len(self.entries))
        for entry, colour in zip(self.entries, colours):
            entry.background_colour = colour

    def pair_background(self):
        """
        gives etch entry pair a unique colour
        """

        # entries with no paring counts sa its own pair
        entry_pairs = len(self.pairs) + len(self.non_pairs)

        for colour, pair in zip(
                get_n_good_colours(entry_pairs),
                self.pairs + [[entry] for entry in self.non_pairs]):
            for entry in pair:
                entry.background_colour = colour

    # </editor-fold>

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            pass

        if self.focused_entry is not None:
            self.focused_entry.handle_event(event)

        if self.dragged_entry is not None:
            self.dragged_entry.handle_drag_event(event)

        if event.type == pg.MOUSEBUTTONDOWN:
            over = self.over_entries(event.pos)
            if event.button == 1:  # focus
                if over:
                    self.focus(over[0])
            if event.button == 2:  # create/remove entry
                if over:
                    over[0].delete()
                else:
                    entry = Entry(self, pos=event.pos)
                    entry.focus()
            if event.button == 3:  # drag
                if over:
                    over[0].start_drag(pg.mouse.get_pos())

        if event.type == pg.KEYDOWN:
            if pg.key.get_mods() & pg.KMOD_CTRL:
                # hide entries
                if event.key == pg.K_q:
                    self.show_entries = False
                # unique background
                if event.key == pg.K_w:
                    self.unique_background()
                # pair background
                if event.key == pg.K_e:
                    self.pair_background()
                # change lan
                if event.key == pg.K_r:
                    self.change_lan()

        if event.type == pg.KEYUP:
            if event.key == pg.K_q:
                self.show_entries = True
            if event.key in (pg.K_w, pg.K_e, pg.K_LCTRL, pg.K_RCTRL):
                self.default_background()

    # <editor-fold desc="pair handling">
    def get_connections(self):
        entries = self.entries.copy()
        entries.sort(key=lambda x: x.pos[1])  # sort by y pos

        margins = 1

        """
        the percentage you remove from the entry
        0 -> the entry has to overlap with the hotbox
        0.5 -> half the entry has to overlap
        1 -> the center has to overlap
        2 -> the whole lines has to be inside
        """

        pairs = []
        indexed = []
        for entry in entries:
            y = entry.pos[1]
            height = entry.size[1]
            """
            decreases the entry "size" by size * margins
            top_line
                y + height * margins / 2
            
            bottom_line
                y + height - height * margins / 2
                =>
                y + height(1 - * margins  / 2)
            """

            bottom_line = y + height * margins / 2
            top_line = y + height * (1 - margins / 2)

            for j, indexed_entry in enumerate(indexed):
                # if the top or bottom of the hit-box collides
                i_y = indexed_entry.pos[1]
                i_height = indexed_entry.size[1]
                top_hit_box, bottom_hit_box = i_y, i_y + i_height
                if top_hit_box <= bottom_line <= bottom_hit_box or \
                        top_hit_box <= top_line <= bottom_hit_box:
                    pairs.append((indexed_entry, entry))

            indexed.append(entry)

        return pairs

    def get_pairs(self):
        def connects_to(x):
            x_cn_to = []
            for pair in possible_pairs:
                if x in pair:
                    x_cn_to.append(pair)

            return x_cn_to

        data = self.entries.copy()

        possible_pairs = self.get_connections()

        tr_pairs: list[tuple[Entry, Entry]] = []
        non_pairs = []

        data.sort(key=lambda x: x.pos[0])  # sort by x pos
        while 0 < len(data):
            # a start that is guarantied to not have multiple things before it
            current_point = data[0]

            # all pairs with "current_point" included
            cn_pairs = connects_to(current_point)

            if not len(cn_pairs):
                data.pop(0)
                non_pairs.append(current_point)
                continue

            cn_pairs.sort(key=lambda x: x[0].pos[0] if x[1] == current_point else x[1].pos[0])
            best_cn = cn_pairs[0]

            data.remove(best_cn[0])
            data.remove(best_cn[1])

            tr_pairs.append(best_cn)

            possible_pairs = [possible_pair for possible_pair in possible_pairs
                              if not any(entry in possible_pair for entry in best_cn)]

        return tr_pairs, non_pairs

    def update_pairs(self):
        self.pairs, self.non_pairs = self.get_pairs()
    # </editor-fold>

    def draw_connections(self):
        for a, b in self.pairs:
            if a.pos[0] > b.pos[0]:
                a, b = b, a

            if a.pos[1] < b.pos[1]:
                # a over b
                a_rel = 0, 0
                b_rel = b.pos[0] - a.pos[0], b.pos[1] - a.pos[1]
            else:
                # a under b
                a_rel = 0, a.pos[1] - b.pos[1]
                b_rel = b.pos[0] - a.pos[0], 0

            image_size = (b.pos[0] - a.pos[0] + b.size[0],
                          abs(b.pos[1] - a.pos[1]) + b.size[1])

            image = Image.new(mode="RGBA",
                              size=image_size)
            draw = ImageDraw.Draw(image)

            from_pos = (a_rel[0] + a.size[0] / 2,
                        a_rel[1] + a.size[1] / 2)
            to_pos = (b_rel[0] + b.size[0] / 2,
                      b_rel[1] + b.size[1] / 2)

            draw.line((from_pos, to_pos), fill=(0, 0, 0))

            def remove_colour(pos, rect_size):
                i = Image.new(mode="RGBA",
                              size=rect_size)
                image.paste(i, pos)

            remove_colour(a_rel, a.size)
            remove_colour(b_rel, b.size)

            size = image.size
            data = image.tobytes()

            py_image = pg.image.fromstring(data, size, "RGBA")

            self.surface.blit(py_image,
                              (min(a.pos[0], b.pos[0]),
                               min(a.pos[1], b.pos[1])))

    def draw_entries(self):
        for entry in self.entries:
            entry.update_pos()

        self.update_pairs()

        for entry in self.entries:
            entry.draw()


# todo optimize when Entry.update_pos() gets called

# todo actually implement the entry part of Entry

# todo implement Entry.split()
