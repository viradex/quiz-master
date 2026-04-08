import tkinter as tk
from tkinter import ttk

KONAMI_CODE = [
    "Up",
    "Up",
    "Down",
    "Down",
    "Left",
    "Right",
    "Left",
    "Right",
    "b",
    "a",
    "Return",
]

license_contents = """MIT License

Copyright (c) 2026 Viradex

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

cat_contents = r"""Will I get extra marks for this cat hes so cute

|\---/|
| o_o |
 \_^_/
"""


class App:
    def __init__(self):
        self.sequence = []

        self.root = tk.Tk()
        self.root.title("Quiz Master — About")
        self.root.geometry("1000x600")
        self.root.minsize(800, 600)

        self.notebook = ttk.Notebook(self.root, padding=(2, 0))
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.about_frame = ttk.Frame(self.notebook)
        self.help_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.about_frame, text="About")
        self.notebook.add(self.help_frame, text="Help")

        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        ttk.Label(
            self.about_frame,
            text="About Quiz Master",
            font=("Segoe UI", 16, "bold"),
        ).grid(row=0, column=0, sticky="W", pady=(10, 0), padx=10)

        ttk.Label(
            self.about_frame,
            text="Developed and coded from start to finish by Arnav Thorat :)",
            font=("Segoe UI", 12),
        ).grid(row=1, column=0, sticky="W", pady=(5, 0), padx=10)

        ttk.Label(
            self.about_frame,
            text="This app requires local network access. No personal identifiable information is shared to any first-party or third-party services.",
            font=("Segoe UI", 10),
        ).grid(row=2, column=0, sticky="W", pady=(15, 10), padx=10)

        self.license_text = tk.Text(
            self.about_frame, wrap="word", height=25, width=80, state="normal"
        )
        self.license_text.insert("end", license_contents)
        self.license_text.configure(state=tk.DISABLED)
        self.license_text.grid(row=3, column=0, sticky="nsew", pady=(0, 15), padx=10)

        self.root.bind("<Key>", self.key_pressed)

    def key_pressed(self, event):
        key = event.keysym

        if key in ["Up", "Down", "Left", "Right"]:
            pass
        elif len(key) == 1:
            key = key.lower()

        self.sequence.append(key)

        if len(self.sequence) > len(KONAMI_CODE):
            self.sequence.pop(0)

        if self.sequence == KONAMI_CODE:
            self.better_license()
            self.sequence.clear()

    def better_license(self):
        self.license_text.configure(state=tk.NORMAL)
        self.license_text.delete(1.0, "end")
        self.license_text.insert("end", cat_contents)
        self.license_text.configure(state=tk.DISABLED)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    App().run()
