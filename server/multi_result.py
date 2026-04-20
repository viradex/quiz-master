# Multi-choice results screen
import tkinter as tk
from tkinter import ttk

from constants import *


class MultiResult:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Quiz Master — Results")
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
        style.configure("Subtle.TLabel", foreground=COLOR_DARK_GRAY)

        style.configure("AnswerA.TLabel", foreground=COLOR_RED, font=FONT_ANSWER)
        style.configure("AnswerB.TLabel", foreground=COLOR_BLUE, font=FONT_ANSWER)
        style.configure("AnswerC.TLabel", foreground=COLOR_YELLOW, font=FONT_ANSWER)
        style.configure("AnswerD.TLabel", foreground=COLOR_GREEN, font=FONT_ANSWER)

        style.configure("Treeview", font=FONT_TREEIVEW, rowheight=TREEVIEW_ROW_HEIGHT)
        style.configure("Treeview.Heading", font=FONT_TREEVIEW_HEADING)

        style.configure("Large.TButton", font=FONT_BODY)
        style.configure("Medium.TButton", font=FONT_MEDIUM)
        style.configure("Small.TButton", font=FONT_SMALL)

        self.question_num = ttk.Label(
            self.frame,
            text="Question 1 / 2",
            font=FONT_MEDIUM,
        )
        self.question_num.grid(row=0, column=0, sticky="n", columnspan=2, pady=(0, 2))

        self.question_text = ttk.Label(
            self.frame, text="What is 2 + 2?", font=FONT_TITLE
        )
        self.question_text.grid(row=1, column=0, sticky="n", columnspan=2)

        ttk.Separator(self.frame, orient="horizontal").grid(
            row=2, column=0, columnspan=2, sticky="ew", pady=10
        )

        content = ttk.Frame(self.frame)
        content.grid(row=3, column=0, columnspan=2, sticky="nsew")

        content.columnconfigure(0, weight=3)
        content.columnconfigure(2, weight=2)
        content.rowconfigure(0, weight=1)

        left = ttk.Frame(content)
        left.grid(row=0, column=0, sticky="nsew", padx=(20, 0))

        left.columnconfigure(0, weight=1)
        left.rowconfigure(1, weight=1)

        ttk.Label(
            left,
            text="Leaderboard",
            font=FONT_HEADER,
        ).grid(row=0, column=0, sticky="w", pady=(10, 20))

        self.leaderboard = ttk.Treeview(
            left, columns=("place", "name", "gained", "total"), show="headings"
        )

        self.leaderboard.heading("place", text="Place")
        self.leaderboard.heading("name", text="Name")
        self.leaderboard.heading("gained", text="Gained")
        self.leaderboard.heading("total", text="Total")

        self.leaderboard.column("place", anchor="center", width=50)
        self.leaderboard.column("name", anchor="center", width=200)
        self.leaderboard.column("gained", anchor="center", width=50)
        self.leaderboard.column("total", anchor="center", width=50)

        scrollbar = ttk.Scrollbar(
            left, orient="vertical", command=self.leaderboard.yview
        )
        self.leaderboard.configure(yscrollcommand=scrollbar.set)

        self.leaderboard.grid(row=1, column=0, sticky="nsew")
        scrollbar.grid(row=1, column=1, sticky="ns")

        # TODO for prototype only
        players = (
            ("#1", "Viradex", "+1000", "1000"),
            ("#2", "Peptalker101", "+975", "975"),
            ("#3", "TrexGamerGirl", "+972", "972"),
            ("#4", "Scyrist", "+968", "968"),
            ("#5", "ItsJakePlayz21", "+964", "964"),
        )
        for player in players:
            self.leaderboard.insert("", "end", values=player)

        self.kick_player_btn = ttk.Button(
            left,
            text="Kick Player",
            style="Medium.TButton",
            padding=(20, 0),
            width=10,
        )
        self.kick_player_btn.grid(row=2, column=0, sticky="w", pady=(10, 0))

        sep = ttk.Separator(content, orient="vertical")
        sep.grid(row=0, column=1, sticky="ns", padx=20)

        right = ttk.Frame(content)
        right.grid(row=0, column=2, sticky="nsew")

        right.columnconfigure(0, weight=1)
        right.rowconfigure(7, weight=1)

        ttk.Label(
            right,
            text="Responses",
            font=FONT_HEADER,
        ).grid(row=0, column=0, sticky="w", pady=(10, 0))

        self.players_answered = ttk.Label(
            right,
            text="Players answered: 5 / 5",
            style="Subtle.TLabel",
            font=FONT_MEDIUM,
        )
        self.players_answered.grid(row=1, column=0, sticky="w", pady=(5, 20))

        self.answer_a = ttk.Label(right, text="A: 0   ", style="AnswerA.TLabel")
        self.answer_a.grid(row=2, column=0, sticky="w")

        self.answer_b = ttk.Label(right, text="B: 5  ✓", style="AnswerB.TLabel")
        self.answer_b.grid(row=3, column=0, sticky="w")

        self.answer_c = ttk.Label(right, text="C: 0  ", style="AnswerC.TLabel")
        self.answer_c.grid(row=4, column=0, sticky="w")

        self.answer_d = ttk.Label(right, text="D: 0  ", style="AnswerD.TLabel")
        self.answer_d.grid(row=5, column=0, sticky="w")

        ttk.Button(
            right,
            text="Next Question",
            style="Large.TButton",
            padding=(5, 5),
            width=20,
        ).grid(row=6, column=0, sticky="w", pady=(30, 0))

        ttk.Button(
            right,
            text="End Game",
            style="Small.TButton",
            padding=(8, 5),
            width=15,
        ).grid(row=7, column=0, sticky="se")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    MultiResult().run()
