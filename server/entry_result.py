# Entry results screen
# TODO This and MultiResult should be merged
import tkinter as tk
from tkinter import ttk


class EntryResult:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Quiz Master — Results")
        self.root.geometry("1000x600")
        self.root.minsize(800, 600)

        self.frame = ttk.Frame(self.root, padding=40)
        self.frame.grid(row=0, column=0, sticky="nsew")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.frame.rowconfigure(3, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)

        style = ttk.Style()
        style.configure(
            "CorrectAnswer.TLabel", foreground="#196B24", font=("Segoe UI", 13, "bold")
        )
        style.configure(
            "WrongAnswer.TLabel", foreground="#C00000", font=("Segoe UI", 12)
        )

        style.configure("Treeview", font=("Segoe UI", 12), rowheight=30)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

        style.configure("Gray.TLabel", foreground="#7F7F7F", font=("Segoe UI", 12))
        style.configure(
            "GraySubheading.TLabel", foreground="#4D4D4D", font=("Segoe UI", 14)
        )
        style.configure(
            "LightGraySubheading.TLabel", foreground="#8A8A8A", font=("Segoe UI", 14)
        )

        style.configure("Large.TButton", font=("Segoe UI", 14))
        style.configure("Medium.TButton", font=("Segoe UI", 12))
        style.configure("Small.TButton", font=("Segoe UI", 10))

        ttk.Label(
            self.frame,
            text="Question 2 / 2",
            font=("Segoe UI", 12),
        ).grid(row=0, column=0, sticky="n", columnspan=2, pady=(0, 2))

        ttk.Label(
            self.frame, text="Name a primary color", font=("Segoe UI", 24, "bold")
        ).grid(row=1, column=0, sticky="n", columnspan=2)

        ttk.Separator(self.frame, orient="horizontal").grid(
            row=2, column=0, columnspan=2, sticky="ew", pady=10
        )

        self.content = ttk.Frame(self.frame)
        self.content.grid(row=3, column=0, columnspan=2, sticky="nsew")

        self.content.columnconfigure(0, weight=3)
        self.content.columnconfigure(1, weight=0)
        self.content.columnconfigure(2, weight=2)
        self.content.rowconfigure(0, weight=1)

        left = ttk.Frame(self.content)
        left.grid(row=0, column=0, sticky="nsew", padx=(20, 0))

        left.columnconfigure(0, weight=1)
        left.columnconfigure(1, weight=0)
        left.rowconfigure(1, weight=1)

        ttk.Label(
            left,
            text="Leaderboard",
            font=("Segoe UI", 18, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(10, 20))

        tree = ttk.Treeview(
            left, columns=("place", "name", "gained", "total"), show="headings"
        )

        tree.heading("place", text="Place")
        tree.heading("name", text="Name")
        tree.heading("gained", text="Gained")
        tree.heading("total", text="Total")

        tree.column("place", anchor="center", width=50)
        tree.column("name", anchor="center", width=200)
        tree.column("gained", anchor="center", width=50)
        tree.column("total", anchor="center", width=50)

        scrollbar = ttk.Scrollbar(left, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.grid(row=1, column=0, sticky="nsew")
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
            tree.insert("", "end", values=player)

        ttk.Button(
            left,
            text="Kick Player",
            style="Medium.TButton",
            padding=(20, 0),
            width=10,
        ).grid(row=2, column=0, sticky="w", pady=(10, 0))

        sep = ttk.Separator(self.content, orient="vertical")
        sep.grid(row=0, column=1, sticky="ns", padx=20)

        right = ttk.Frame(self.content)
        right.grid(row=0, column=2, sticky="nsew")

        right.columnconfigure(0, weight=1)
        right.rowconfigure(4, weight=1)

        ttk.Label(
            right,
            text="Responses",
            font=("Segoe UI", 18, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(10, 0))

        ttk.Label(right, text="Players answered: 5 / 5", style="Gray.TLabel").grid(
            row=1, column=0, sticky="w", pady=(5, 20)
        )

        # TODO frame may need attached scrollbar if possible
        answers_frame = ttk.Frame(right)
        answers_frame.grid(row=2, column=0, sticky="nsew")

        answers_frame.columnconfigure(0, weight=1)

        ttk.Label(
            answers_frame, text="Correct Answers", style="GraySubheading.TLabel"
        ).grid(row=0, column=0, sticky="w", pady=(0, 5))

        # TODO row num should be determined automatically, and
        # labels be dynamically shown with a for..in loop
        ttk.Label(
            answers_frame, text=f'✓ "red" — 1 player', style="CorrectAnswer.TLabel"
        ).grid(row=1, column=0, sticky="w", pady=2)
        ttk.Label(
            answers_frame, text=f'✓ "blue" — 1 player', style="CorrectAnswer.TLabel"
        ).grid(row=2, column=0, sticky="w", pady=2)

        ttk.Label(
            answers_frame, text="Other Responses", style="LightGraySubheading.TLabel"
        ).grid(row=3, column=0, sticky="w", pady=(20, 5))

        ttk.Label(
            answers_frame, text=f'"green" — 2 players', style="WrongAnswer.TLabel"
        ).grid(row=4, column=0, sticky="w", pady=2)
        ttk.Label(
            answers_frame, text=f'"purple" — 1 player', style="WrongAnswer.TLabel"
        ).grid(row=5, column=0, sticky="w", pady=2)

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
