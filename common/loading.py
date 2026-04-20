# Loading screen
import tkinter as tk
from tkinter import ttk

from constants import *


class Loading:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Quiz Master — Please wait...")
        self.root.geometry(WINDOW_GEOMETRY)
        self.root.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        self.frame = ttk.Frame(self.root, padding=40)
        self.frame.pack(expand=True)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        ttk.Label(
            self.frame, text="Loading, please wait...", font=(FONT_FAMILY, 24, "italic")
        ).pack()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    Loading().run()
