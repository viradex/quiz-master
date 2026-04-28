from PyQt6.QtWidgets import QLabel, QVBoxLayout
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QTimer

from ui.screens.base_screen import BaseScreen


class CommonLoadingScreen(BaseScreen):
    title_text = "Quiz Master – Loading..."

    def __init__(self, parent=None):
        super().__init__(parent)

        self.frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.index = 0

        self.setup_ui()
        self.setup_timer()

    def setup_ui(self):
        loading_font = QFont()
        loading_font.setPointSize(32)

        self.loading_lbl = QLabel(f"{self.frames[0]} Loading...")
        self.loading_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_lbl.setFont(loading_font)

        self.status_lbl = QLabel("Preparing game...")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_lbl.setStyleSheet("color: #888888;" "font-size: 22px;")

        vbox = QVBoxLayout()
        vbox.addStretch()
        vbox.addWidget(self.loading_lbl)
        vbox.addSpacing(10)
        vbox.addWidget(self.status_lbl)
        vbox.addStretch()

        self.setLayout(vbox)

    def setup_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_spinner)
        self.timer.setInterval(90)

    def update_spinner(self):
        frame = self.frames[self.index]

        self.loading_lbl.setText(f"{frame} Loading...")
        self.index = (self.index + 1) % len(self.frames)

    def on_enter(self):
        self.index = 0
        self.timer.start()
        self.update_spinner()

    def on_leave(self):
        self.timer.stop()
        self.loading_lbl.setText(f"{self.frames[0]} Loading...")
