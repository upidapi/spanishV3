import inspect
from abc import abstractmethod
from typing import Literal


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
                 x: None | int = 0,
                 y: None | int = 0,
                 rel_x: None | float = 0,
                 rel_y: None | float = 0,

                 pad_x: list[int, int] = (0, 0),
                 pad_y: list[int, int] = (0, 0),
                 ipad_x: list[int, int] = (0, 0),
                 ipad_y: list[int, int] = (0, 0),

                 min_size: list[int, int] = None,
                 size: list[int, int] = (0, 0),
                 max_size: list[int, int] = None,
                 fill: bool = False,
                 fit: bool = False,

                 show: bool = True,
                 **kwargs):

        self.parent = parent
        self.children: list = []

        self.show: bool = show

        # <editor-fold desc="pos">
        if x is None and rel_x is None:
            raise TypeError("no x pos found")

        if x and rel_x:
            raise TypeError("multiple x pos found")

        if y is None and rel_y is None:
            raise TypeError("no y pos found")

        if y and rel_y:
            raise TypeError("multiple y pos found")

        self.x: int = x
        self.y: int = y
        self.rel_x: float = rel_x
        self.rel_y: float = rel_y
        # </editor-fold>

        # <editor-fold desc="padding">
        self.pad_x: list[int, int] = pad_x
        self.pad_y: list[int, int] = pad_y
        self.ipad_x: list[int, int] = ipad_x
        self.ipad_y: list[int, int] = ipad_y
        # </editor-fold>

        # <editor-fold desc="size">
        self.min_size: list[int, int] = [0, 0]

        self.internal_size: list[int, int] = [0, 0]
        self.size: list[int, int] = size
        self.external_size: list[int, int] = [0, 0]

        # make self fill parent
        self.fill: bool = fill
        # make self contract around min_size
        self.fit: bool = fit

        temp = self.fill + self.fit + bool(self.size)
        if temp > 1:
            used = {'fill' if self.fill else ''}, {'fit' if self.fill else ''}, {'size' if self.fill else ''}
            used = ", ".join(used[:-1]) + " and " + used[-1]
            raise TypeError(f"Can't use multiple size managers ({used})")
        if temp == 0:
            raise TypeError("No size controller found")
        # </editor-fold>

    def place(self,
              x: None | int = 0,
              y: None | int = 0,
              rel_x: None | float = 0,
              rel_y: None | float = 0,

              pad_x: list[int, int] = (0, 0),
              pad_y: list[int, int] = (0, 0),
              ipad_x: list[int, int] = (0, 0),
              ipad_y: list[int, int] = (0, 0),

              min_size: list[int, int] = None,
              size: list[int, int] = (0, 0),
              max_size: list[int, int] = None,
              fill: bool = False,
              fit: bool = False):

        # <editor-fold desc="pos">
        if x is None and rel_x is None:
            raise TypeError("no x pos found")

        if x and rel_x:
            raise TypeError("multiple x pos found")

        if y is None and rel_y is None:
            raise TypeError("no y pos found")

        if y and rel_y:
            raise TypeError("multiple y pos found")

        self.x: int = x
        self.y: int = y
        self.rel_x: float = rel_x
        self.rel_y: float = rel_y
        # </editor-fold>

        # <editor-fold desc="padding">
        self.pad_x: list[int, int] = pad_x
        self.pad_y: list[int, int] = pad_y
        self.ipad_x: list[int, int] = ipad_x
        self.ipad_y: list[int, int] = ipad_y
        # </editor-fold>

        # <editor-fold desc="size">
        self.min_size: list[int, int] = [0, 0]

        self.internal_size: list[int, int] = [0, 0]
        self.size: list[int, int] = size
        self.external_size: list[int, int] = [0, 0]

        # make self fill parent
        self.fill: bool = fill
        # make self contract around min_size
        self.fit: bool = fit

        temp = self.fill + self.fit + bool(self.size)
        if temp > 1:
            used = {'fill' if self.fill else ''}, {'fit' if self.fill else ''}, {'size' if self.fill else ''}
            used = ", ".join(used[:-1]) + " and " + used[-1]
            raise TypeError(f"Can't use multiple size managers ({used})")
        if temp == 0:
            raise TypeError("No size controller found")
        # </editor-fold>



    def update_min_size(self, changed):
        self.min_size = matrix_map(max, [child.corner_pos for child in self.children])

        self.parent.update_min_size(self)

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


class Container(Widget):
    class Square:
        def __init__(self,
                     row,
                     column,
                     row_span=1,
                     column_span=1):

            self.row = row
            self.column = column
            self.row_span = row_span
            self.column_span = column_span

    def __init__(self, parent, *,
                 x: None | int = 0,
                 y: None | int = 0,
                 rel_x: None | float = 0,
                 rel_y: None | float = 0,

                 pad_x: list[int, int] = (0, 0),
                 pad_y: list[int, int] = (0, 0),
                 ipad_x: list[int, int] = (0, 0),
                 ipad_y: list[int, int] = (0, 0),

                 min_size: list[int, int] = None,
                 size: list[int, int] = (0, 0),
                 max_size: list[int, int] = None,
                 fill: bool = False,
                 fit: bool = False,

                 show: bool = True):

        # gets all arguments and passes them on to super class
        sig, current_locals = inspect.signature(self.__init__), locals()
        args = {param.name: current_locals[param.name] for param in sig.parameters.values()}
        super().__init__(**args)

        self.children = []

        self.geometry_manager: Literal["place", "grid", None] = None

        self.grid_values = {}
        self.x_grid_list = []
        self.y_grid_list = []

    def set_geometry_manager(self, to):
        if self.geometry_manager is None:
            self.geometry_manager = to
            return

        if self.geometry_manager != to:
            raise f"Can't use multiple geometry managers in one container"

    def place(self, *, _):
        self.set_geometry_manager("place")

    def grid(self, child, *, row, column, row_span=1, column_span=1):
        self.children.append(child)
        self.grid_values[child] = {row, column}
        self.set_geometry_manager("grid")


class Grid(Widget):
    def __init__(self, parent, *,
                 x: None | int = 0,
                 y: None | int = 0,
                 rel_x: None | float = 0,
                 rel_y: None | float = 0,

                 pad_x: list[int, int] = (0, 0),
                 pad_y: list[int, int] = (0, 0),
                 ipad_x: list[int, int] = (0, 0),
                 ipad_y: list[int, int] = (0, 0),

                 min_size: list[int, int] = None,
                 size: list[int, int] = (0, 0),
                 max_size: list[int, int] = None,
                 fill: bool = False,
                 fit: bool = False,

                 show: bool = True,
                 **kwargs):

        # gets all arguments and passes them on to super class
        sig, current_locals = inspect.signature(self.__init__), locals()
        args = {param.name: current_locals[param.name] for param in sig.parameters.values()}
        super().__init__(**args)

        self.rect_s = []

        self.x_grid_size = []
        self.y_grid_size = []

        self.children = []

    def grid(self,
             row,
             column,
             row_span=1,
             column_span=1):

        self.rect_s.append()
