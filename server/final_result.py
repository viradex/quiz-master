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

        self.frame.rowconfigure(3, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)

        style = ttk.Style()
        style.configure(
            "BlackTitle.TLabel", foreground="#2E2E2E", font=("Segoe UI", 24, "bold")
        )

        style.configure("Treeview", font=("Segoe UI", 12), rowheight=30)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

        style.configure(
            "DescGray.TLabel", foreground="#7F7F7F", font=("Segoe UI", 10, "italic")
        )
        style.configure("Medium.TButton", font=("Segoe UI", 12))

        ttk.Label(
            self.frame,
            text="Quiz complete!",
            font=("Segoe UI", 12),
        ).grid(row=0, column=0, sticky="n", columnspan=2, pady=(0, 2))

        # Note: 1st -> GoldTitle, 2nd -> SilverTitle, 3rd -> BronzeTitle, rest -> BlackTitle
        # Also exclamation mark at end for 1st-3rd place
        ttk.Label(self.frame, text="Final Standings", style="BlackTitle.TLabel").grid(
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
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

        left.columnconfigure(0, weight=1)
        left.rowconfigure(2, weight=1)

        ttk.Label(
            left,
            text="Leaderboard",
            font=("Segoe UI", 18, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(10, 0))

        ttk.Label(left, text="All players ranked", style="DescGray.TLabel").grid(
            row=1, column=0, sticky="w", pady=(2, 20)
        )

        tree = ttk.Treeview(left, columns=("place", "name", "total"), show="headings")
        tree.tag_configure("gold", foreground="#D4AF37", font=("Segoe UI", 12, "bold"))
        tree.tag_configure(
            "silver", foreground="#B0B0B0", font=("Segoe UI", 12, "bold")
        )
        tree.tag_configure(
            "bronze", foreground="#CD7F32", font=("Segoe UI", 12, "bold")
        )

        tree.heading("place", text="Place")
        tree.heading("name", text="Name")
        tree.heading("total", text="Total")

        tree.column("place", anchor="center", width=50)
        tree.column("name", anchor="center", width=200)
        tree.column("total", anchor="center", width=50)

        scroll = ttk.Scrollbar(left, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)

        tree.grid(row=2, column=0, sticky="nsew")
        scroll.grid(row=2, column=1, sticky="ns")

        # TODO for prototype only
        players = (
            ("#1", "Peptalker101", "1837"),
            ("#2", "ItsJakePlayz21", "1835"),
            ("#3", "Viradex", "1000"),
            ("#4", "TrexGamerGirl", "972"),
            ("#5", "Scyrist", "968"),
        )
        for player in players:
            if player[0] == "#1":
                tree.insert("", "end", values=player, tags=("gold",))
            elif player[0] == "#2":
                tree.insert("", "end", values=player, tags=("silver",))
            elif player[0] == "#3":
                tree.insert("", "end", values=player, tags=("bronze",))
            else:
                tree.insert("", "end", values=player)

        sep = ttk.Separator(self.content, orient="vertical")
        sep.grid(row=0, column=1, sticky="ns")

        right = ttk.Frame(self.content)
        right.grid(row=0, column=2, sticky="nsew", padx=(20, 0))

        right.columnconfigure(0, weight=1)
        right.rowconfigure(5, weight=1)

        ttk.Label(
            right,
            text="Game Summary",
            font=("Segoe UI", 18, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(10, 0))

        ttk.Label(right, text="Session stats", style="DescGray.TLabel").grid(
            row=1, column=0, sticky="w", pady=(2, 20)
        )

        ttk.Label(right, text="Players: 5", font=("Segoe UI", 11)).grid(
            row=2, column=0, sticky="w", pady=(0, 6)
        )
        ttk.Label(right, text="Questions: 2", font=("Segoe UI", 11)).grid(
            row=3, column=0, sticky="w", pady=(0, 6)
        )
        ttk.Label(
            right, text="Winner: Peptalker101 (1837 pts)", font=("Segoe UI", 11, "bold")
        ).grid(row=4, column=0, sticky="w", pady=(0, 6))

        ttk.Button(
            right,
            text="Back to Menu",
            style="Medium.TButton",
            padding=(8, 5),
            width=15,
        ).grid(row=5, column=0, sticky="se")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    FinalResult().run()
