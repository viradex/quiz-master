# Disconnected screen
import tkinter as tk
from tkinter import ttk


class Disconnect:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Quiz Master — Disconnected")
        self.root.geometry("1000x600")
        self.root.minsize(800, 600)

        self.frame = ttk.Frame(self.root, padding=40)
        self.frame.pack(expand=True)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        style = ttk.Style()
        style.configure("Large.TButton", font=("Segoe UI", 14))

        ttk.Label(
            self.frame,
            text="Disconnected",
            font=("Segoe UI", 24, "bold"),
        ).pack()

        ttk.Label(
            self.frame,
            text="You have been disconnected from the server.",
            font=("Segoe UI", 12),
        ).pack(pady=(5, 0))

        ttk.Label(
            self.frame,
            text="Reason: Kicked by host",
            font=("Segoe UI", 16),
        ).pack(pady=(20, 0))

        ttk.Button(
            self.frame,
            text="Return to Menu",
            style="Large.TButton",
            padding=(50, 10),
        ).pack(pady=(50, 0))

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    Disconnect().run()
