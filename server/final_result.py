# Final results screen
import tkinter as tk
from tkinter import ttk

from constants import *


class FinalResult:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Quiz Master — Final Results")
        self.root.geometry(WINDOW_GEOMETRY)
        self.root.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        self.frame = ttk.Frame(self.root, padding=40)
        self.frame.grid(row=0, column=0, sticky="nsew")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.frame.rowconfigure(3, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)

        style = ttk.Style()
        style.configure("Treeview", font=FONT_TREEIVEW, rowheight=TREEVIEW_ROW_HEIGHT)
        style.configure("Treeview.Heading", font=FONT_TREEVIEW_HEADING)

        style.configure("Subtle.TLabel", foreground=COLOR_DARK_GRAY)
        style.configure("Medium.TButton", font=FONT_MEDIUM)

        ttk.Label(
            self.frame,
            text="Quiz complete!",
            font=FONT_MEDIUM,
        ).grid(row=0, column=0, sticky="n", columnspan=2, pady=(0, 2))

        # Note: 1st -> GoldTitle, 2nd -> SilverTitle, 3rd -> BronzeTitle, rest -> BlackTitle
        # Also exclamation mark at end for 1st-3rd place
        ttk.Label(self.frame, text="Final Standings", font=FONT_TITLE).grid(
            row=1, column=0, sticky="n", columnspan=2
        )

        ttk.Separator(self.frame, orient="horizontal").grid(
            row=2, column=0, columnspan=2, sticky="ew", pady=10
        )

        content = ttk.Frame(self.frame)
        content.grid(row=3, column=0, columnspan=2, sticky="nsew")

        content.columnconfigure(0, weight=5)
        content.columnconfigure(2, weight=1)
        content.rowconfigure(0, weight=1)

        left = ttk.Frame(content)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

        left.columnconfigure(0, weight=1)
        left.rowconfigure(2, weight=1)

        ttk.Label(
            left,
            text="Leaderboard",
            font=FONT_HEADER,
        ).grid(row=0, column=0, sticky="w", pady=(10, 0))

        ttk.Label(
            left, text="All players ranked", style="Subtle.TLabel", font=FONT_DESC
        ).grid(row=1, column=0, sticky="w", pady=(2, 20))

        self.leaderboard = ttk.Treeview(
            left, columns=("place", "name", "total"), show="headings"
        )
        self.leaderboard.tag_configure(
            "gold", foreground=COLOR_GOLD, font=FONT_TREEVIEW_BOLD
        )
        self.leaderboard.tag_configure(
            "silver", foreground=COLOR_SILVER, font=FONT_TREEVIEW_BOLD
        )
        self.leaderboard.tag_configure(
            "bronze", foreground=COLOR_BRONZE, font=FONT_TREEVIEW_BOLD
        )

        self.leaderboard.heading("place", text="Place")
        self.leaderboard.heading("name", text="Name")
        self.leaderboard.heading("total", text="Total")

        self.leaderboard.column("place", anchor="center", width=50)
        self.leaderboard.column("name", anchor="center", width=200)
        self.leaderboard.column("total", anchor="center", width=50)

        scroll = ttk.Scrollbar(left, orient="vertical", command=self.leaderboard.yview)
        self.leaderboard.configure(yscrollcommand=scroll.set)

        self.leaderboard.grid(row=2, column=0, sticky="nsew")
        scroll.grid(row=2, column=1, sticky="ns")

        # TODO for prototype only
        players = (
            ("#1", "Peptalker101", "1837"),
            ("#2", "ItsJakePlayz21", "1835"),
            ("#3", "Viradex", "1000"),
            ("#4", "TrexGamerGirl", "972"),
            ("#5", "Scyrist", "968"),
        )
        for player in players:
            if player[0] == "#1":
                self.leaderboard.insert("", "end", values=player, tags=("gold",))
            elif player[0] == "#2":
                self.leaderboard.insert("", "end", values=player, tags=("silver",))
            elif player[0] == "#3":
                self.leaderboard.insert("", "end", values=player, tags=("bronze",))
            else:
                self.leaderboard.insert("", "end", values=player)

        sep = ttk.Separator(content, orient="vertical")
        sep.grid(row=0, column=1, sticky="ns")

        right = ttk.Frame(content)
        right.grid(row=0, column=2, sticky="nsew", padx=(20, 0))

        right.columnconfigure(0, weight=1)
        right.rowconfigure(5, weight=1)

        ttk.Label(
            right,
            text="Game Summary",
            font=FONT_HEADER,
        ).grid(row=0, column=0, sticky="w", pady=(10, 0))

        ttk.Label(
            right, text="Session stats", style="Subtle.TLabel", font=FONT_DESC
        ).grid(row=1, column=0, sticky="w", pady=(2, 20))

        self.players_amount = ttk.Label(right, text="Players: 5", font=FONT_MEDIUM)
        self.players_amount.grid(row=2, column=0, sticky="w", pady=(0, 6))

        self.questions_amount = ttk.Label(right, text="Questions: 2", font=FONT_MEDIUM)
        self.questions_amount.grid(row=3, column=0, sticky="w", pady=(0, 6))

        self.winner = ttk.Label(
            right,
            text="Winner: Peptalker101 (1837 pts)",
            font=(FONT_FAMILY, 12, "bold"),
        )
        self.winner.grid(row=4, column=0, sticky="w", pady=(0, 6))

        ttk.Button(
            right,
            text="Back to Menu",
            style="Medium.TButton",
            padding=(8, 5),
            width=15,
        ).grid(row=5, column=0, sticky="se")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    FinalResult().run()
