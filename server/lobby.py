# Lobby screen
import tkinter as tk
from tkinter import ttk


class Lobby:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Quiz Master — Lobby")
        self.root.geometry("1000x600")
        self.root.minsize(800, 600)

        self.frame = ttk.Frame(self.root, padding=40)
        self.frame.grid(row=0, column=0, sticky="nsew")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.frame.columnconfigure(0, weight=0)
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(0, weight=0)
        self.frame.rowconfigure(1, weight=0)
        self.frame.rowconfigure(2, weight=1)
        self.frame.rowconfigure(3, weight=0)

        self.quiz_var = tk.StringVar()

        style = ttk.Style()
        style.configure("Large.TButton", font=("Segoe UI", 18))
        style.configure("Medium.TButton", font=("Segoe UI", 12))
        style.configure("Small.TButton", font=("Segoe UI", 8))

        style.configure("Treeview", font=("Segoe UI", 12), rowheight=30)
        style.configure("Large.TCombobox", padding=8)
        style.configure("Gray.TLabel", foreground="#A7A7A7", font=("Segoe UI", 10))

        ttk.Label(
            self.frame,
            text="Lobby",
            font=("Segoe UI", 24, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=(40, 0))

        ttk.Label(
            self.frame,
            text="Players: 5/16",
            font=("Segoe UI", 12),
        ).grid(row=1, column=0, sticky="w", pady=(5, 0), padx=(40, 0))

        tree_frame = ttk.Frame(self.frame)
        tree_frame.grid(row=2, column=0, sticky="nsew", pady=(20, 0), padx=(40, 0))

        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.tree = ttk.Treeview(
            tree_frame,
            show="tree",
            height=20,
            selectmode="browse",
            yscrollcommand=scrollbar.set,
        )

        self.tree.column("#0", width=250, anchor="center", stretch=True)
        self.tree.grid(row=0, column=0, sticky="nsew")

        # TODO for prototype only
        players = (
            "Viradex",
            "Peptalker101",
            "TrexGamerGirl",
            "Scyrist",
            "ItsJakePlayz21",
        )
        for player in players:
            self.tree.insert("", "end", text=player)

        scrollbar.config(command=self.tree.yview)

        player_btn_frame = ttk.Frame(self.frame)
        player_btn_frame.grid(row=3, column=0, sticky="nsew", padx=(40, 0))

        ttk.Button(
            player_btn_frame,
            text="Get Info",
            style="Medium.TButton",
            padding=(10, 0),
            width=10,
        ).grid(row=0, column=0, sticky="e", pady=(10, 0), padx=(0, 5))
        ttk.Button(
            player_btn_frame,
            text="Kick Player",
            style="Medium.TButton",
            padding=(10, 0),
            width=10,
        ).grid(row=0, column=1, sticky="w", pady=(10, 0), padx=(5, 0))

        ttk.Label(
            self.frame,
            text="Waiting for players...",
            font=("Segoe UI", 10),
        ).grid(row=4, column=0, sticky="sw", pady=(30, 0), padx=(40, 0))

        ttk.Label(
            self.frame,
            text="Server IP: 192.168.0.2",
            font=("Segoe UI", 28),
        ).grid(row=0, column=1, sticky="n")

        quiz_ctrl_frame = ttk.Frame(self.frame)
        quiz_ctrl_frame.grid(row=2, column=1, sticky="nsew", pady=(50, 0))
        quiz_ctrl_frame.columnconfigure(0, weight=1)

        ttk.Label(
            quiz_ctrl_frame,
            text="Select quiz:",
            font=("Segoe UI", 12),
        ).grid(row=0, column=0, sticky="n")

        # Makes the dropdown font large as well (global config)
        # If more dropdowns are added in the future, this font will be used
        # It can be overwritten by recalling this code with new font
        self.root.option_add("*TCombobox*Listbox.font", ("Segoe UI", 12))

        self.quiz_combo = ttk.Combobox(
            quiz_ctrl_frame,
            textvariable=self.quiz_var,
            values=("Maths Quiz", "Science Quiz", "General Knowledge Quiz"),
            width=30,
            style="Large.TCombobox",
            font=("Segoe UI", 12),
            state="readonly",
        )
        self.quiz_combo.grid(row=1, column=0, sticky="n", pady=(10, 0))

        ttk.Button(
            quiz_ctrl_frame,
            text="Start Game",
            style="Large.TButton",
            padding=(20, 10),
            width=15,
        ).grid(row=2, column=0, sticky="n", pady=(80, 0))

        # Should be hidden with .grid_forget() when button is enabled
        # Text should also inform that game can only be started with 2+ players
        ttk.Label(
            quiz_ctrl_frame, text="(select quiz to start)", style="Gray.TLabel"
        ).grid(row=3, column=0, sticky="n", pady=(5, 0))

        ttk.Button(
            self.frame,
            text="Close Lobby",
            style="Small.TButton",
            padding=(8, 5),
            width=15,
        ).grid(row=4, column=1, sticky="ne", pady=(40, 0), padx=(0, 40))

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    Lobby().run()
