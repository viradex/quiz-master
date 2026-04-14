# Lobby screen
import tkinter as tk
from tkinter import ttk


class Lobby:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Quiz Master — Lobby")
        self.root.geometry("1000x600")
        self.root.minsize(800, 600)

        self.frame = ttk.Frame(self.root, padding=40)
        self.frame.grid(row=0, column=0, sticky="nsew")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.frame.columnconfigure(0, weight=0)
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(0, weight=0)
        self.frame.rowconfigure(1, weight=0)
        self.frame.rowconfigure(2, weight=1)
        self.frame.rowconfigure(3, weight=0)

        style = ttk.Style()
        style.configure("Small.TButton", font=("Segoe UI", 8))
        style.configure("Treeview", font=("Segoe UI", 12), rowheight=30)
        style.configure("Gray.TLabel", foreground="#A7A7A7", font=("Segoe UI", 10))

        ttk.Label(
            self.frame,
            text="Lobby",
            font=("Segoe UI", 24, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=(40, 0))

        ttk.Label(
            self.frame,
            text="Players: 5/16",
            font=("Segoe UI", 12),
        ).grid(row=1, column=0, sticky="w", pady=(5, 0), padx=(40, 0))

        # Treeview container frame (important for proper layout)
        tree_frame = ttk.Frame(self.frame)
        tree_frame.grid(row=2, column=0, sticky="nsew", pady=(20, 0), padx=(40, 0))

        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.tree = ttk.Treeview(
            tree_frame,
            show="tree",
            height=20,
            selectmode="browse",
            yscrollcommand=scrollbar.set,
        )

        self.tree.column("#0", width=250, anchor="center", stretch=True)
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.tag_configure("you", font=("Segoe UI", 12, "bold"))

        # FOR PROTOTYPE ONLY
        players = (
            "Viradex (you)",
            "Peptalker101",
            "TrexGamerGirl",
            "Scyrist",
            "ItsJakePlayz21",
        )
        for player in players:
            if player.endswith("(you)"):
                self.tree.insert("", "end", text=player, tags=("you",))
            else:
                self.tree.insert("", "end", text=player)

        scrollbar.config(command=self.tree.yview)

        ttk.Label(
            self.frame,
            text="Connected to 127.0.0.1:7878",
            font=("Segoe UI", 8),
        ).grid(row=3, column=0, sticky="sw", pady=(30, 0), padx=(40, 0))

        progress_frame = ttk.Frame(self.frame)
        progress_frame.grid(row=2, column=1, sticky="nsew")
        progress_frame.columnconfigure(0, weight=1)

        ttk.Label(
            progress_frame,
            text="Waiting for the host to start the game...",
            font=("Segoe UI", 16),
            justify="center",
            anchor="center",
        ).grid(row=0, column=0, sticky="ew", pady=(20, 5), padx=(50, 10))

        progress = ttk.Progressbar(progress_frame, mode="indeterminate", length=500)
        progress.grid(row=1, column=0, sticky="ew", pady=(5, 0), padx=(50, 10))
        progress.start(20)

        ttk.Label(
            progress_frame,
            text="Connected to server. Game will begin shortly.",
            style="Gray.TLabel",
            justify="center",
            anchor="center",
        ).grid(row=2, column=0, sticky="ew", pady=(10, 0), padx=(50, 10))

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
    Lobby().run()
