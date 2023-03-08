from __future__ import annotations

import inspect


# todo add support for finding min_size
#  The min size is the minimum size self can be
#  while still containing all of its children.

# todo make .fill and .fit do something

class Widget:
    def __init__(self, parent):
        self.parent = parent
        self.children = []

        self._changed = False

        # should self be drawn or not
        self.show: bool = True

        # should self fill parent
        self.fill: bool = False
        # should self fit around children
        self.fit: bool = False

        self._pos: None | list[int, int] = [0, 0]
        self._size: None | list[int, int] = [0, 0]

        # <editor-fold desc="padding">
        # format [padding to the left/top, padding to the right/bottom]
        self._pad_x: list[int, int] = [0, 0]
        self._pad_y: list[int, int] = [0, 0]
        self._border_x: list[int, int] = [0, 0]
        self._border_y: list[int, int] = [0, 0]
        # self._ipad_x: list[int, int] = [0, 0]
        # self._ipad_y: list[int, int] = [0, 0]

        # make the padding dynamically affect the size
        def x(name: str, width_height: int):
            protected_name = "_" + name

            def y(_) -> list[int, int]:
                return self.__getattribute__(protected_name)

            def z(_, value: list[int, int]):
                self.size[width_height] += sum(value) - sum(self.__getattribute__(protected_name))
                self.__setattr__(protected_name, value)

            return property(
                fget=y,
                fset=z
            )

        self.pad_x = x("pad_x", 0)
        self.pad_y = x("pad_y", 1)
        self.border_x = x("border_x", 0)
        self.border_y = x("border_y", 1)
        # self.ipad_x = x("ipad_x", 0)
        # self.ipad_y = x("ipad_y", 1)

        # ipad don't affect the size
        self.ipad_x: list[int, int] = [0, 0]
        self.ipad_y: list[int, int] = [0, 0]

        # </editor-fold>

    # <editor-fold desc="properties">
    @property
    def is_placed(self) -> bool:
        if self.pos is None or self.size is None:
            return False
        return True

    @property
    def changed(self) -> bool:
        return self._changed

    @changed.setter
    def changed(self, value: bool):
        if value:
            if not self._changed:
                self._changed = True
                self.parent._changed = True
        else:
            self._changed = False

    # <editor-fold desc="size">
    @property
    def size(self) -> list[int, int]:
        return self._size

    @size.setter
    def size(self, value: list[int, int]):
        self.parent.update()
        self._size = value

    @property
    def outer_size(self) -> list[int, int]:
        outer_size = [
            self.size[0] + sum(self.pad_x),
            self.size[1] + sum(self.pad_y),
        ]

        return outer_size

    @outer_size.setter
    def outer_size(self, value: list[int, int]):
        self.size = [
            value[0] - sum(self.pad_x),
            value[1] - sum(self.pad_y)
        ]

    @property
    def inner_size(self) -> list[int, int]:
        inner_size = [
            self.size[0] - sum(self.border_x + self.ipad_x),
            self.size[1] - sum(self.border_y + self.ipad_y),
        ]

        return inner_size

    @inner_size.setter
    def inner_size(self, value: list[int, int]):
        self.size = [
            value[0] + sum(self.border_x, self.ipad_x),
            value[1] + sum(self.border_y, self.ipad_y)
        ]
    # </editor-fold>

    # <editor-fold desc="pos">
    @property
    def pos(self) -> list[int, int]:
        return self._pos

    @pos.setter
    def pos(self, value: list[int, int]):
        self.parent.update()
        self._pos = value

    @property
    def inner_pos(self) -> list[int, int]:
        inner_pos = [
            self.pos[0] + sum((self.pad_x[0], self.border_x[0], self.ipad_x[0])),
            self.pos[1] + sum((self.pad_y[0], self.border_y[0], self.ipad_y[0]))
        ]

        return inner_pos

    @inner_pos.setter
    def inner_pos(self, value: list[int, int]):
        self.pos = [
            value[0] - sum((self.pad_x[0], self.border_x[0], self.ipad_x[0])),
            value[1] - sum((self.pad_y[0], self.border_y[0], self.ipad_y[0]))
        ]
    # </editor-fold>
    # </editor-fold>

    # <editor-fold desc="place">
    def place(self, *,
              inner_pos=None,
              pos=None,

              inner_size: None | list[int, int] = None,
              size: None | list[int, int] = None,
              outer_size: None | list[int, int] = None,

              pad_x: None | list[int, int] = None,
              pad_y: None | list[int, int] = None,
              border_x: None | list[int, int] = None,
              border_y: None | list[int, int] = None,
              ipad_x: None | list[int, int] = None,
              ipad_y: None | list[int, int] = None,
              ):

        sig, current_locals = inspect.signature(self.place), locals()
        all_kwargs = {param.name: current_locals[param.name] for param in sig.parameters.values()}

        kwarg_keys = (
            inner_pos,
            pos,

            inner_size,
            size,
            outer_size,

            pad_x,
            pad_y,
            border_x,
            border_y,
            ipad_x,
            ipad_y,
        )

        for key in kwarg_keys:
            if all_kwargs[key] is not None:
                self.__setattr__(key, all_kwargs[key])
    # </editor-fold>

    def update(self):
        if not self.changed:
            return

        # update self

        self.changed = False

        for child in self.children:
            child.update()

    # <editor-fold desc="draw">
    def draw(self):
        """
        draws self
        """

    def draw_recursion(self, surface, abs_pos=(0, 0)):
        inner_pos = self.inner_pos

        for child in self.children:
            child_pos = [
                inner_pos[0] + child.pos[0],
                inner_pos[1] + child.pos[1]
            ]

            child.draw_recursion(child_pos, surface, abs_pos)
    # </editor-fold>
