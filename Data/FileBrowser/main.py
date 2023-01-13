# todo might want to add option to delete book/chapter/part from file browser
import tkinter as tk

from Data.FileBrowser.Parts import Head, ContainerPart, NewFilePart, DataPart


def add_chapter(handler):
    if isinstance(handler.focused, ContainerPart):
        NewFilePart(handler.focused, ContainerPart)


def add_part(handler):
    if isinstance(handler.focused, ContainerPart):
        NewFilePart(handler.focused, DataPart)


def add_files_button_setup(root, handler):
    root.update_idletasks()
    w = root.winfo_width()
    h = root.winfo_height()

    translate = tk.Button(root, text='add part', command=lambda: add_part(handler))
    translate.place(x=w-5, y=h-35, anchor=tk.SE)

    memory = tk.Button(root, text='add chapter', command=lambda: add_chapter(handler))
    memory.place(x=w-5, y=h-5, anchor=tk.SE)


def manual_close_window():
    global return_func

    def false_return():
        return False

    return_func = false_return


def ask_for_files():
    global return_func

    root = tk.Tk()
    root.geometry("300x300")
    root.title('select file(s) (return)')

    handler = Head(root, multiple=True)
    handler.make_structure()
    handler.place_all()

    return_func = handler.get_data_files
    root.protocol("WM_DELETE_WINDOW", manual_close_window)
    root.mainloop()

    return return_func()


def ask_for_file():
    root = tk.Tk()
    root.geometry("300x300")
    root.title('select file (middle click)')

    handler = Head(root, multiple=False)
    handler.make_structure()
    handler.place_all()

    add_files_button_setup(root, handler)
    root.mainloop()

    return handler.focused.file


if __name__ == "__main__":
    print(ask_for_file())
