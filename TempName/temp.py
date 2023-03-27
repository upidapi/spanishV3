import pyglet
import sys


class TextWidget:
    default_bg_colour = (200, 200, 220)
    default_text_colour = (0, 0, 0, 255)

    def __init__(self, text, x, y, batch):
        self.batch = batch

        # <editor-fold desc="init sub parts">
        self.document = pyglet.text.document.UnformattedDocument(text)
        self.document.set_style(0, len(self.document.text),
                                dict(color=TextWidget.default_text_colour))
        font = self.document.get_font()

        height = font.ascent - font.descent
        self.layout = pyglet.text.layout.IncrementalTextLayout(
            self.document, sys.maxsize, height, batch=self.batch)
        self.layout.position = x, y, 0

        self.caret = pyglet.text.caret.Caret(self.layout, batch=self.batch)
        # Rectangular outline
        self.rectangle = pyglet.shapes.Rectangle(
            x, y, 0, height,
            TextWidget.default_bg_colour,
            self.batch)
        # </editor-fold>

        self.update_width()

    @property
    def bg_colour(self):
        return self.rectangle.color

    @bg_colour.setter
    def bg_colour(self, color):
        self.rectangle.color = color

    @property
    def height(self):
        return self.rectangle.height

    def draw(self):
        self.batch.draw()

    @property
    def pos(self):
        return self.layout.x, self.layout.y

    def move(self, x, y):
        self.layout.x = x
        self.layout.y = y

        self.rectangle.x = x
        self.rectangle.y = y

    def update_width(self):
        width = self.layout.lines[0].width
        self.rectangle.width = width

    def hit_test(self, x, y):
        return (0 < x - self.layout.x < self.layout.width and
                0 < y - self.layout.y < self.layout.height)

    def delete(self):
        self.rectangle.delete()
        self.caret.delete()
        self.layout.delete()


class Window(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(400, 140, caption='Text entry', *args, **kwargs)

        self.batch = pyglet.graphics.Batch()
        self.labels = [
            pyglet.text.Label('Name', x=10, y=100, anchor_y='bottom',
                              color=(0, 0, 0, 255), batch=self.batch),
            pyglet.text.Label('Species', x=10, y=60, anchor_y='bottom',
                              color=(0, 0, 0, 255), batch=self.batch),
            pyglet.text.Label('Special abilities', x=10, y=20,
                              anchor_y='bottom', color=(0, 0, 0, 255),
                              batch=self.batch)
        ]

        self.widgets = [TextWidget('This is a test', 200, 100, self.batch)]

        self.text_cursor = self.get_system_mouse_cursor('text')

        self.d_drag = (0, 0)
        self.dragging = None

        self.focus = None
        self.set_focus(self.widgets[0])

    def on_resize(self, width, height):
        super(Window, self).on_resize(width, height)
        for widget in self.widgets:
            widget.width = width - 110

    def on_draw(self):
        pyglet.gl.glClearColor(1, 1, 1, 1)
        self.clear()
        self.batch.draw()
        # for widget in self.widgets:
        #     widget.draw()

    def get_clicked_widget(self, x, y):
        for widget in self.widgets:
            if widget.hit_test(x, y):
                return widget

    def on_mouse_motion(self, x, y, dx, dy):
        clicked_widget = self.get_clicked_widget(x, y)
        if clicked_widget is None:
            self.set_mouse_cursor(None)
        else:
            self.set_mouse_cursor(self.text_cursor)

    def on_mouse_release(self, x, y, button, modifiers):
        self.dragging = None

    def delete_widget(self, widget):
        self.widgets.remove(widget)
        widget.delete()

    def place_new_text_widget(self, x, y):
        new_widget = TextWidget("", x, y, self.batch)

        # move to center
        w_x, w_y = new_widget.pos
        w_y -= new_widget.height
        new_widget.move(w_x, w_y)

        self.set_focus(new_widget)

    def on_mouse_press(self, x, y, button, modifiers):
        clicked_widget = self.get_clicked_widget(x, y)

        if button == 1:  # left click
            if clicked_widget is None:
                self.set_focus(None)
            else:
                self.set_focus(clicked_widget)

            if self.focus:
                self.focus.caret.on_mouse_press(x, y, button, modifiers)

        elif button == 2: # middle click
            if clicked_widget is None:
                self.place_new_text_widget(x, y)
            else:
                self.delete_widget(clicked_widget)

        elif button == 4:  # right click
            # start drag
            self.dragging = clicked_widget

            if self.dragging is not None:
                pos = self.dragging.pos
                self.d_drag = pos[0] - x, pos[1] - y

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.dragging is not None:

            self.dragging.move(
                self.d_drag[0] + x,
                self.d_drag[1] + y)

        elif self.focus:
            self.focus.caret.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

    def on_text(self, text):
        if self.focus:
            self.focus.caret.on_text(text)
            self.focus.update_width()

    def on_text_motion(self, motion):
        if self.focus:
            self.focus.caret.on_text_motion(motion)
            self.focus.update_width()

    def on_text_motion_select(self, motion):
        if self.focus:
            self.focus.caret.on_text_motion_select(motion)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.TAB:
            if modifiers & pyglet.window.key.MOD_SHIFT:
                direction = -1
            else:
                direction = 1

            if self.focus in self.widgets:
                i = self.widgets.index(self.focus)
            else:
                i = 0
                direction = 0

            self.set_focus(self.widgets[(i + direction) % len(self.widgets)])

        elif symbol == pyglet.window.key.ESCAPE:
            pyglet.app.exit()

    def set_focus(self, focus):
        if focus is self.focus:
            return

        if self.focus:
            self.focus.caret.visible = False
            self.focus.caret.mark = self.focus.caret.position = 0

        self.focus = focus
        if self.focus:
            self.focus.caret.visible = True


window = Window(resizable=True)
pyglet.app.run()
