# Lobby screen
import tkinter as tk
from tkinter import ttk

from constants import *


class Lobby:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Quiz Master — Lobby")
        self.root.geometry(WINDOW_GEOMETRY)
        self.root.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        self.frame = ttk.Frame(self.root, padding=40)
        self.frame.grid(row=0, column=0, sticky="nsew")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(2, weight=1)

        style = ttk.Style()
        style.configure("Small.TButton", font=FONT_TINY)
        style.configure("Treeview", font=FONT_TREEIVEW, rowheight=TREEVIEW_ROW_HEIGHT)
        style.configure("Muted.TLabel", foreground=COLOR_GRAY)

        ttk.Label(
            self.frame,
            text="Lobby",
            font=FONT_TITLE,
        ).grid(row=0, column=0, sticky="w", padx=(40, 0))

        self.players_amount = ttk.Label(
            self.frame,
            text="Players: 5",
            font=FONT_MEDIUM,
        )
        self.players_amount.grid(row=1, column=0, sticky="w", pady=(5, 0), padx=(40, 0))

        tree_frame = ttk.Frame(self.frame)
        tree_frame.grid(row=2, column=0, sticky="nsew", pady=(20, 0), padx=(40, 0))

        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.players = ttk.Treeview(
            tree_frame,
            show="tree",
            height=20,
            selectmode="browse",
            yscrollcommand=scrollbar.set,
        )

        self.players.column("#0", width=250, anchor="center", stretch=True)
        self.players.grid(row=0, column=0, sticky="nsew")
        self.players.tag_configure("you", font=FONT_TREEVIEW_BOLD)

        # TODO for prototype only
        players = (
            "Viradex (you)",
            "Peptalker101",
            "TrexGamerGirl",
            "Scyrist",
            "ItsJakePlayz21",
        )
        for player in players:
            if player.endswith("(you)"):
                self.players.insert("", "end", text=player, tags=("you",))
            else:
                self.players.insert("", "end", text=player)

        scrollbar.config(command=self.players.yview)

        self.connection_details = ttk.Label(
            self.frame,
            text="Connected to 127.0.0.1:7878",
            font=FONT_TINY,
        )
        self.connection_details.grid(
            row=3, column=0, sticky="sw", pady=(30, 0), padx=(40, 0)
        )

        progress_frame = ttk.Frame(self.frame)
        progress_frame.grid(row=2, column=1, sticky="nsew")

        progress_frame.columnconfigure(0, weight=1)

        ttk.Label(
            progress_frame,
            text="Waiting for the host to start the game...",
            font=FONT_LARGE,
            justify="center",
            anchor="center",
        ).grid(row=0, column=0, sticky="ew", pady=(20, 10), padx=(50, 10))

        progress = ttk.Progressbar(progress_frame, mode="indeterminate", length=500)
        progress.grid(row=1, column=0, sticky="ew", pady=(5, 0), padx=(50, 10))
        progress.start(20)

        ttk.Label(
            progress_frame,
            text="Connected to server. Game will begin shortly.",
            style="Muted.TLabel",
            font=FONT_SMALL,
            justify="center",
            anchor="center",
        ).grid(row=2, column=0, sticky="ew", pady=(10, 0), padx=(50, 10))

        ttk.Button(
            self.frame,
            text="Leave Game",
            style="Small.TButton",
            padding=(8, 5),
            width=15,
        ).grid(row=3, column=1, sticky="ne", pady=(40, 0), padx=(0, 40))

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    Lobby().run()
