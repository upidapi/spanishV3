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


class PointerVar:
    def __init__(self, value, handler):
        """
        :param handler: where to search for PointerVars
        :param value: what to search for
        """

        self.value = value
        self.handler = handler

    def __getattribute__(self, item):
        return object.__getattribute__(self.handler, self.value)


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


# class Container(Widget):
#     def __init__(self, parent, *,
#                  show: bool = True):
#
#         # gets all arguments and passes them on to super class
#         sig, current_locals = inspect.signature(self.__init__), locals()
#         args = {param.name: current_locals[param.name] for param in sig.parameters.values()}
#         super().__init__(**args)
#
#         self.children = []
#
#         self.geometry_manager: Literal["place", "grid", None] = None
#
#         self.grid_values = {}
#         self.x_grid_list = []
#         self.y_grid_list = []
#
#     def set_geometry_manager(self, to):
#         if self.geometry_manager is None:
#             self.geometry_manager = to
#             return
#
#         if self.geometry_manager != to:
#             raise f"Can't use multiple geometry managers in one container"
#
#     def place(self, *, _):
#         self.set_geometry_manager("place")
#
#     def grid(self, child, *, row, column, row_span=1, column_span=1):
#         self.children.append(child)
#         self.grid_values[child] = {row, column}
#         self.set_geometry_manager("grid")


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
