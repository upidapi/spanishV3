import tkinter as tk

from FixRawInput.helper_funcs import get_mods
from FixRawInput import TrLines


class Data:
    # tkinter instances
    root: any
    tk_font: any
    tk_image: any
    overlay_image: any

    # declarations
    font_height: int
    bg_color = "#f0f0f0"
    languages: tuple

    # "global" vars
    switch = False
    show_entries = True
    mode = 0


def setup(root, tk_font, tk_image, languages):
    Data.root = root

    Data.tk_font = tk_font
    Data.tk_image = tk_image
    print(f"{Data.tk_font.actual()=}")

    Data.languages = languages

    # gets the height of the font
    widget = tk.Label(root, text="My String", font=tk_font)
    widget.pack()
    Data.font_height = tk.font.Font(font=widget['font']).metrics('linespace')
    widget.destroy()


class Handler:
    # helper funcs
    @staticmethod
    def find_focus():
        focus = Data.root.focus_get()
        for instance in TextEntry.instances:
            if instance.entry == focus:
                return instance

    # other
    @staticmethod
    def get_data():
        full_data = []
        # gets the New from all the instances
        for instance in TextEntry.instances:
            text_main = instance.tk_text.get()
            text_translation = instance.other_text

            raw_entry_data = instance.entry.place_info()
            x, y = raw_entry_data['x'], raw_entry_data['y']

            text_width = instance.get_width()

            if Data.switch:
                text_main, text_translation = text_translation, text_main

            data = {
                'self': instance,
                'text': {'main': text_main, 'translation': text_translation},
                'x': int(x),
                'y': int(y),
                'height': int(Data.font_height),
                'width': int(text_width),
            }

            full_data.append(data)

        return full_data

    @staticmethod
    def populate(data):
        for d1, d2 in zip(*data):
            text_1, text_2 = d1['text'], d2['text']
            x, y = d1['x'], d1['y']

            TextEntry(text=text_1, x=x, y=y, text_other=text_2)

    @staticmethod
    def hide(event, show):
        # hides the text by overlaying an identical image of the bg
        if 'ctrl' in get_mods(event) or show:
            if show:
                if not Data.show_entries:
                    Data.overlay_image.destroy()
                    Data.show_entries = True
            else:
                if Data.show_entries:
                    Data.overlay_image = tk.Label(Data.root, image=Data.tk_image)
                    w, h = Data.tk_image.width(), Data.tk_image.height()
                    Data.overlay_image.place(x=0, y=0, w=w, h=h)
                    Data.show_entries = False

    @staticmethod
    def update_tr_lines():
        TrLines.draw(Handler.get_data())

    @staticmethod
    def switch_text(event):
        # when it goes to mode 1 the text gets combined (saved_text == other_text)
        if Data.mode == 0:
            if 'ctrl' in get_mods(event):
                if Data.switch:
                    Data.switch = False
                    Data.root.title(f'split/move/add/delete words (lan: {Data.languages[0]})')
                else:
                    Data.switch = True
                    Data.root.title(f'split/move/add/delete words (lan: {Data.languages[1]})')

                # switches the text and other_text for all instances
                for instance in TextEntry.instances:
                    text_main = instance.saved_text
                    text_switch = instance.other_text

                    instance.tk_text.set(text_switch)
                    instance.saved_text = text_switch
                    instance.other_text = text_main

                    instance.update_hit_box(2)

            Handler.update_tr_lines()

    # affects only a few
    @staticmethod
    def new_word():
        x, y = Data.root.winfo_pointerxy()
        x -= Data.root.winfo_rootx()
        y -= Data.root.winfo_rooty()
        y -= Data.font_height // 2

        TextEntry(text='', x=x, y=y, allow_write=True)

        Handler.update_tr_lines()

    @staticmethod
    def move(_):
        self = Handler.find_focus()

        if self is not None:
            x, y = Data.root.winfo_pointerxy()
            x -= Data.root.winfo_rootx()
            y -= Data.root.winfo_rooty()
            y -= Data.font_height // 2

            if 0 <= x and 0 <= y:
                entry_data = self.entry.place_info()

                self.entry.grid_forget()
                self.entry.place(x=x, y=y, width=entry_data['width'])

        Handler.update_tr_lines()

    @staticmethod
    def merge(event):
        if 'ctrl' in get_mods(event):
            selected_widget = Handler.find_focus()

            over_widget = None
            x, y = Data.root.winfo_pointerxy()
            widget = Data.root.winfo_containing(x, y)
            for instance in TextEntry.instances:
                if instance.entry == widget:
                    over_widget = instance
                    break

            if selected_widget != over_widget and over_widget is not None and selected_widget is not None:
                selected_widget.save()

                selected_widget.saved_text += over_widget.saved_text
                selected_widget.other_text += over_widget.other_text
                selected_widget.tk_text.set(selected_widget.saved_text)

                over_widget.delete_instance()
                selected_widget.save()

        Handler.update_tr_lines()


class TextEntry:
    instances = []

    # helper funcs
    def get_width(self, tolerance=11):
        text = self.tk_text.get()
        # print(f"text: {text}, Width: {Data.tk_font.measure(text)}")
        return Data.tk_font.measure(text) + tolerance

    # call funcs
    def on_key_press(self, event):
        other = ['BackSpace', 'Delete', 'Control_L']
        combined_char = ['\x04']

        if Data.mode == 0 and not self.allow_write:
            # # for example ctrl + W => \x17
            # combined_unicode = event.char != event.keysym and len(event.keysym) == 1

            combined_char_exception = event.char in combined_char

            # some things just don't get captured, this ia a quick fix
            exception = event.keysym in other

            # checks if it's a normal character (abc, 123, !?\, etc)
            normal_character = event.char.isprintable() and event.char != ''

            if combined_char_exception or exception or normal_character:
                return 'break'

            self.update_hit_box(2)

        elif self.entry == Data.root.focus_get():
            self.update_hit_box(11)

    def custom_bind(self, key, func: callable = None, do_extra: callable = None, mod=None):
        # used to ease the proses of binding things

        def combined_funcs(event):
            if mod in get_mods(event) or mod is None:
                if func is not None:
                    func()

            if do_extra is not None:
                do_extra()

            return self.on_key_press(event)

        self.entry.bind(key, lambda event: combined_funcs(event))

    def delete_instance(self):
        self.entry.destroy()
        TextEntry.instances.remove(self)

        Handler.update_tr_lines()

    def update_hit_box(self, tolerance):
        width = self.get_width(tolerance)
        entry_data = self.entry.place_info()

        self.entry.grid_forget()
        self.entry.place(x=entry_data['x'], y=entry_data['y'], width=width)

    def revert_changes(self):
        """
        reverts all changes on the text entry
        """
        # Remove changes
        self.tk_text.set(self.saved_text)

        x, y = self.saved_pos
        width = self.get_width(2)

        self.entry.grid_forget()
        self.entry.place(x=x, y=y, width=width)

        Handler.update_tr_lines()

    def un_focus(self):
        """
        does all things that have to be done when you un focus
        """
        self.allow_write = False

        self.entry.config(fg='#000000')

        # if its empty delete it
        if self.saved_text == "":
            self.delete_instance()

        else:
            self.revert_changes()

    def save(self):
        """
        saves the entry New
        """
        text = self.tk_text.get().strip()
        self.saved_text = text

        if self.allow_write:
            self.other_text = self.saved_text

        entry_data = self.entry.place_info()
        x, y = entry_data['x'], entry_data['y']
        width = self.get_width(2)

        self.saved_pos = (x, y)

        self.entry.grid_forget()
        self.entry.place(x=x, y=y, width=width)

    def split(self):
        cursor_pos = self.entry.index(tk.INSERT)

        text_main, text_translation = self.tk_text.get(), self.other_text
        if Data.switch:
            text_main, text_translation = text_translation, text_main

        bef_cursor = text_main[:cursor_pos]
        aft_cursor = text_translation[cursor_pos:]

        self.tk_text.set(bef_cursor)
        self.other_text = bef_cursor
        self.save()
        self.un_focus()

        x = int(self.entry.place_info()['width']) + 5 + int(self.saved_pos[0])  # the 5 is to shift it a bit
        y = int(self.saved_pos[1])
        split_text = TextEntry(text=aft_cursor, x=x, y=y, allow_write=True)
        split_text.save()
        split_text.un_focus()

    def __init__(self, *, text, x, y, text_other=None, allow_write=False):
        TextEntry.instances.append(self)

        self.allow_write = allow_write
        self.saved_pos = (x, y)
        self.saved_text = text
        self.tk_text = tk.StringVar(Data.root, text)

        if text_other is None:
            self.other_text = text
        else:
            self.other_text = text_other

        self.entry = tk.Entry(
            Data.root,
            readonlybackground=Data.bg_color,
            bg=Data.bg_color,
            borderwidth=0,
            highlightthickness=0,
            textvariable=self.tk_text,
            font=('DejaVu Sans Mono', 10)
            # todo fix this (by using the var tk_font instead somehow)
            # for some reason when multiple tk.Tk() instances exist the family argument on a font doesn't change family
        )

        self.entry.place(x=x, y=y)
        self.entry.focus()
        self.update_hit_box(2)

        # binds things
        self.custom_bind('s', self.split, mod='ctrl')
        self.custom_bind('<Delete>', self.delete_instance, do_extra=Data.root.focused_entry)
        self.custom_bind('<Return>', self.save, do_extra=Data.root.focused_entry)
        self.custom_bind('<Escape>', self.revert_changes, do_extra=Data.root.focused_entry)

        self.custom_bind('<KeyRelease>')
        self.custom_bind('<KeyPress>')

        self.custom_bind('<FocusOut>', self.un_focus)
        self.custom_bind('<FocusIn>', lambda: self.entry.config(fg='#ff0000'))
