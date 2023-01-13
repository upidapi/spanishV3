import tkinter as tk


def select_gui_setup(word_data_handler, languishes):
    root = tk.Tk()
    root.geometry(f"{str(230)}x{str(100)}")

    def select(select_type):
        word_data_handler.get_new_words(select_type)

        root.destroy()

    text_label = tk.Label(root, text='select translation direction')
    text_label.place(relx=0.5, rely=0.2, anchor=tk.CENTER)

    l1_to_l2 = tk.Button(root, text=f'from {languishes[0]} to {languishes[1]}',
                         command=lambda: select('lan1'))
    l1_to_l2.place(relx=0.25, rely=0.5, anchor=tk.CENTER)

    l2_to_l1 = tk.Button(root, text=f'from {languishes[1]} to {languishes[0]}',
                         command=lambda: select('lan2'))
    l2_to_l1.place(relx=0.75, rely=0.5, anchor=tk.CENTER)

    # back = tk.Button(root, text='back', command=WindowSetup.main)
    # back.place(relx=0.1, rely=0.8, anchor=tk.CENTER)

    root.mainloop()
