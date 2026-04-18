# Multi-choice results screen
import tkinter as tk
from tkinter import ttk


class MultiResult:
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
            "AnswerRed.TLabel", foreground="#E74C3C", font=("Segoe UI", 18, "bold")
        )
        style.configure(
            "AnswerBlue.TLabel", foreground="#3498DB", font=("Segoe UI", 18, "bold")
        )
        style.configure(
            "AnswerYellow.TLabel", foreground="#F1C40F", font=("Segoe UI", 18, "bold")
        )
        style.configure(
            "AnswerGreen.TLabel", foreground="#2ECC71", font=("Segoe UI", 18, "bold")
        )

        style.configure("Treeview", font=("Segoe UI", 12), rowheight=30)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

        style.configure("Gray.TLabel", foreground="#7F7F7F", font=("Segoe UI", 12))

        style.configure("Large.TButton", font=("Segoe UI", 14))
        style.configure("Medium.TButton", font=("Segoe UI", 12))
        style.configure("Small.TButton", font=("Segoe UI", 10))

        ttk.Label(
            self.frame,
            text="Question 1 / 2",
            font=("Segoe UI", 12),
        ).grid(row=0, column=0, sticky="n", columnspan=2, pady=(0, 2))

        ttk.Label(
            self.frame, text="What is 2 + 2?", font=("Segoe UI", 24, "bold")
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
            ("#1", "Viradex", "+1000", "1000"),
            ("#2", "Peptalker101", "+975", "975"),
            ("#3", "TrexGamerGirl", "+972", "972"),
            ("#4", "Scyrist", "+968", "968"),
            ("#5", "ItsJakePlayz21", "+964", "964"),
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
        right.rowconfigure(7, weight=1)

        ttk.Label(
            right,
            text="Responses",
            font=("Segoe UI", 18, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(10, 0))

        ttk.Label(right, text="Players answered: 5 / 5", style="Gray.TLabel").grid(
            row=1, column=0, sticky="w", pady=(5, 20)
        )

        ttk.Label(right, text="A: 0   ", style="AnswerRed.TLabel").grid(
            row=2, column=0, sticky="w"
        )
        ttk.Label(right, text="B: 5  ✓", style="AnswerBlue.TLabel").grid(
            row=3, column=0, sticky="w"
        )
        ttk.Label(right, text="C: 0  ", style="AnswerYellow.TLabel").grid(
            row=4, column=0, sticky="w"
        )
        ttk.Label(right, text="D: 0  ", style="AnswerGreen.TLabel").grid(
            row=5, column=0, sticky="w"
        )

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
