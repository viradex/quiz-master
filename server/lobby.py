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

        self.quiz_var = tk.StringVar()

        style = ttk.Style()
        style.configure("Large.TButton", font=FONT_LARGE)
        style.configure("Medium.TButton", font=FONT_MEDIUM)
        style.configure("Small.TButton", font=FONT_TINY)

        style.configure("Treeview", font=FONT_TREEIVEW, rowheight=TREEVIEW_ROW_HEIGHT)
        style.configure("Large.TCombobox", padding=8)
        style.configure("Muted.TLabel", foreground=COLOR_GRAY)

        ttk.Label(
            self.frame,
            text="Lobby",
            font=FONT_TITLE,
        ).grid(row=0, column=0, sticky="w", padx=(40, 0))

        self.players_amount = ttk.Label(
            self.frame,
            text="Players: 5 / 16",
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

        # TODO for prototype only
        players = (
            "Viradex",
            "Peptalker101",
            "TrexGamerGirl",
            "Scyrist",
            "ItsJakePlayz21",
        )
        for player in players:
            self.players.insert("", "end", text=player)

        scrollbar.config(command=self.players.yview)

        player_btn_frame = ttk.Frame(self.frame)
        player_btn_frame.grid(row=3, column=0, sticky="nsew", padx=(40, 0))

        self.get_info_btn = ttk.Button(
            player_btn_frame,
            text="Get Info",
            style="Medium.TButton",
            padding=(10, 0),
            width=10,
        )
        self.get_info_btn.grid(row=0, column=0, sticky="e", pady=(10, 0), padx=(0, 5))

        self.kick_player_btn = ttk.Button(
            player_btn_frame,
            text="Kick Player",
            style="Medium.TButton",
            padding=(10, 0),
            width=10,
        )
        self.kick_player_btn.grid(
            row=0, column=1, sticky="w", pady=(10, 0), padx=(5, 0)
        )

        # TODO should inform when lobby is full so its no longer waiting
        self.waiting_status = ttk.Label(
            self.frame,
            text="Waiting for players...",
            font=FONT_SMALL,
        )
        self.waiting_status.grid(
            row=4, column=0, sticky="sw", pady=(30, 0), padx=(40, 0)
        )

        ttk.Label(
            self.frame,
            text="Server IP: 192.168.0.2",
            font=(FONT_FAMILY, 28),
        ).grid(row=0, column=1, sticky="n")

        quiz_ctrl_frame = ttk.Frame(self.frame)
        quiz_ctrl_frame.grid(row=2, column=1, sticky="nsew", pady=(50, 0))

        quiz_ctrl_frame.columnconfigure(0, weight=1)

        ttk.Label(
            quiz_ctrl_frame,
            text="Select quiz:",
            font=FONT_MEDIUM,
        ).grid(row=0, column=0, sticky="n")

        # Makes the dropdown font larger as well (global config)
        # If more dropdowns are added in the future, this font will be used
        # It can be overwritten by recalling this code with new font
        self.root.option_add("*TCombobox*Listbox.font", FONT_MEDIUM)

        self.quiz_combo = ttk.Combobox(
            quiz_ctrl_frame,
            textvariable=self.quiz_var,
            values=("Maths Quiz", "Science Quiz", "General Knowledge Quiz"),
            width=30,
            style="Large.TCombobox",
            font=FONT_MEDIUM,
            state="readonly",
        )
        self.quiz_combo.grid(row=1, column=0, sticky="n", pady=(10, 0))

        self.start_game_btn = ttk.Button(
            quiz_ctrl_frame,
            text="Start Game",
            style="Large.TButton",
            padding=(20, 10),
            width=15,
        )
        self.start_game_btn.grid(row=2, column=0, sticky="n", pady=(80, 0))

        # Should be hidden with .grid_forget() when button is enabled
        # Text should also inform that game can only be started with 2+ players
        self.instruction = ttk.Label(
            quiz_ctrl_frame,
            text="(select quiz to start)",
            style="Muted.TLabel",
            font=FONT_SMALL,
        )
        self.instruction.grid(row=3, column=0, sticky="n", pady=(5, 0))

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
