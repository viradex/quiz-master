# Entry field question screen
# TODO This and MultiQuestion should be merged
import tkinter as tk
from tkinter import ttk
from pathlib import Path

from constants import *


class EntryQuestion:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Quiz Master — Question 2 / 2")
        self.root.geometry(WINDOW_GEOMETRY)
        self.root.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        self.frame = ttk.Frame(self.root, padding=40)
        self.frame.grid(row=0, column=0, sticky="nsew")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(2, weight=1)

        style = ttk.Style()
        style.configure("Subtle.TLabel", foreground=COLOR_DARK_GRAY)

        style.configure("Large.TButton", font=FONT_LARGE)
        style.configure("Small.TButton", font=FONT_SMALL)

        self.question_num = ttk.Label(
            self.frame,
            text="Question 2 / 2",
            font=FONT_MEDIUM,
        )
        self.question_num.grid(row=0, column=0, sticky="sw", padx=(40, 0), pady=(10, 2))

        self.question_text = ttk.Label(
            self.frame,
            text="Name a primary color",
            font=FONT_QUESTION,
            wraplength=WRAP_QUESTION,  # TODO add responsiveness for wrap length when resizing window AND possibly font size change
        )
        self.question_text.grid(
            row=1, column=0, sticky="nw", padx=(40, 0), pady=(2, 10)
        )

        timer_frame = ttk.Frame(self.frame)
        timer_frame.grid(row=0, column=1, rowspan=2, sticky="ne", padx=(0, 60))

        BASE_DIR = Path(__file__).resolve().parent.parent
        img_path = BASE_DIR / "assets" / "timer.png"
        self.timer_img = tk.PhotoImage(file=img_path)

        ttk.Label(timer_frame, image=self.timer_img).grid(row=0, column=0, sticky="n")

        self.timer_secs = ttk.Label(
            timer_frame,
            text="5",
            font=FONT_HUGE,
            foreground=COLOR_ERROR,
        )
        self.timer_secs.grid(row=1, column=0, sticky="n", pady=0)

        self.timer_secs_text = ttk.Label(
            timer_frame,
            text="seconds left",
            font=FONT_SMALL,
            foreground=COLOR_ERROR,
        )
        self.timer_secs_text.grid(row=2, column=0, sticky="n", pady=0)

        answer_frame = ttk.Frame(self.frame, padding=(40, 10))
        answer_frame.grid(row=2, column=0, columnspan=2, sticky="nsew")

        answer_frame.columnconfigure(0, weight=1)

        ttk.Label(
            answer_frame,
            text="Enter the answer in the input field on your screens",
            style="Subtle.TLabel",
            font=FONT_SMALL,
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))

        ttk.Entry(
            answer_frame,
            font=FONT_ANSWER_ENTRY,  # for making entry field taller
            width=40,
            state="readonly",
        ).grid(row=1, column=0, sticky="ew")

        self.responses = ttk.Label(
            self.frame,
            text="Responses: 1",
            font=FONT_MEDIUM,
        )
        self.responses.grid(row=3, column=0, sticky="sw", pady=(30, 0), padx=(40, 0))

        ttk.Button(
            self.frame,
            text="Skip Question",
            style="Small.TButton",
            padding=(8, 5),
            width=15,
        ).grid(row=3, column=1, sticky="ne", pady=(40, 0), padx=(0, 40))

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    EntryQuestion().run()
