from Quiz.other.FadeText import Fade
import tkinter as tk
from Quiz.other.Words import WordData
from Quiz.other import start_screen  # , end_screen


def translation_label_setup(root):
    # show word to be translated
    translate_text = tk.StringVar(root)
    translate_word_text = tk.Label(root, textvariable=translate_text, font=("Times New Roman", 40, "bold"))
    translate_word_text.pack()

    def set_translate_text(text):
        translate_text.set(text)

    return set_translate_text


def rw_label_setup(root):
    # shows the right translation if you typed it wrong
    wrong_text_var = tk.StringVar(root)
    wrong_text = tk.Label(root, textvariable=wrong_text_var, font=("Times New Roman", 40, "bold"))
    wrong_text_fade = Fade(frame_obj=root, text_obj=wrong_text, time=3, gradiant='exponential')
    wrong_text.pack()

    total_done_right_var = tk.StringVar(root)
    total_done_right = tk.Label(root, textvariable=total_done_right_var, font=("Times New Roman", 20, "bold"))
    total_done_right.pack()

    def both(handler, correct=False):
        amount_right = len(handler.right)
        amount_wrong = len(handler.wrong)
        done = amount_wrong + amount_right
        total = len(handler.current) + done
        total = total - 1 if correct else total

        total_done_right_var.set(f"{total}/{done}/{amount_right}")

    def right_answer(handler):
        both(handler)
        wrong_text_var.set('Correct!')
        wrong_text_fade.change(start=(0, 255, 0), end=(240, 240, 240), time=1)

    def wrong_answer(handler):
        both(handler)
        wrong_text_var.set(handler.current_word['translation'])
        wrong_text_fade.change(start=(255, 0, 0), end=(240, 240, 240), time=3)

    return right_answer, wrong_answer


def text_box_setup(root, word_data_handler):
    # translation entry
    input_text = tk.StringVar(root)
    input_field = tk.Entry(root, textvariable=input_text, font=("Times New Roman", 40, "bold"), justify='center')
    input_field.pack()

    def replace(char):
        replace_from_to = (('§', '¿'),)

        for rep in replace_from_to:
            if char.char == rep[0]:
                text = input_text.get()
                position = input_field.index(tk.INSERT)

                input_text.set(text[:position] + rep[1] + text[position:])

                # Changing position of cursor one character right
                input_field.icursor(position + 1)

                return "break"

    def check_word(_):
        word_data_handler.check_correct(input_text.get())
        input_text.set("")

    input_field.bind('<Return>', check_word)
    input_field.bind('<KeyPress>', replace)


# todo add a hinting system for words
#  eg word "clase de quimica"
#  would have the folowing hints
#  ****************
#  ***** ** *******
#  c**** ** ******a
#  cl*** d* *****ca
#  clase de quimica
def __init__(languishes=('spa', 'swe')):
    # setup
    word_data_handler = WordData(languishes)

    start_screen(word_data_handler, languishes)

    # window
    root = tk.Tk()

    root.geometry("600x400")
    # default_bg = root.cget('bg')

    set_translate_text = translation_label_setup(root)
    text_box_setup(root, word_data_handler)
    right_answer, wrong_answer = rw_label_setup(root)

    word_data_handler.setup(right_answer, wrong_answer, set_translate_text)
    word_data_handler.next_word(True)

    root.mainloop()


# todo add how may you got correct / you have done out of total
if __name__ == '__main__':
    # todo add buttons for selecting if you spelled it right eg
    #   "try again"(same as wrong),
    #   "easy" you got it right (almost right) but it was hard
    #   "medium" you got it right and it was pretty medium
    #   "hard" you easily got it right
    #  these would be used to help the program know when to test you again on that word eg
    #    "try again" directly after
    #    "easy" pretty soon
    #    etc
    __init__()
