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


class Template:
    def __init__(self, *args, **kwargs):
        self.pos: list[int, int] = [0, 0]
        self.size: list[int, int] = [0, 0]

        self.fill = False

    @property
    def corner_pos(self):
        """
        self.pos + self.size
        """
        return matrix_add(self.pos + self.size)

    @abstractmethod
    def update_min_size(self, changed):
        pass


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


class BasicContainer(Template):
    def __init__(self, parent, *args, **kwargs):
        """
        :param parent: container self is contained by
        :param kwargs:
        """
        super().__init__(kwargs)

        self.handler = None

        self.show = True

        self.min_size: list[int, int] = [0, 0]

        self.parent = parent
        self.children: list = []

    def update_min_size(self, changed: Template):
        self.min_size = matrix_map(max, [child.corner_pos for child in self.children])

        self.parent.update_size(self)

    def update_pos(self):
        pass

    def update_size(self):
        pass

    def draw_recursion(self, pos, surface):
        """
        :param pos: the absolute pos of self
        :param surface:
        """
        if self.show:
            for child in self.children:
                child.draw_recursion(matrix_add(pos, child.pos), surface)


class Widget:
    def __init__(self, parent, *args,
                 x: None | int = 0,
                 y: None | int = 0,
                 rel_x: None | float = 0,
                 rel_y: None | float = 0,

                 pad_x: list[int, int] = (0, 0),
                 pad_y: list[int, int] = (0, 0),
                 ipad_x: list[int, int] = (0, 0),
                 ipad_y: list[int, int] = (0, 0),

                 size: list[int, int] = (0, 0),
                 fill: bool = False,
                 fit: bool = False,

                 show: bool = True,
                 ):

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

    def update_min_size(self, changed: Template):
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
        if self.rel_x is not None:
            self.pos[0] = (self.parent.size[0] - self.size[0]) * self.rel_x + self.size[0] // 2
        else:
            self.pos[0] = self.x

        if self.rel_y is not None:
            self.pos[1] = (self.parent.size[1] - self.size[1]) * self.rel_y + self.size[0] // 2
        else:
            self.pos[1] = self.y

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


class NewContainer(Widget):
    def __init__(self, parent, *args,
                 x: None | int = 0,
                 y: None | int = 0,
                 rel_x: None | float = 0,
                 rel_y: None | float = 0,

                 pad_x: list[int, int] = (0, 0),
                 pad_y: list[int, int] = (0, 0),
                 ipad_x: list[int, int] = (0, 0),
                 ipad_y: list[int, int] = (0, 0),

                 size: list[int, int] = (0, 0),
                 fill: bool = False,
                 fit: bool = False,

                 show: bool = True,
                 **kwargs):

        super().__init__(parent, args, kwargs)



# class PadContainer(BasicContainer):
#     def __init__(self, parent, *args,
#                  pad_x: list[int, int] = (int, int),
#                  pad_y: list[int, int] = (int, int),
#                  **kwargs):
#
#         super().__init__(parent, args, kwargs)
#
#         self.pad_x = pad_x
#         self.pad_y = pad_y
#
#         self.pad_container = BasicContainer(parent)
#
#         self.pad_container.pos =
#
#         self.children = PointerVar("children", self.pad_container)
#
#
#
# class IpadContainer(PadContainer):
#     def __init__(self, parent, *args,
#                  ipad_x: list[int, int] = (int, int),
#                  ipad_y: list[int, int] = (int, int),
#                  **kwargs):
#
#         super().__init__(parent, args, kwargs)
#
#         self.ipad_x = ipad_x
#         self.ipad_y = ipad_y



class Container(BasicContainer):
    def __init__(self, parent, *,
                 rel_x: float = 0,
                 rel_y: float = 0,
                 pad_x: list[int, int] = (int, int),
                 pad_y: list[int, int] = (int, int),
                 ipad_x: list[int, int] = (int, int),
                 ipad_y: list[int, int] = (int, int),
                 **kwargs):

        super().__init__(kwargs)

        self.rel_x = rel_x
        self.rel_y = rel_y

        self.pad_x = pad_x
        self.pad_y = pad_y

        self.ipad_x = ipad_x
        self.ipad_y = ipad_y

        self.anchor_container = BasicContainer(parent)
        self.anchor_container.pos = PointerVar("pos", self)

        # place anchor_container
        self.pad_container = BasicContainer(self.anchor_container)
        # place pad_container
        self.ipad_container = BasicContainer(self.pad_container)
        # place ipad_container

        self.geometry_manager: Literal["place", "grid", None] = None

    def temp_name(self, x, y):
        bounding_box = [(self.parent.size[0] - self.size[0]) * x + self.size[0] // 2,
                        (self.parent.size[1] - self.size[1]) * y + self.size[0] // 2]

    def update_min_size(self, changed: Template, update_parent=True):
        self.min_size = matrix_map(max, [child.corner_pos for child in self.children])
        if update_parent:
            self.parent.update_size(self)

    def set_geometry_manager(self, to):
        if self.geometry_manager is None:
            self.geometry_manager = to
            return

        if self.geometry_manager != to:
            raise f"Can't use multiple geometry managers in one container"

    def place(self, *, _):
        self.set_geometry_manager("place")

    # def pack(self, *, _):
    #     self.set_geometry_manager("pack")

    def grid(self, *, _):
        self.set_geometry_manager("grid")


