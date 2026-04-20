# Entry results screen
# TODO This and MultiResult should be merged
import tkinter as tk
from tkinter import ttk

from constants import *


class EntryResult:
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
        style.configure("Success.TLabel", foreground=COLOR_SUCCESS)
        style.configure("Error.TLabel", foreground=COLOR_ERROR)

        style.configure("Subtle.TLabel", foreground=COLOR_DARK_GRAY)
        style.configure("Muted.TLabel", foreground=COLOR_GRAY)

        style.configure("Treeview", font=FONT_TREEIVEW, rowheight=TREEVIEW_ROW_HEIGHT)
        style.configure("Treeview.Heading", font=FONT_TREEVIEW_HEADING)

        style.configure("Large.TButton", font=FONT_BODY)
        style.configure("Medium.TButton", font=FONT_MEDIUM)
        style.configure("Small.TButton", font=FONT_SMALL)

        self.question_num = ttk.Label(
            self.frame,
            text="Question 2 / 2",
            font=FONT_MEDIUM,
        )
        self.question_num.grid(row=0, column=0, sticky="n", columnspan=2, pady=(0, 2))

        self.question_text = ttk.Label(
            self.frame, text="Name a primary color", font=FONT_TITLE
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

        content.grid_propagate(True)

        left = ttk.Frame(content)
        left.grid(row=0, column=0, sticky="nsew", padx=(20, 0))

        left.columnconfigure(0, weight=1)
        left.columnconfigure(1, weight=0)
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
            ("#1", "Peptalker101", "+862", "1837"),
            ("#2", "ItsJakePlayz21", "+871", "1835"),
            ("#3", "Viradex", "+0", "1000"),
            ("#4", "TrexGamerGirl", "+0", "972"),
            ("#5", "Scyrist", "+0", "968"),
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
        right.rowconfigure(2, weight=1)

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

        # TODO move canvas code (for making frame scrollable) to a separate class
        container = ttk.Frame(right)
        container.grid(row=2, column=0, sticky="nsew")

        canvas = tk.Canvas(container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)

        answers_frame = ttk.Frame(canvas)

        answers_frame.bind(
            "<Configure>", lambda _: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=answers_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.configure(width=1)

        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)

        ttk.Label(
            answers_frame,
            text="Correct Answers",
            foreground=COLOR_ASH,
            font=FONT_BODY,
        ).grid(row=0, column=0, sticky="w", pady=(0, 5))

        # TODO row num should be determined automatically, and
        # labels be dynamically shown with a for..in loop
        ttk.Label(
            answers_frame,
            text='✓ "blue" — 1 player',
            style="Success.TLabel",
            font=(FONT_FAMILY, 12, "bold"),
        ).grid(row=1, column=0, sticky="w", pady=2)
        ttk.Label(
            answers_frame,
            text='✓ "red" — 1 player',
            style="Success.TLabel",
            font=(FONT_FAMILY, 12, "bold"),
        ).grid(row=2, column=0, sticky="w", pady=2)
        ttk.Label(
            answers_frame,
            text='✓ "yellow" — 0 players',
            style="Success.TLabel",
            font=(FONT_FAMILY, 12, "bold"),
        ).grid(row=3, column=0, sticky="w", pady=2)

        ttk.Label(
            answers_frame, text="Other Responses", style="Muted.TLabel", font=FONT_BODY
        ).grid(row=4, column=0, sticky="w", pady=(20, 5))

        ttk.Label(
            answers_frame,
            text='"green" — 2 players',
            style="Error.TLabel",
            font=FONT_MEDIUM,
        ).grid(row=5, column=0, sticky="w", pady=2)
        ttk.Label(
            answers_frame,
            text='"purple" — 1 player',
            style="Error.TLabel",
            font=FONT_MEDIUM,
        ).grid(row=6, column=0, sticky="w", pady=2)

        ttk.Button(
            right,
            text="Next Question",
            style="Large.TButton",
            padding=(5, 5),
            width=20,
        ).grid(row=3, column=0, sticky="w", pady=(30, 0))

        ttk.Button(
            right,
            text="End Game",
            style="Small.TButton",
            padding=(8, 5),
            width=15,
        ).grid(row=4, column=0, sticky="se")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    EntryResult().run()
