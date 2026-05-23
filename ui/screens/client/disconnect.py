from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from ui.screens.base_screen import BaseScreen
from core.screen_ids import Screens


class ClientDisconnectScreen(BaseScreen):
    title_text = "Quiz Master – Disconnected"

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setup_ui()

    def setup_ui(self):
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)

        title = QLabel("Disconnected")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(title_font)

        desc = QLabel("You have been disconnected from the server.")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("font-size: 16px;" "color: #6E6E6E;")

        reason_font = QFont()
        reason_font.setPointSize(16)

        self.reason = QLabel("Reason: Kicked by host")
        self.reason.setWordWrap(True)
        self.reason.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.reason.setFont(reason_font)

        self.return_btn = QPushButton("Return to Menu")
        self.return_btn.setFixedSize(275, 60)
        self.return_btn.clicked.connect(lambda: self.go_to(Screens.COMMON_MENU))
        self.return_btn.setStyleSheet("font-size: 22px;")

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(title)
        vbox.addSpacing(5)
        vbox.addWidget(desc)
        vbox.addSpacing(10)
        vbox.addWidget(self.reason)
        vbox.addSpacing(40)
        vbox.addWidget(self.return_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        vbox.addStretch(1)

        self.setLayout(vbox)
