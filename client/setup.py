# Client setup screen
import tkinter as tk
from tkinter import ttk


class Setup:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Quiz Master — Client Setup")
        self.root.geometry("1000x600")
        self.root.minsize(800, 600)

        self.frame = ttk.Frame(self.root, padding=20)
        self.frame.grid(row=0, column=0, sticky="nsew")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.frame.columnconfigure(0, weight=0)
        self.frame.columnconfigure(1, weight=1)

        self.server_ip_var = tk.StringVar(value="127.0.0.1")
        self.nickname_var = tk.StringVar()

        style = ttk.Style()
        style.configure("Big.TButton", font=("Segoe UI", 14))
        style.configure("Gray.TLabel", foreground="#A7A7A7", font=("Segoe UI", 8))

        ttk.Label(
            self.frame,
            text="Enter connection details:",
            font=("Segoe UI", 20),
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(30, 0), padx=(30, 0))

        ttk.Label(
            self.frame,
            text="Server IP:",
            font=("Segoe UI", 14),
        ).grid(row=1, column=0, sticky="e", pady=(50, 0), padx=(30, 0))

        ttk.Entry(
            self.frame, textvariable=self.server_ip_var, font=("Segoe UI", 14)
        ).grid(row=1, column=1, sticky="ew", pady=(50, 0), padx=25)

        ttk.Label(
            self.frame, text="Connecting to port: 5555", style="Gray.TLabel"
        ).grid(row=2, column=1, sticky="e", pady=(5, 0), padx=(0, 25))

        ttk.Label(
            self.frame,
            text="Nickname:",
            font=("Segoe UI", 14),
        ).grid(row=3, column=0, sticky="e", pady=(20, 0), padx=(30, 0))

        ttk.Entry(
            self.frame, textvariable=self.nickname_var, font=("Segoe UI", 14)
        ).grid(row=3, column=1, sticky="ew", pady=(20, 0), padx=25)

        ttk.Button(
            self.frame,
            text="Join",
            style="Big.TButton",
            padding=(70, 5),
            width=5,
        ).grid(row=4, column=1, sticky="e", pady=(40, 0), padx=(0, 25))

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    Setup().run()
