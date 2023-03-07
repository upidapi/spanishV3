from __future__ import annotations

import inspect
from typing import Type


def matrix_map(func: callable, *args: list | tuple):
    length = len(args[0])
    for thing in args[1:]:
        assert len(thing) == length

    return [func([arg[i] for arg in args])
            for i in range(len(args))]


def matrix_add(*args: list | tuple):
    return matrix_map(sum, *args)


class Window:
    pass


class Widget:
    def __init__(self, parent, *,
                 show: bool = True,
                 **kwargs):

        # <editor-fold desc="pos">
        self.x: None | int = None
        self.y: None | int = None
        self.rel_x: None | float = None
        self.rel_y: None | float = None
        # </editor-fold>

        # <editor-fold desc="padding">
        self.pad_x: list[int, int] = [0, 0]
        self.pad_y: list[int, int] = [0, 0]
        self.ipad_x: list[int, int] = [0, 0]
        self.ipad_y: list[int, int] = [0, 0]
        # </editor-fold>

        # <editor-fold desc="size">
        self.min_size: None | list[int, int] = None
        self.max_size: None | list[int, int] = None

        self.internal_size: list[int, int] = [0, 0]
        self.size: None | list[int, int] = None
        self.external_size: list[int, int] = [0, 0]

        # make self fill parent
        self.fill: bool = False
        # make self contract around min_size
        self.fit: bool = False
        # </editor-fold>

        self.placed = False

        self.parent: Type[Widget] | Widget = parent
        self.children: list = []

        # self.pos_changed = False
        # self.size_changed = False
        # self.pos_changed = False

        self.show: bool = show

        parent.adopt(self)

    def adopt(self, child):
        self.children.append(child)
        child.parent = self

    def place(self,
              x: None | int = None,
              y: None | int = None,
              rel_x: None | float = None,
              rel_y: None | float = None,

              pad_x: list[int, int] = (0, 0),
              pad_y: list[int, int] = (0, 0),
              ipad_x: list[int, int] = (0, 0),
              ipad_y: list[int, int] = (0, 0),

              min_size: None | list[int, int] = None,
              max_size: None | list[int, int] = None,

              size: None | list[int, int] = None,
              fill: bool = False,
              fit: bool = False):

        self.placed = True

        # <editor-fold desc="pos">
        if x is None and rel_x is None:
            raise TypeError("no x pos found")

        if x and rel_x:
            raise TypeError("multiple x pos found")

        if y is None and rel_y is None:
            raise TypeError("no y pos found")

        if y and rel_y:
            raise TypeError("multiple y pos found")

        self.x = x
        self.y = y
        self.rel_x = rel_x
        self.rel_y = rel_y
        # </editor-fold>

        # <editor-fold desc="padding">
        self.pad_x = pad_x
        self.pad_y = pad_y
        self.ipad_x = ipad_x
        self.ipad_y = ipad_y
        # </editor-fold>

        # <editor-fold desc="size">
        self.min_size = [0, 0]
        self.max_size = [0, 0]

        self.internal_size = [0, 0]
        self.size = size
        self.external_size = [0, 0]

        # make self fill parent
        self.fill = fill
        # make self contract around min_size
        self.fit = fit

        temp = self.fill + self.fit + bool(self.size)
        if temp > 1:
            used = {'fill' if self.fill else ''}, {'fit' if self.fill else ''}, {'size' if self.fill else ''}
            used = ", ".join(used[:-1]) + " and " + used[-1]
            raise TypeError(f"Can't use multiple size managers ({used})")
        if temp == 0:
            raise TypeError("No size controller found")
        # </editor-fold>

    def un_place(self):
        self.placed = False

        # <editor-fold desc="pos">
        self.x: None | int = None
        self.y: None | int = None
        self.rel_x: None | float = None
        self.rel_y: None | float = None
        # </editor-fold>

        # <editor-fold desc="padding">
        self.pad_x: list[int, int] = [0, 0]
        self.pad_y: list[int, int] = [0, 0]
        self.ipad_x: list[int, int] = [0, 0]
        self.ipad_y: list[int, int] = [0, 0]
        # </editor-fold>

        # <editor-fold desc="size">
        self.min_size: None | list[int, int] = None
        self.max_size: None | list[int, int] = None

        self.internal_size: list[int, int] = [0, 0]
        self.size: None | list[int, int] = None
        self.external_size: list[int, int] = [0, 0]

        # make self fill parent
        self.fill: bool = False
        # make self contract around min_size
        self.fit: bool = False
        # </editor-fold>

    def update_min_size(self):
        self.min_size = matrix_map(max, [child.corner_pos for child in self.children])

        self.parent.update_min_size()

    def update_size(self):
        total_ipad = (self.ipad_x[0] + self.ipad_x[1],
                      self.ipad_y[0] + self.ipad_y[1])
        total_pad = (self.pad_x[0] + self.pad_x[1],
                     self.pad_y[0] + self.pad_y[1])

        if self.fit:
            self.internal_size = self.min_size.copy()

            self.size = [self.internal_size[0] + total_ipad[0],
                         self.internal_size[1] + total_ipad[1]]

            self.external_size = [self.size[0] + total_pad[0],
                                  self.size[1] + total_pad[1]]

        elif self.fill:
            self.external_size = self.parent.internal_size.copy()

            self.size = [self.internal_size[0] + total_ipad[0],
                         self.internal_size[1] + total_ipad[0]]

            self.external_size = [self.size[0] + total_pad[0],
                                  self.size[1] + total_pad[1]]

        else:
            self.internal_size = [self.size[0] - total_ipad[0],
                                  self.size[1] - total_ipad[1]]

            self.external_size = [self.size[0] + total_pad[0],
                                  self.size[1] + total_pad[1]]

    def update_pos(self):
        if self.fill:
            self.x = 0
            self.y = 0

        elif self.fit:
            self.x = 0
            self.y = 0

        else:
            if self.rel_x is not None:
                self.x = (self.parent.size[0] - self.size[0]) * self.rel_x + self.size[0] // 2

            if self.rel_y is not None:
                self.y = (self.parent.size[1] - self.size[1]) * self.rel_y + self.size[0] // 2

    def draw(self, pos):
        pass

    def draw_recursion(self, pos, surface):
        """
        :param pos: the absolute pos of self
        :param surface:
        """
        if self.show:
            self.draw(pos)

            for child in self.children:
                child.draw_recursion(matrix_add(pos,
                                                (self.ipad_x, self.ipad_y),
                                                (child.pad_x, child.pad_y),
                                                child.pos),
                                     surface)


class GridCell(Widget):
    def __init__(self,
                 parent: Grid,
                 *,
                 row: int,
                 column: int,
                 row_span: int = 1,
                 column_span: int = 1):

        super().__init__(parent)

        self.row: int = row
        self.column: int = column
        self.row_span: int = row_span
        self.column_span: int = column_span

        self.parent: Grid = parent

    def place(self, **kwargs):
        raise AttributeError("type object 'GridPart' has no attribute 'place'")

    def un_place(self, **kwargs):
        raise AttributeError("type object 'GridPart' has no attribute 'un_place'")

    def update_pos(self):
        self.x = round(sum(self.parent.x_grid_size[:self.column]))
        self.y = round(sum(self.parent.y_grid_size[:self.row]))

    def update_size(self):
        self.size = [round(sum(self.parent.x_grid_size[self.column:self.column + self.column_span])),
                     round(sum(self.parent.y_grid_size[self.row:self.row + self.row_span]))]


class WidgetV2:
    def __init__(self, parent):
        self.parent = parent
        self.children = []

        self.pos: None | list[int, int] = [0, 0]
        self.size: None | list[int, int] = [0, 0]

        # different typed of "padding"
        # format [padding to the left/top, padding to the right/bottom]
        self.pad_x: list[int, int] = [0, 0]
        self.pad_y: list[int, int] = [0, 0]
        self.border_x: list[int, int] = [0, 0]
        self.border_y: list[int, int] = [0, 0]
        self.ipad_x: list[int, int] = [0, 0]
        self.ipad_y: list[int, int] = [0, 0]

    # <editor-fold desc="size">
    @property
    def outer_size(self):
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
    def inner_size(self):
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
    def inner_pos(self):
        inner_pos = [
            self.pos[0] + sum((self.pad_x[0], self.border_x[0], self.ipad_x[0])),
            self.pos[1] + sum((self.pad_y[0], self.border_y[0], self.ipad_y[0]))
        ]

        return inner_pos

    @inner_pos.setter
    def inner_pos(self, value):
        self.pos = [
            value[0] - sum((self.pad_x[0], self.border_x[0], self.ipad_x[0])),
            value[1] - sum((self.pad_y[0], self.border_y[0], self.ipad_y[0]))
        ]
    # </editor-fold>

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

        sig, current_locals = inspect.signature(self.__init__), locals()
        kwargs = {param.name: current_locals[param.name] for param in sig.parameters.values()}

        for kwarg in kwargs.keys():
            if kwargs[kwarg] is not None:
                self.__setattr__(kwarg, kwargs[kwarg])

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


class Grid(Widget):
    def __init__(self, parent, *,
                 show: bool = True,
                 **kwargs):

        # gets all arguments and passes them on to super class
        sig, current_locals = inspect.signature(self.__init__), locals()
        args = {param.name: current_locals[param.name] for param in sig.parameters.values()}
        super().__init__(**args)

        self.x_grid_size: list[float] = []
        self.y_grid_size: list[float] = []

        self.min_cell_size: list[int, int] = [0, 0]
        self.children: list[GridCell] = []

        self.grid_changed = False

    def update_grid(self):
        max_row = max(self.children, key=lambda x: x.row + x.row_span)
        max_row_index = max_row.row + max_row.row_span
        self.x_grid_size = [self.min_size[0] for _ in range(max_row_index)]
        for child in self.children:
            for i in range(child.row, child.row + child.row_span):
                self.x_grid_size[i] = max(self.x_grid_size[i], child.min_size[0])

        max_column = max(self.children, key=lambda x: x.column + x.column_span)
        max_column_index = max_column.column + max_column.column_span
        self.x_grid_size = [self.min_cell_size[1] for _ in range(max_column_index)]
        for child in self.children:
            for i in range(child.column, child.column + child.column_span):
                self.x_grid_size[i] = max(self.x_grid_size[i], child.min_size[1])

    def construct_cell(self,
                       row: int,
                       column: int,
                       row_span: int = 1,
                       column_span: int = 1):

        grid_part = GridCell(self,
                             row=row,
                             column=column,
                             row_span=row_span,
                             column_span=column_span)

        self.children.append(grid_part)

        return grid_part
