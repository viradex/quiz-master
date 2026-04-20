# Multi-choice question screen
import tkinter as tk
from tkinter import ttk
from pathlib import Path

from constants import *


class MultiQuestion:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Quiz Master — Question 1 / 2")
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

        style.configure("Small.TButton", font=FONT_SMALL)

        self.question_num = ttk.Label(
            self.frame,
            text="Question 1 / 2",
            font=FONT_MEDIUM,
        )
        self.question_num.grid(row=0, column=0, sticky="sw", padx=(40, 0), pady=(10, 2))

        self.question_text = ttk.Label(
            self.frame,
            text="What is 2 + 2?",
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

        self.timer_secs = ttk.Label(timer_frame, text="10", font=FONT_HUGE)
        self.timer_secs.grid(row=1, column=0, sticky="n", pady=0)

        self.timer_secs_text = ttk.Label(
            timer_frame, text="seconds left", font=FONT_SMALL
        )
        self.timer_secs_text.grid(row=2, column=0, sticky="n", pady=0)

        colors = {
            "red": "#E74C3C",
            "blue": "#3498DB",
            "yellow": "#F1C40F",
            "green": "#2ECC71",
        }

        answer_frame = ttk.Frame(self.frame)
        answer_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(20, 0))

        answer_frame.columnconfigure(0, weight=1, uniform="equal")
        answer_frame.columnconfigure(1, weight=1, uniform="equal")
        answer_frame.rowconfigure(1, weight=1)
        answer_frame.rowconfigure(2, weight=1)

        ttk.Label(
            answer_frame,
            text="Enter the answer on your screens",
            style="Subtle.TLabel",
            font=FONT_MEDIUM,
        ).grid(row=0, column=0, sticky="sw", pady=(0, 5), padx=(40, 0))

        # TODO improve contrast for yellow btn, white text can be hard to read
        # maybe switch text to black, but black text breaks consistency
        # or make bg darker, see colors dict above
        red_btn = self.create_answer_button(answer_frame, "3", colors["red"])
        blue_btn = self.create_answer_button(answer_frame, "4", colors["blue"])
        yellow_btn = self.create_answer_button(answer_frame, "5", colors["yellow"])
        green_btn = self.create_answer_button(answer_frame, "6", colors["green"])

        red_btn.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        blue_btn.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        yellow_btn.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
        green_btn.grid(row=2, column=1, padx=5, pady=5, sticky="nsew")

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

    def create_answer_button(self, parent, text, bg):
        btn = tk.Button(
            parent,
            text=text,
            bg=bg,
            disabledforeground="white",
            font=(FONT_FAMILY, 20, "bold"),
            bd=0,
            relief="flat",
            highlightthickness=0,
            padx=20,
            pady=18,
            state="disabled",
        )

        return btn

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    MultiQuestion().run()
