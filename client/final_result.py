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

        ttk.Label(self.frame, text="Quiz complete!", font=FONT_MEDIUM).grid(
            row=0, column=0, sticky="n", columnspan=2, pady=(0, 2)
        )

        # Note: 1st -> GoldTitle, 2nd -> SilverTitle, 3rd -> BronzeTitle, rest -> BlackTitle
        # Also exclamation mark at end for 1st-3rd place
        self.ordinal_position = ttk.Label(
            self.frame, text="You came 3rd!", font=FONT_TITLE, foreground=COLOR_BRONZE
        )
        self.ordinal_position.grid(row=1, column=0, sticky="n", columnspan=2)

        ttk.Separator(self.frame, orient="horizontal").grid(
            row=2, column=0, columnspan=2, sticky="ew", pady=10
        )

        content = ttk.Frame(self.frame)
        content.grid(row=3, column=0, columnspan=2, sticky="nsew")

        content.columnconfigure(0, weight=1, uniform="equal")
        content.columnconfigure(2, weight=1, uniform="equal")
        content.rowconfigure(0, weight=1)

        left = ttk.Frame(content)
        left.grid(row=0, column=0, sticky="nsew", padx=(40, 0))

        ttk.Label(
            left,
            text="Summary",
            font=FONT_HEADER,
        ).grid(row=0, column=0, sticky="w", pady=(10, 0))

        self.nickname = ttk.Label(
            left, text="Nickname: Viradex", style="Subtle.TLabel", font=FONT_DESC
        )
        self.nickname.grid(row=1, column=0, sticky="w", pady=(2, 20))

        self.place = ttk.Label(left, text="Place: #3", font=FONT_BODY)
        self.place.grid(row=2, column=0, sticky="w", pady=(0, 5))

        self.points = ttk.Label(left, text="Points: 1000", font=FONT_BODY)
        self.points.grid(row=3, column=0, sticky="w", pady=(0, 5))

        self.score = ttk.Label(left, text="Correct: 1 / 2", font=FONT_BODY)
        self.score.grid(row=4, column=0, sticky="w", pady=(0, 5))

        self.accuracy = ttk.Label(left, text="Accuracy: 50%", font=FONT_BODY)
        self.accuracy.grid(row=5, column=0, sticky="w", pady=(0, 5))

        sep = ttk.Separator(content, orient="vertical")
        sep.grid(row=0, column=1, sticky="ns")

        right = ttk.Frame(content)
        right.grid(row=0, column=2, sticky="nsew", padx=(40, 0))

        right.columnconfigure(0, weight=1)
        right.rowconfigure(5, weight=1)

        ttk.Label(
            right,
            text="Leaderboard Snapshot",
            font=FONT_HEADER,
        ).grid(row=0, column=0, sticky="w", pady=(10, 0))

        ttk.Label(
            right, text="Nearby rankings", style="Subtle.TLabel", font=FONT_DESC
        ).grid(row=1, column=0, sticky="w", pady=(2, 20))

        self.leaderboard = ttk.Treeview(
            right,
            columns=("place", "name", "total"),
            show="headings",
            height=4,
        )
        self.leaderboard.tag_configure("you", font=FONT_TREEVIEW_BOLD)

        self.leaderboard.heading("place", text="Place")
        self.leaderboard.heading("name", text="Name")
        self.leaderboard.heading("total", text="Total")

        self.leaderboard.column("place", anchor="center", width=50)
        self.leaderboard.column("name", anchor="center", width=200)
        self.leaderboard.column("total", anchor="center", width=50)

        self.leaderboard.grid(row=2, column=0, sticky="ew")

        # TODO for prototype only
        players = (
            ("#2", "ItsJakePlayz21", "1835"),
            ("#3", "Viradex (you)", "1000"),
            ("#4", "TrexGamerGirl", "972"),
        )
        for player in players:
            if player[1].endswith("(you)"):
                self.leaderboard.insert("", "end", values=player, tags=("you",))
            else:
                self.leaderboard.insert("", "end", values=player)

        # TODO custom message depending on distance? (e.g. <200pts)
        self.points_behind = ttk.Label(
            right, text="You were 835 points behind 2nd place!", font=FONT_SMALL
        )
        self.points_behind.grid(row=4, column=0, sticky="w", pady=(10, 0))

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
