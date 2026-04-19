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

        style.configure("Gray.TLabel", foreground="#A7A7A7", font=("Segoe UI", 14))
        style.configure(
            "NicknameGray.TLabel", foreground="#6E6E6E", font=("Segoe UI", 12)
        )
        style.configure("Small.TButton", font=("Segoe UI", 10))

        ttk.Label(
            self.frame,
            text="Question 1 / 2",
            font=("Segoe UI", 12),
        ).grid(row=0, column=0, sticky="n", columnspan=2, pady=(0, 2))

        ttk.Label(self.frame, text="Correct! +1000", style="CorrectTitle.TLabel").grid(
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

        left.columnconfigure(0, weight=1)
        left.rowconfigure(8, weight=1)

        ttk.Label(
            left,
            text="Question Review",
            font=("Segoe UI", 14, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(30, 0))

        ttk.Label(left, text="What is 2 + 2?", style="Question.TLabel").grid(
            row=1, column=0, sticky="w", pady=(10, 20)
        )

        ttk.Label(left, text="A) 3", style="AnswerRed.TLabel").grid(
            row=2, column=0, sticky="w"
        )
        ttk.Label(left, text="B) 4", style="AnswerBlue.TLabel").grid(
            row=3, column=0, sticky="w"
        )
        ttk.Label(left, text="C) 5", style="AnswerYellow.TLabel").grid(
            row=4, column=0, sticky="w"
        )
        ttk.Label(left, text="D) 6", style="AnswerGreen.TLabel").grid(
            row=5, column=0, sticky="w"
        )

        ttk.Label(left, text="✓ Your answer: B", style="CorrectAnswer.TLabel").grid(
            row=6, column=0, sticky="w", pady=(20, 5)
        )
        # TODO this is here for demonstrational purposes
        # if the answer is already correct, this will be hidden
        ttk.Label(
            left, text="✓ Correct answer: B", style="CorrectAnswer.TLabel"
        ).grid_forget()
        # .grid(row=7, column=0, sticky="w")

        ttk.Label(left, text="Nickname: Viradex", style="NicknameGray.TLabel").grid(
            row=8, column=0, sticky="sw", pady=(30, 0)
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
        ).grid(row=0, column=0, sticky="w", pady=(30, 0))

        ttk.Label(
            right,
            text="Score: 1000",
            font=("Segoe UI", 14),
        ).grid(row=1, column=0, sticky="w", pady=(20, 0))

        ttk.Label(
            right,
            text="Place: #1",
            font=("Segoe UI", 14),
        ).grid(row=2, column=0, sticky="w", pady=(5, 0))

        ttk.Label(
            right,
            text="Waiting for next question...",
            style="Gray.TLabel",
        ).grid(row=3, column=0, sticky="w", pady=(50, 0))

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
    MultiResult().run()
