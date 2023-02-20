import tkinter as tk
import os
import pathlib


def get_im_dirs(root_dir):
    sub_dirs = []
    for file in os.listdir(root_dir):
        d = os.path.join(root_dir, file)
        sub_dirs.append(d)
    return sub_dirs


class SuperPart:
    def __init__(self, parent, file):
        self.file = file
        self.indent_width = 0

        self.children = []
        self.parent = parent
        self.show_children = False
        self.selected = False

        if self.parent is None:
            self.handler = self
        else:
            self.handler = self.parent.handler
            self.parent.children.append(self)

            text = os.path.basename(os.path.normpath(file))
            self.bar = tk.Button(self.handler.root,
                                 text=text,
                                 command=self.hide)
            # noinspection PyUnresolvedReferences
            if self.handler.multiple:  # the last in line is the handler
                # if you're allowed to select multiple make selection possible (right-click)
                self.bar.bind("<Button-3>", self.select)
            else:
                # if you're only allowed to select one bind selection button to middle-click
                def return_file(_):
                    self.focus()
                    self.handler.root.destroy()

                self.bar.bind("<Button-2>", return_file)

    @property
    def raw_name(self):
        """
        :return: the parents children (siblings)
        """
        return os.path.basename(os.path.normpath(self.file))

    @property
    def siblings(self):
        """
        :return: the parents children (siblings)
        """
        if self.parent is None:
            return []
        else:
            return self.parent.children

    @property
    def super_parents(self):
        """
        :return: all parents (including self at index 0)
        """
        if self.parent is None:
            return []
        else:
            return [self] + self.parent.super_parents

    @property
    def super_children(self):
        """
        :return: all children (including self at index 0)
        """
        children_below = [self]
        for child in self.children:
            children_below += child.super_children
        return children_below

    @property
    def shown_children(self):
        """
        :return: the shown children (and theirs recursively)
        """
        children_below = [self]
        if self.show_children:
            for child in self.children:
                children_below += child.shown_children
        return children_below

    def get_total_indentation(self):
        """
        :return: the total indentation of self and parents
        """
        total_indentation = 0
        for parent in self.super_parents:
            total_indentation += parent.indent_width
        return total_indentation

    def get_total_index(self):
        """
        :return: the total amount of shown parts before self
        """
        to_parent = 0
        for sibling_before in self.siblings:
            if sibling_before == self:
                break

            to_parent += len(sibling_before.shown_children)

        if self.parent is None:
            return to_parent
        else:
            return to_parent + self.parent.get_total_index() + 1

    # high level functions
    def set_color(self):
        if self.handler.focused == self:
            color = "#ff00ff"
        elif self.selected:
            color = "#c0c0c0"
        else:
            color = "#f0f0f0"

        self.bar.config(background=color)

    def place(self):
        """
        places self att right position
        """
        if self.parent.show_children:
            height = 30
            x = self.get_total_indentation()
            y = self.get_total_index() * height

            self.bar.place(x=x, y=y)
        else:
            self.bar.place_forget()

    def focus(self):
        """
        sets focus to self
        """
        old_focus = self.handler.focused
        self.handler.focused = self

        if old_focus:
            old_focus.set_color()

        if self is not None:
            self.handler.focused = self
            self.set_color()

    def hide(self):
        """
        (un)hides all children
        """
        if self.show_children:
            for child in self.super_children:
                child.show_children = False
        else:
            self.show_children = True

        self.focus()
        self.handler.place_all()

    def select(self, _):
        """
        (un)selects all children
        """
        change_to = not self.selected
        for child in self.super_children:
            child.selected = change_to
            child.set_color()


class DataPart(SuperPart):
    """
    The last part in the line containing the file (with the data)
    """
    def __init__(self, parent, file):
        super().__init__(parent, file)

        self.indent_width = 20


class ContainerPart(SuperPart):
    """
    Contains ContainerPart(s) / DataPart(s)
    """
    def __init__(self, parent, file):
        super().__init__(parent, file)

        self.indent_width = 20
        self.drop_down_show()

    def drop_down_show(self):
        drop_symbol = {True: '˅', False: '˃'}[self.show_children]
        self.bar.config(text=f"{drop_symbol} {self.raw_name}")

    def hide(self):
        """
        (un)hides all children
        """
        if self.show_children:
            for child in self.super_children:
                child.show_children = False
        else:
            self.show_children = True

        self.drop_down_show()
        self.focus()
        self.handler.place_all()

    def make_structure(self):
        for path in get_im_dirs(self.file):
            if path.endswith(".json"):
                DataPart(self, path)
            else:
                ContainerPart(self, path).make_structure()


class NewFilePart(SuperPart):
    def __init__(self, parent, part_type):
        # make this file
        file = os.path.join(parent.file, 'temp_name')
        # os.mkdir(file)

        super().__init__(parent, file)

        self.indent_width = 20
        self.part_type = part_type

        # makes the bar an entry instead
        del self.bar
        self.bar = tk.Entry(self.handler.root)

        self.bar.bind('<Escape>', self.save_file)
        self.bar.bind('<FocusOut>', self.save_file)
        self.bar.bind('<Delete>', self.un_focus)

        self.focus()
        self.parent.show_children = True
        self.handler.place_all()
        self.bar.focus()

    def del_references(self):
        self.parent.children.remove(self)
        self.bar.destroy()
        self.handler.place_all()

    def un_focus(self, _=None):
        self.parent.focused_entry()
        self.del_references()

    def save_file(self, _):
        parent_path = os.path.abspath(self.parent.file)

        file_name = self.bar.get()

        if self.part_type is DataPart:
            # file_name = file_name.replace(' ', '_')
            file_name += '.json'

        file_path = os.path.join(parent_path, file_name)

        if file_name in os.listdir(parent_path) or file_name.strip(' ') == '':
            self.un_focus()
        else:
            if self.part_type is not DataPart:
                os.mkdir(file_path)

            self.part_type(self.parent, file_path).focused_entry()
            self.del_references()


class BookPart(ContainerPart):
    """
    Is the handler / head of the parts (this is not shown)
    """

    def __init__(self, parent, file):
        super().__init__(parent, file)

    def get_data_files(self):
        config_file = os.path.join(self.file, 'config.json')
        data_parts = []
        for child in self.children:
            data_parts += child.super_children

        data_files = []
        for part in data_parts:
            if part.file.endswith(".json") and part.selected:
                data_files.append(part.file)

        return {"config_file": config_file, "data_files": data_files}

    def make_structure(self):
        for path in get_im_dirs(self.file):
            if not path.endswith('config.json'):
                if path.endswith('.json'):
                    ContainerPart(self, path)
                else:
                    ContainerPart(self, path).make_structure()


class Head(SuperPart):
    """
    Is the handler / head of the parts (this is not shown)
    """

    def __init__(self, root, multiple):
        self.focused = False
        self.root = root
        self.multiple = multiple

        file_path = pathlib.Path(__file__).resolve()
        books_path = file_path.parent.parent / 'DataFiles' / 'books'
        print(books_path)

        super().__init__(None, books_path)

        self.indent_width = 0
        self.show_children = True

        if self.multiple:
            self.handler.root.bind('<Return>', lambda _: self.handler.root.destroy())

    def place_all(self):
        for child in self.super_children[1:]:
            child.place()

    def get_data_files(self):
        book_path_files = []
        for book in self.children:
            # this is redundant the book is always an instance of BookPart
            if isinstance(book, BookPart):
                book_path_files.append(book.get_data_files())
                # book_data = book.get_data_files()
                # if len(book_data["data_files"]) == 0:
                #     book_path_files
            # if isinstance(book, ContainerPart):
            #     book_path_files.append(book.get_data_files())
            # if isinstance(book, DataPart):
            #     book_path_files.append(book.get_data_files())

        return book_path_files

    def make_structure(self):
        """
        makes a part structure depending on the structures of the files

        if file has a config.json file it becomes a BookPart
        elif file ends with .json it becomes a DataPart
        else it becomes a ContainerPert

        Structure:
        Head
            BookPart
                ContainerPart
                    DataPart
                    DataPart
                    DataPart

                ContainerPart
                    DataPart
            BookPart
                ...
        """

        for path in get_im_dirs(self.file):
            if 'config.json' in os.listdir(path):
                BookPart(self, path).make_structure()
            else:
                if path.endswith('.json'):
                    ContainerPart(self, path)
                else:
                    ContainerPart(self, path).make_structure()
