# Final results screen
import tkinter as tk
from tkinter import ttk


class FinalResult:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Quiz Master — Final Results")
        self.root.geometry("1000x600")
        self.root.minsize(800, 600)

        self.frame = ttk.Frame(self.root, padding=40)
        self.frame.grid(row=0, column=0, sticky="nsew")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.frame.rowconfigure(3, weight=3)
        self.frame.rowconfigure(4, weight=0)
        self.frame.rowconfigure(5, weight=2)
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)

        style = ttk.Style()
        style.configure(
            "GoldTitle.TLabel", foreground="#D4AF37", font=("Segoe UI", 24, "bold")
        )
        style.configure(
            "SilverTitle.TLabel", foreground="#B0B0B0", font=("Segoe UI", 24, "bold")
        )
        style.configure(
            "BronzeTitle.TLabel", foreground="#CD7F32", font=("Segoe UI", 24, "bold")
        )
        style.configure(
            "BlackTitle.TLabel", foreground="#2E2E2E", font=("Segoe UI", 24, "bold")
        )

        style.configure(
            "Treeview",
            font=("Segoe UI", 14, "bold"),
            rowheight=28,
        )

        style.configure(
            "AnswerCorrect.TLabel", foreground="#2E7D32", font=("Segoe UI", 14, "bold")
        )
        style.configure(
            "AnswerWrong.TLabel", foreground="#C62828", font=("Segoe UI", 14, "bold")
        )
        style.configure("Muted.TLabel", foreground="#666666", font=("Segoe UI", 12))

        style.configure("DescGray.TLabel", foreground="#7F7F7F", font=("Segoe UI", 10))
        style.configure("Small.TButton", font=("Segoe UI", 10))

        ttk.Label(
            self.frame,
            text="Quiz complete!",
            font=("Segoe UI", 12),
        ).grid(row=0, column=0, sticky="n", columnspan=2, pady=(0, 2))

        # Note: 1st -> GoldTitle, 2nd -> SilverTitle, 3rd -> BronzeTitle, rest -> BlackTitle
        # Also exclamation mark at end for 1st-3rd place
        ttk.Label(self.frame, text="You came 3rd!", style="BronzeTitle.TLabel").grid(
            row=1, column=0, sticky="n", columnspan=2
        )

        ttk.Separator(self.frame, orient="horizontal").grid(
            row=2, column=0, columnspan=2, sticky="ew", pady=10
        )

        self.content = ttk.Frame(self.frame)
        self.content.grid(row=3, column=0, columnspan=2, sticky="nsew")

        self.content.columnconfigure(0, weight=1, uniform="equal")
        self.content.columnconfigure(1, weight=0)
        self.content.columnconfigure(2, weight=1, uniform="equal")
        self.content.rowconfigure(0, weight=1)

        left = ttk.Frame(self.content)
        left.grid(row=0, column=0, sticky="nsew", padx=(40, 0))

        ttk.Label(
            left,
            text="Summary",
            font=("Segoe UI", 18, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(10, 0))

        ttk.Label(left, text="Nickname: Viradex", style="DescGray.TLabel").grid(
            row=1, column=0, sticky="w", pady=(2, 20)
        )

        ttk.Label(left, text="Place: #3", font=("Segoe UI", 14)).grid(
            row=2, column=0, sticky="w", pady=(0, 5)
        )
        ttk.Label(left, text="Points: 1000", font=("Segoe UI", 14)).grid(
            row=3, column=0, sticky="w", pady=(0, 5)
        )
        ttk.Label(left, text="Correct: 1 / 2", font=("Segoe UI", 14)).grid(
            row=4, column=0, sticky="w", pady=(0, 5)
        )
        ttk.Label(left, text="Accuracy: 50%", font=("Segoe UI", 14)).grid(
            row=5, column=0, sticky="w", pady=(0, 5)
        )

        sep = ttk.Separator(self.content, orient="vertical")
        sep.grid(row=0, column=1, sticky="ns")

        right = ttk.Frame(self.content)
        right.grid(row=0, column=2, sticky="nsew", padx=(40, 0))

        right.columnconfigure(0, weight=0)
        right.columnconfigure(1, weight=0)
        right.rowconfigure(2, weight=1)

        ttk.Label(
            right,
            text="Questions",
            font=("Segoe UI", 18, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(10, 0))

        ttk.Label(
            right, text="Select question for recap", style="DescGray.TLabel"
        ).grid(row=1, column=0, sticky="w", pady=(2, 20))

        self.tree = ttk.Treeview(right, show="tree", selectmode="browse", height=8)
        self.tree.grid(row=2, column=0, sticky="ns")
        self.tree.column("#0", width=200, stretch=False)

        self.tree.tag_configure("correct", foreground="#196B24")
        self.tree.tag_configure("wrong", foreground="#C00000")

        scroll = ttk.Scrollbar(right, orient="vertical", command=self.tree.yview)
        scroll.grid(row=2, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scroll.set)

        self.tree.insert("", "end", text="Q1  ✓", tags=("correct",))
        self.tree.insert("", "end", text="Q2  ✗", tags=("wrong",))

        ttk.Separator(self.frame, orient="horizontal").grid(
            row=4, column=0, columnspan=2, sticky="ew", pady=10
        )

        recap = ttk.Frame(self.frame)
        recap.grid(row=5, column=0, columnspan=2, sticky="nsew", padx=(40, 0))

        recap.columnconfigure(0, weight=1, uniform="equal")
        recap.columnconfigure(1, weight=1, uniform="equal")

        ttk.Label(
            recap,
            text="Recap (Q1)",
            font=("Segoe UI", 18, "bold"),
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(
            recap,
            text="What is 2 + 2?",
            font=("Segoe UI", 14),
            wraplength=400,
        ).grid(row=1, column=0, rowspan=2, sticky="w", pady=(5, 0))

        ttk.Label(recap, text="Result: +1000", font=("Segoe UI", 10, "italic")).grid(
            row=0, column=1, sticky="w", padx=(20, 0)
        )

        ttk.Label(recap, text="Your answer: 4", style="AnswerCorrect.TLabel").grid(
            row=1, column=1, sticky="w", pady=2, padx=(20, 0)
        )

        ttk.Label(recap, text="Correct answer: 4", style="Muted.TLabel").grid(
            row=2, column=1, sticky="w", padx=(20, 0)
        )

        ttk.Button(
            recap,
            text="Return to Menu",
            style="Small.TButton",
            padding=(2, 2),
            width=15,
        ).grid(row=0, column=1, sticky="ne")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    FinalResult().run()
