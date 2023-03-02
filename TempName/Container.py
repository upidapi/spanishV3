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


class BasicContainer(Template):
    def __init__(self, parent, **kwargs):
        super().__init__(kwargs)

        self.show = True

        self.min_size: list[int, int] = [0, 0]

        self.parent = parent
        self.children: list = []

    def update_min_size(self, changed: Template):
        self.min_size = matrix_map(max, [child.corner_pos for child in self.children])

        self.parent.update_size(self)

    def draw(self, pos, surface):
        """
        :param pos: the absolute pos of self
        :param surface:
        """
        if self.show:
            for child in self.children:
                child.draw(matrix_add(pos, child.pos), surface)


class Container(BasicContainer):
    def __init__(self, parent, **kwargs):
        super().__init__(kwargs)

        self.anchor_container = BasicContainer(parent)
        # place anchor_container
        self.pad_container = BasicContainer(self.anchor_container)
        # place pad_container
        self.ipad_container = BasicContainer(self.pad_container)
        # place ipad_container


        self.geometry_manager: Literal["place", "grid", None] = None

    def update_min_size(self, changed: Template):
        self.min_size = matrix_map(max, [child.corner_pos for child in self.children])

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
