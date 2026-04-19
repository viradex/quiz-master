# Entry field question screen
# TODO This and MultiQuestion should be merged
import tkinter as tk
from tkinter import ttk
from pathlib import Path


class EntryQuestion:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Quiz Master — Question 2 / 2")
        self.root.geometry("1000x600")
        self.root.minsize(800, 600)

        self.frame = ttk.Frame(self.root, padding=40)
        self.frame.grid(row=0, column=0, sticky="nsew")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(0, weight=0)
        self.frame.rowconfigure(1, weight=0)
        self.frame.rowconfigure(2, weight=1)
        self.frame.rowconfigure(3, weight=0)

        self.answer_var = tk.StringVar()

        style = ttk.Style()
        style.configure("Small.TButton", font=("Segoe UI", 10))
        style.configure("Big.TButton", font=("Segoe UI", 16))
        style.configure("Red.TLabel", foreground="#C0392B", font=("Segoe UI", 20))
        style.configure("RedSmall.TLabel", foreground="#C0392B", font=("Segoe UI", 10))
        style.configure("Gray.TLabel", foreground="#828790", font=("Segoe UI", 10))

        ttk.Label(
            self.frame,
            text="Question 2 / 2",
            font=("Segoe UI", 12),
        ).grid(row=0, column=0, sticky="sw", padx=(40, 0), pady=(10, 2))

        ttk.Label(
            self.frame,
            text="Name a primary color",
            font=("Segoe UI", 28, "bold"),
            wraplength=750,  # TODO add responsiveness for wrap length when resizing window AND possibly font size change
        ).grid(row=1, column=0, sticky="nw", padx=(40, 0), pady=(2, 10))

        timer_frame = ttk.Frame(self.frame)
        timer_frame.grid(row=0, column=1, rowspan=2, sticky="ne", padx=(0, 60))

        BASE_DIR = Path(__file__).resolve().parent.parent
        img_path = BASE_DIR / "assets" / "timer.png"
        self.timer_img = tk.PhotoImage(file=img_path)

        ttk.Label(timer_frame, image=self.timer_img).grid(row=0, column=0, sticky="n")
        ttk.Label(timer_frame, text="5", style="Red.TLabel").grid(
            row=1, column=0, sticky="n", pady=0
        )
        ttk.Label(timer_frame, text="seconds left", style="RedSmall.TLabel").grid(
            row=2, column=0, sticky="n", pady=0
        )

        answer_frame = ttk.Frame(self.frame, padding=(40, 10))
        answer_frame.grid(row=2, column=0, columnspan=2, sticky="nsew")

        answer_frame.columnconfigure(0, weight=1)

        ttk.Label(
            answer_frame, text="Enter your answer here:", style="Gray.TLabel"
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))

        ttk.Entry(
            answer_frame, textvariable=self.answer_var, font=("Segoe UI", 24), width=40
        ).grid(row=1, column=0, sticky="ew")

        ttk.Button(
            answer_frame,
            text="Submit",
            style="Big.TButton",
            padding=(50, 10),
        ).grid(row=2, column=0, sticky="w", pady=(20, 0))

        ttk.Label(
            self.frame,
            text="Not submitted!",
            font=("Segoe UI", 12),
        ).grid(row=3, column=0, sticky="sw", pady=(30, 0), padx=(40, 0))

        ttk.Button(
            self.frame,
            text="Leave Game",
            style="Small.TButton",
            padding=(8, 5),
            width=15,
        ).grid(row=3, column=1, sticky="ne", pady=(40, 0), padx=(0, 40))

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    EntryQuestion().run()
