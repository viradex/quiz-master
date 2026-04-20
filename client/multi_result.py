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
        style.configure("Success.TLabel", foreground=COLOR_SUCCESS)
        style.configure("Error.TLabel", foreground=COLOR_ERROR)

        style.configure("Question.TLabel", foreground=COLOR_DARK_GRAY, font=FONT_LARGE)
        style.configure("AnswerA.TLabel", foreground=COLOR_RED, font=FONT_ANSWER)
        style.configure("AnswerB.TLabel", foreground=COLOR_BLUE, font=FONT_ANSWER)
        style.configure("AnswerC.TLabel", foreground=COLOR_YELLOW, font=FONT_ANSWER)
        style.configure("AnswerD.TLabel", foreground=COLOR_GREEN, font=FONT_ANSWER)

        style.configure("Muted.TLabel", foreground=COLOR_GRAY)
        style.configure("Subtle.TLabel", foreground=COLOR_DARK_GRAY)

        style.configure("Small.TButton", font=FONT_SMALL)

        self.question_num = ttk.Label(
            self.frame,
            text="Question 1 / 2",
            font=FONT_MEDIUM,
        )
        self.question_num.grid(row=0, column=0, sticky="n", columnspan=2, pady=(0, 2))

        self.result = ttk.Label(
            self.frame, text="Correct! +1000", style="Success.TLabel", font=FONT_TITLE
        )
        self.result.grid(row=1, column=0, sticky="n", columnspan=2)

        ttk.Separator(self.frame, orient="horizontal").grid(
            row=2, column=0, columnspan=2, sticky="ew", pady=10
        )

        content = ttk.Frame(self.frame)
        content.grid(row=3, column=0, columnspan=2, sticky="nsew")

        content.columnconfigure(0, weight=5)
        content.columnconfigure(2, weight=1)
        content.rowconfigure(0, weight=1)

        left = ttk.Frame(content)
        left.grid(row=0, column=0, sticky="nsew", padx=(40, 0))

        left.columnconfigure(0, weight=1)
        left.rowconfigure(8, weight=1)

        ttk.Label(left, text="Question Review", font=FONT_SM_HEADER).grid(
            row=0, column=0, sticky="w", pady=(10, 0)
        )

        self.question_text = ttk.Label(
            left, text="What is 2 + 2?", style="Question.TLabel"
        )
        self.question_text.grid(row=1, column=0, sticky="w", pady=(10, 20))

        self.answer_a = ttk.Label(left, text="A) 3", style="AnswerA.TLabel")
        self.answer_a.grid(row=2, column=0, sticky="w")

        self.answer_b = ttk.Label(left, text="B) 4", style="AnswerB.TLabel")
        self.answer_b.grid(row=3, column=0, sticky="w")

        self.answer_c = ttk.Label(left, text="C) 5", style="AnswerC.TLabel")
        self.answer_c.grid(row=4, column=0, sticky="w")

        self.answer_d = ttk.Label(left, text="D) 6", style="AnswerD.TLabel")
        self.answer_d.grid(row=5, column=0, sticky="w")

        self.player_answer = ttk.Label(
            left,
            text="✓ Your answer: B",
            style="Success.TLabel",
            font=FONT_FEEDBACK,
        )
        self.player_answer.grid(row=6, column=0, sticky="w", pady=(20, 5))

        # TODO this is here for demonstrational purposes
        # if the answer is already correct, this will be hidden
        self.correct_answer = ttk.Label(
            left,
            text="✓ Correct answer: B",
            style="Success.TLabel",
            font=FONT_FEEDBACK,
        )
        self.correct_answer.grid_forget()
        # self.correct_answer.grid(row=7, column=0, sticky="w")

        self.nickname = ttk.Label(
            left, text="Nickname: Viradex", style="Subtle.TLabel", font=FONT_MEDIUM
        )
        self.nickname.grid(row=8, column=0, sticky="sw", pady=(30, 0))

        sep = ttk.Separator(content, orient="vertical")
        sep.grid(row=0, column=1, sticky="ns")

        right = ttk.Frame(content)
        right.grid(row=0, column=2, sticky="nsew", padx=(40, 0))

        right.columnconfigure(0, weight=1)
        right.rowconfigure(4, weight=1)

        ttk.Label(
            right,
            text="Your Progress",
            font=FONT_HEADER,
        ).grid(row=0, column=0, sticky="w", pady=(10, 0))

        self.score = ttk.Label(
            right,
            text="Score: 1000",
            font=FONT_BODY,
        )
        self.score.grid(row=1, column=0, sticky="w", pady=(20, 0))

        self.place = ttk.Label(
            right,
            text="Place: #1",
            font=FONT_BODY,
        )
        self.place.grid(row=2, column=0, sticky="w", pady=(5, 0))

        ttk.Label(
            right,
            text="Waiting for next question...",
            style="Muted.TLabel",
            font=FONT_SMALL,
        ).grid(row=3, column=0, sticky="w", pady=(20, 0))

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
