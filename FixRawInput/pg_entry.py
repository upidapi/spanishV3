from __future__ import annotations

import math
import random

import pygame as pg


DEFAULT_BG = (255, 255, 255)

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

    colours = [hsv_to_rgb(i / (n + 1), 1, 1) for i in range(n)]
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

    def __init__(self, handler: type(Controller)):
        self.handler = handler

        self.background_colour = (0, 0, 0)

        self.text: str = ""
        self.o_text: str = ""

        self.pos: tuple[int, int] = (0, 0)
        self.size: tuple[int, int] = (0, 0)

        self.delta_drag_start: tuple[int, int] | None = None

        self.paring = None

        self.save_state = None
        self.checkpoint()

    def delete(self):
        self.handler.entries.remove(self)

    def focus(self):
        self.handler.fucus(self)

    @property
    def has_focus(self):
        return self.handler.fucus == self

    # <editor-fold desc="savestate">
    def checkpoint(self):
        a = vars(self)
        del a["save_state"]
        self.save_state = a

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
        self.delete()

    def split(self):
        # I have to implement the cursor first
        raise NotImplementedError(".split is not yet implemented")

    def drag(self, pos):
        if self.delta_drag_start is not None:
            self.pos = (pos[0] + self.delta_drag_start[0],
                        pos[1] + self.delta_drag_start[1])

    def handle_event(self, event):
        def handle_drag_event():
            if event.type == pg.MOUSEBUTTONDOWN:
                self.delta_drag_start = \
                    (event.pos[0] - self.pos[0],
                     event.pos[1] - self.pos[1])
            elif event.type == pg.MOUSEBUTTONUP:
                if shift:
                    over = self.handler.over_entries(event.pos)
                    over.remove(self)   # might cause problem

                    if len(over):
                        merge_with = over[0]

                        self.merge(merge_with)

                self.delta_drag_start = None

            else:
                self.drag(event.pos)

        shift = pg.key.get_mods() & pg.KMOD_SHIFT
        ctrl = pg.key.get_mods() & pg.KMOD_CTRL

        # might cause problem
        if event.button == 3:  # right click
            handle_drag_event()

        if event.type == pg.KEYDOWN:
            if ctrl:
                if event.key == pg.K_s:
                    self.checkpoint()

                if event.key == pg.K_z:
                    self.load_checkpoint()

            if event.key == pg.K_d:
                self.split()

            if event.key == pg.K_DELETE:
                self.delete()

        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 2:  # middle click
                self.delete()


class Controller:
    """
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

    def __new__(cls):
        # singleton
        if not hasattr(cls, 'instance'):
            cls.instance = super(Controller, cls).__new__(cls)

        # f u pycharm
        return cls.instance

    def __init__(self):
        self.focused_entry: Entry | None = None

        self.show_entries = True

        self.pairs = []

        self.entries: list[Entry] = []

    def over_entries(self, pos):
        over = []
        for entry in self.entries:
            if entry.inside_hit_box(pos):
                over.append(entry)
        return over

    def focus(self, entry):
        self.focused_entry = entry

    def change_lan(self):
        for entry in self.entries:
            entry.text, entry.o_text = entry.o_text, entry.text

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
        pairs = 0
        for entry in self.entries:
            if entry.paring is not None:
                pairs += 0.5  # only half of the pair

        # entries with no paring counts sa its own pair
        entry_pairs = len(self.entries) - int(pairs)

        uncoloured_entries = self.entries

        for colour in get_n_good_colours(entry_pairs):
            if not len(uncoloured_entries):
                pair_start = uncoloured_entries[0]
                uncoloured_entries.pop(0)

                pair_start.background_colour = colour
                if pair_start.paring is not None:
                    pair_start.paring.background_colour = colour
                    uncoloured_entries.remove(pair_start.paring)
    # </editor-fold>

    def handle_events(self):
        for event in pg.event.get():
            self.focused_entry.handle_event(event)

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

        tr_pairs = []
        non_pairs = []

        data.sort(key=lambda x: x.pos[0])  # sort by x pos
        while 0 < len(data):
            # a start that is guarantied to not have multiple things before it
            current_point = data.pop(0)

            # all pairs with "current_point" included
            cn_pairs = connects_to(current_point)

            if not len(cn_pairs):
                non_pairs.append(current_point)
                continue

            best_cn = cn_pairs.pop(0)

            for cn_pair in cn_pairs[1:]:
                # don't reference a paired line
                possible_pairs.remove(cn_pair)

                connection = cn_pair[0] if cn_pair[1] == current_point else cn_pair[1]
                if connection.pos[0] < best_cn.pos[0]:
                    best_cn = connection

            tr_pairs.append((current_point, best_cn))
            data.remove(best_cn)

            # don't reference a paired line
            best_cn_cns = connects_to(best_cn)

            for best_cn_cn in best_cn_cns:
                possible_pairs.remove(best_cn_cn)

        return tr_pairs, non_pairs

    def update_pairs(self):
        """
        updates
        """
    # </editor-fold>


    def draw(self):
        def draw_connections():
            pass

        if self.show_entries:
            draw_connections()
            for entry in self.entries:
                entry.draw()