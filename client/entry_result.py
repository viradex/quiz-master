# Entry results screen
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
            "CorrectTitle.TLabel", foreground="#196B24", font=("Segoe UI", 24, "bold")
        )
        style.configure(
            "IncorrectTitle.TLabel", foreground="#C00000", font=("Segoe UI", 24, "bold")
        )

        style.configure("Question.TLabel", foreground="#7F7F7F", font=("Segoe UI", 16))
        style.configure(
            "WrongAnswer.TLabel", foreground="#C00000", font=("Segoe UI", 16, "bold")
        )
        style.configure(
            "CorrectAnswer.TLabel", foreground="#196B24", font=("Segoe UI", 16, "bold")
        )

        style.configure("Gray.TLabel", foreground="#A7A7A7", font=("Segoe UI", 14))
        style.configure(
            "NicknameGray.TLabel", foreground="#6E6E6E", font=("Segoe UI", 12)
        )
        style.configure("Small.TButton", font=("Segoe UI", 10))

        ttk.Label(
            self.frame,
            text="Question 2 / 2",
            font=("Segoe UI", 12),
        ).grid(row=0, column=0, sticky="n", columnspan=2, pady=(0, 2))

        ttk.Label(self.frame, text="Incorrect! +0", style="IncorrectTitle.TLabel").grid(
            row=1, column=0, sticky="n", columnspan=2
        )

        ttk.Separator(self.frame, orient="horizontal").grid(
            row=2, column=0, columnspan=2, sticky="ew", pady=10
        )

        self.content = ttk.Frame(self.frame)
        self.content.grid(row=3, column=0, columnspan=2, sticky="nsew")

        self.content.columnconfigure(0, weight=5)
        self.content.columnconfigure(1, weight=0)
        self.content.columnconfigure(2, weight=1)
        self.content.rowconfigure(0, weight=1)

        left = ttk.Frame(self.content)
        left.grid(row=0, column=0, sticky="nsew", padx=(40, 0))

        # TODO very reptitive, maybe use different frames?
        left.columnconfigure(0, weight=1)
        left.rowconfigure(0, weight=0)
        left.rowconfigure(1, weight=0)
        left.rowconfigure(2, weight=0)
        left.rowconfigure(3, weight=0)
        left.rowconfigure(4, weight=1)

        ttk.Label(
            left,
            text="Question Review",
            font=("Segoe UI", 14, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(30, 0))

        ttk.Label(left, text="Name the primary colors", style="Question.TLabel").grid(
            row=1, column=0, sticky="w", pady=(10, 0)
        )

        ttk.Label(left, text="✗ Your answer: purple", style="WrongAnswer.TLabel").grid(
            row=2, column=0, sticky="w", pady=(30, 5)
        )
        ttk.Label(
            left,
            text="✓ Correct answer(s): red, yellow, blue",
            style="CorrectAnswer.TLabel",
        ).grid(row=3, column=0, sticky="w")

        ttk.Label(left, text="Nickname: Viradex", style="NicknameGray.TLabel").grid(
            row=4, column=0, sticky="sw", pady=(30, 0)
        )

        sep = ttk.Separator(self.content, orient="vertical")
        sep.grid(row=0, column=1, sticky="ns")

        right = ttk.Frame(self.content)
        right.grid(row=0, column=2, sticky="nsew", padx=(40, 0))

        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=0)
        right.rowconfigure(1, weight=0)
        right.rowconfigure(2, weight=0)
        right.rowconfigure(3, weight=0)
        right.rowconfigure(4, weight=1)

        ttk.Label(
            right,
            text="Your Progress",
            font=("Segoe UI", 18, "bold"),
        ).grid(row=0, column=0, sticky="n", pady=(30, 0))

        ttk.Label(
            right,
            text="Score: 1000",
            font=("Segoe UI", 16),
        ).grid(row=1, column=0, sticky="n", pady=(20, 0))

        ttk.Label(
            right,
            text="Place: #5",
            font=("Segoe UI", 16),
        ).grid(row=2, column=0, sticky="n", pady=(5, 0))

        ttk.Label(
            right,
            text="Waiting for next question...",
            style="Gray.TLabel",
        ).grid(row=3, column=0, sticky="n", pady=(50, 0))

        ttk.Button(
            right,
            text="Leave Game",
            style="Small.TButton",
            padding=(8, 5),
            width=15,
        ).grid(row=4, column=0, sticky="se")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    EntryResult().run()
