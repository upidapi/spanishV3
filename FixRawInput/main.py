import tkinter as tk
from tkinter import font
from PIL import ImageTk, Image

from FixRawInput import TrLines
from FixRawInput import Mode
from FixRawInput import CustomEntery
from FixRawInput.CustomEntery import Handler
from Data import load_raw_data


def get_tk_image(root):
    # background image
    path = r'../Data/DataFiles/selected_image.jpg'
    raw_img = Image.open(path)
    tk_image = ImageTk.PhotoImage(raw_img, master=root)
    return tk_image


def get_canvas(root, tk_image):
    w = tk_image.width()
    h = tk_image.height()

    canvas = tk.Canvas(root, bd=0, highlightthickness=0)
    canvas.place(x=0, y=0, width=w, height=h)

    return canvas


def entries_setup(root, data):
    # adds all the enters
    Handler.populate(data)
    # to prevent the last added entry from being focused
    root.focus()
    Handler.update_tr_lines()
    # binds

    root.bind('<Button-3>', lambda event: Handler.move(event))
    root.bind('<Button-2>', lambda event: Handler.new_word())
    root.bind('<Return>', lambda event: Mode.next_mode(event))
    root.bind('<q>', lambda event: Handler.merge(event))
    root.bind('<w>', lambda event: Handler.switch_text(event))

    root.bind('<e>', lambda event: Handler.hide(event, False))
    root.bind('<KeyRelease-e>', lambda event: Handler.hide(event, True))


def __init__(languishes=('spa', 'swe')):
    data = load_raw_data()

    root = tk.Tk()

    tk_font = font.Font(family='DejaVu Sans Mono', size=10)

    tk_image = get_tk_image(root)
    canvas = get_canvas(root, tk_image)

    root.geometry(f"{tk_image.width()}x{tk_image.height()}")

    canvas.create_image(tk_image.width()//2,
                        tk_image.height()//2,
                        image=tk_image)  # the x and y is the center apparently

    CustomEntery.setup(root, tk_font, tk_image, languages=languishes)
    TrLines.__init__(global_canvas=canvas, global_tk_image=tk_image)
    Mode.__init__(root, global_languages=languishes)

    entries_setup(root, data)
    root.mainloop()


# todo add the ability to scroll on the image or resize the image based om screen height
if __name__ == '__main__':
    __init__()

