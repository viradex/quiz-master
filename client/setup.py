# Client setup screen
import tkinter as tk
from tkinter import ttk


class Setup:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Quiz Master — Client Setup")
        self.root.geometry("1000x600")
        self.root.minsize(800, 600)

        self.frame = ttk.Frame(self.root, padding=40)
        self.frame.grid(row=0, column=0, sticky="nsew")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.frame.columnconfigure(0, weight=0)
        self.frame.columnconfigure(1, weight=1)

        # TODO remove default value for prod
        self.server_ip_var = tk.StringVar(value="127.0.0.1")
        self.nickname_var = tk.StringVar()

        style = ttk.Style()
        style.configure("Large.TButton", font=("Segoe UI", 14))
        style.configure("Medium.TButton", font=("Segoe UI", 12))
        style.configure("Gray.TLabel", foreground="#A7A7A7", font=("Segoe UI", 8))

        ttk.Label(
            self.frame,
            text="Enter connection details:",
            font=("Segoe UI", 20),
        ).grid(row=0, column=0, columnspan=2, sticky="w")

        # TODO add IP hint if users get confused in testing
        # something like "see server screen for IP"
        ttk.Label(
            self.frame,
            text="Server IP:",
            font=("Segoe UI", 14),
        ).grid(row=1, column=0, sticky="e", pady=(50, 0))

        ttk.Entry(
            self.frame, textvariable=self.server_ip_var, font=("Segoe UI", 14)
        ).grid(row=1, column=1, sticky="ew", pady=(50, 0), padx=(25, 0))

        ttk.Label(
            self.frame, text="Connecting to port: 7878", style="Gray.TLabel"
        ).grid(row=2, column=1, sticky="e", pady=(5, 0))

        ttk.Label(
            self.frame,
            text="Nickname:",
            font=("Segoe UI", 14),
        ).grid(row=3, column=0, sticky="e", pady=(20, 0))

        ttk.Entry(
            self.frame, textvariable=self.nickname_var, font=("Segoe UI", 14)
        ).grid(row=3, column=1, sticky="ew", pady=(20, 0), padx=(25, 0))

        ttk.Button(
            self.frame,
            text="Return to Menu",
            style="Medium.TButton",
            padding=(30, 5),
            width=15,
        ).grid(row=4, column=0, columnspan=2, sticky="w", pady=(40, 0))

        ttk.Button(
            self.frame,
            text="Join",
            style="Large.TButton",
            padding=(30, 5),
            width=15,
        ).grid(row=4, column=1, sticky="e", pady=(40, 0))

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    Setup().run()
