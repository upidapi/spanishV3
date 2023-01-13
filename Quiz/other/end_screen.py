import tkinter as tk


def select_gui_setup(word_data_handler, languishes):
    root = tk.Tk()
    root.geometry(f"{str(200)}x{str(250)}")

    def select(select_type):
        word_data_handler.get_new_words(select_type)
        word_data_handler.next_word(True)

        root.destroy()

    amount_right = len(word_data_handler.right)
    amount_wrong = len(word_data_handler.wrong)
    total = amount_wrong + amount_right

    text_label = tk.Label(root, text=f'you got {amount_right}/{total} right')
    text_label.place(relx=0.5, rely=0.10, anchor=tk.CENTER)

    text_label = tk.Label(root, text='select new words')
    text_label.place(relx=0.5, rely=0.30, anchor=tk.CENTER)

    l1_to_l2 = tk.Button(root, text=f'all from {languishes[0]} to {languishes[1]}',
                         command=lambda: select('lan1'))
    l1_to_l2.place(relx=0.5, rely=0.45, anchor=tk.CENTER)

    l2_to_l1 = tk.Button(root, text=f'all from {languishes[1]} to {languishes[0]}',
                         command=lambda: select('lan2'))
    l2_to_l1.place(relx=0.5, rely=0.60, anchor=tk.CENTER)

    same_words = tk.Button(root, text=f'same words as last time',
                           command=lambda: select('same'))
    same_words.place(relx=0.5, rely=0.75, anchor=tk.CENTER)

    wrong_words = tk.Button(root, text=f'the words you got wrong',
                            command=lambda: select('wrong'))
    wrong_words.place(relx=0.5, rely=0.90, anchor=tk.CENTER)

    # probably not useful
    # right_words = tk.Button(root, text=f'the words you got right',
    #                         command=lambda: select('right'))
    # right_words.place(relx=0.7, rely=0.6, anchor=tk.CENTER)
