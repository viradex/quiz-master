# Welcome screen
import tkinter as tk
from tkinter import ttk


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Quiz Master")
        self.root.geometry("1000x600")
        self.root.minsize(800, 600)

        self.frame = ttk.Frame(self.root, padding=40)
        self.frame.grid(row=0, column=0, sticky="nsew")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.frame.columnconfigure(0, weight=1)

        style = ttk.Style()
        style.configure("Large.TButton", font=("Segoe UI", 16))
        style.configure("Medium.TButton", font=("Segoe UI", 12))
        style.configure("Small.TButton", font=("Segoe UI", 10))

        ttk.Label(
            self.frame,
            text="Welcome to Quiz Master!",
            font=("Segoe UI", 24, "bold"),
        ).grid(row=0, column=0, sticky="n", pady=(15, 0))

        ttk.Label(
            self.frame,
            text="Select game mode:",
            font=("Segoe UI", 12),
        ).grid(row=1, column=0, sticky="n", pady=(10, 0))

        ttk.Button(
            self.frame,
            text="Start as Server",
            style="Large.TButton",
            padding=(50, 10),
            width=15,
        ).grid(row=2, column=0, sticky="n", pady=(30, 0))
        ttk.Button(
            self.frame,
            text="Join as Client",
            style="Large.TButton",
            padding=(50, 10),
            width=15,
        ).grid(row=3, column=0, sticky="n", pady=(10, 0))

        ttk.Button(
            self.frame,
            text="Manage Quizzes",
            style="Medium.TButton",
            padding=(50, 7),
            width=18,
        ).grid(row=4, column=0, sticky="n", pady=(40, 0))
        ttk.Button(
            self.frame,
            text="Settings / Stats",
            style="Medium.TButton",
            padding=(50, 7),
            width=18,
        ).grid(row=5, column=0, sticky="n", pady=(10, 0))

        self.small_btn_frame = ttk.Frame(self.frame)
        self.small_btn_frame.grid(row=6, column=0, pady=(40, 0), sticky="n")

        self.small_btn_frame.columnconfigure(0, weight=1)
        self.small_btn_frame.columnconfigure(1, weight=1)

        ttk.Button(
            self.small_btn_frame,
            text="About / Help",
            style="Small.TButton",
            padding=(8, 5),
            width=15,
        ).grid(row=0, column=0, padx=(2, 5), sticky="e")
        ttk.Button(
            self.small_btn_frame,
            text="Exit",
            style="Small.TButton",
            padding=(8, 5),
            width=15,
        ).grid(row=0, column=1, padx=(2, 0), sticky="w")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    App().run()
