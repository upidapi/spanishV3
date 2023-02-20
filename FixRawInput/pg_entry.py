from __future__ import annotations

import pygame as pg


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

        self.text: str = ""
        self.o_text: str = ""

        self.pos: tuple[int, int] = (0, 0)
        self.size: tuple[int, int] = (0, 0)

        self.delta_drag_start: tuple[int, int] | None = None

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

    def handle_event(self, events):
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

        for event in events:
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
        self.focused_entry = None

        self.entries = []

    def over_entries(self, pos):
        over = []
        for entry in self.entries:
            if entry.inside_hit_box(pos):
                over.append(entry)
        return over

    def focus(self, entry):
        self.focused_entry = entry
