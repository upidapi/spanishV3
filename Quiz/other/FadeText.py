class Gradiant:
    def __init__(self, fade_instance, func):
        self.fade_instance = fade_instance
        self.func = func

    def get(self):
        fraction = self.fade_instance.steps / self.fade_instance.total_steps
        if self.func == 'linear':
            return fraction

        elif self.func == 'exponential':
            # starts increasing slowly speeds upp
            return fraction ** 5

        elif self.func == 'inverse_exponential':
            # starts increasing alot slows down
            return (fraction - 1) ** 5 + 1


class Fade:
    MILLISECONDS_PER_FRAME = 50

    def __init__(self, text_obj, frame_obj, start=(240, 240, 240), end=(240, 240, 240), time=1, steps=0, 
                 gradiant='linear'):
        self.text_obj = text_obj
        self.frame_obj = frame_obj
        self.steps = steps
        self.total_steps = (time * 1000) // Fade.MILLISECONDS_PER_FRAME
        self.gradiant = Gradiant(self, gradiant)
        self.start = start
        self.end = end

    def change(self, time_step=0.0, start=None, end=None, time=None):
        if time is not None:
            self.total_steps = (time * 1000) // Fade.MILLISECONDS_PER_FRAME
        if start is not None:
            self.start = start
        if end is not None:
            self.end = end

        if time_step <= self.steps + 1:
            self.steps = time_step

            gradiant = self.gradiant.get()
            colors = []
            for i in range(3):
                dif = self.end[i] - self.start[i]
                color = int(self.start[i] + dif * gradiant)
                colors.append(color)

            colors = tuple(colors)

            color_hex = '#%02x%02x%02x' % colors
            self.text_obj.configure(foreground=color_hex)

            if self.steps != self.total_steps:
                self.frame_obj.after(50, lambda: self.change(time_step + 1))
