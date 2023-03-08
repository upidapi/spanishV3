from __future__ import annotations

from TempName.Widget import Widget


# todo needs to be updated according to the new Widget implementation

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
