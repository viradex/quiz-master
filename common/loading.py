# Loading screen
import tkinter as tk
from tkinter import ttk


class Loading:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Quiz Master — Please wait...")
        self.root.geometry("1000x600")
        self.root.minsize(800, 600)

        self.frame = ttk.Frame(self.root)
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(
            self.frame, text="Loading, please wait...", font=("Segoe UI", 24)
        ).pack()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    Loading().run()
