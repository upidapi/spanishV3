from abc import abstractmethod


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

    @property
    def corner_pos(self):
        """
        self.pos + self.size
        """
        return matrix_add(self.pos + self.size)

    @abstractmethod
    def update_min_size(self, changed):
        pass


class Container(Template):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)

        self.show = True

        self.min_size: list[int, int] = [0, 0]

        self.parent = None
        self.children: list = []

        # @property
    # def parents(self):
    #     """
    #     returns all the parents of self
    #     """
    #
    #     return self.parent + self.parents()
    #
    # def abs_pos(self):
    #     return matrix_add(*[parent.pos for parent in [self, *self.parents]])

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

