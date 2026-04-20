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

        self.loading = ttk.Label(
            self.frame,
            text="⠋  Loading...",
            font=(FONT_FAMILY, 32),
        )
        self.loading.pack()

        self.action = ttk.Label(
            self.frame,
            text="Preparing game...",
            font=(FONT_FAMILY, 16),
            foreground=COLOR_DARK_GRAY,
        )
        self.action.pack(pady=(10, 0))

        self.spinner = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.index = 0

        self.animate_loading()

    def animate_loading(self):
        # Might be an exception for the prototype guidelines ;)
        frame = self.spinner[self.index]
        self.loading.config(text=f"{frame}  Loading...")

        self.index = (self.index + 1) % len(self.spinner)
        self.root.after(80, self.animate_loading)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    Loading().run()
