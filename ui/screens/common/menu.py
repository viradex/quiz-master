from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from core.screen_ids import Screens
from ui.screens.base_screen import BaseScreen
from ui.components.dialogs import not_implemented


class CommonMenuScreen(BaseScreen):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setup_ui()

    def setup_ui(self):
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)

        title = QLabel("Welcome to Quiz Master!")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(title_font)

        desc_font = QFont()
        desc_font.setPointSize(14)

        desc = QLabel("Select game mode:")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setFont(desc_font)

        self.client_btn = self._create_button("Join as Client", (275, 60), "large_btn")
        self.client_btn.clicked.connect(lambda: self.go_to(Screens.CLIENT_SETUP))
        self.server_btn = self._create_button("Start as Server", (275, 60), "large_btn")
        self.server_btn.clicked.connect(lambda: self.go_to(Screens.SERVER_LOBBY))

        self.manage_quizzes_btn = self._create_button(
            "Manage Quizzes", (275, 45), "medium_btn"
        )
        self.manage_quizzes_btn.clicked.connect(lambda: not_implemented(self))
        self.settings_btn = self._create_button(
            "Settings / Stats", (275, 45), "medium_btn"
        )
        self.settings_btn.clicked.connect(lambda: not_implemented(self))

        self.about_btn = self._create_button("About / Help", (135, 35), "small_btn")
        self.about_btn.clicked.connect(lambda: self.go_to(Screens.COMMON_ABOUT))
        self.exit_btn = self._create_button("Exit", (135, 35), "small_btn")
        self.exit_btn.clicked.connect(QApplication.exit)

        small_btn_hbox = QHBoxLayout()
        small_btn_hbox.addStretch()
        small_btn_hbox.addWidget(self.about_btn)
        small_btn_hbox.addWidget(self.exit_btn)
        small_btn_hbox.addStretch()

        self.setStyleSheet("""
            QPushButton[class="large_btn"] {
                font-size: 22px;
            }
            QPushButton[class="medium_btn"] {
                font-size: 16px;
            }
            QPushButton[class="small_btn"] {
                font-size: 12px;
            }
""")

        vbox = QVBoxLayout()
        vbox.setContentsMargins(40, 40, 40, 40)

        vbox.addStretch(1)
        vbox.addWidget(title)

        vbox.addSpacing(10)
        vbox.addWidget(desc)

        vbox.addSpacing(20)
        vbox.addWidget(self.client_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        vbox.addSpacing(5)
        vbox.addWidget(self.server_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        vbox.addSpacing(30)
        vbox.addWidget(self.manage_quizzes_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        vbox.addSpacing(5)
        vbox.addWidget(self.settings_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        vbox.addSpacing(30)
        vbox.addLayout(small_btn_hbox)

        vbox.addStretch(2)

        self.setLayout(vbox)

    def _create_button(self, text, size, qss_class):
        btn = QPushButton(text)
        btn.setFixedSize(*size)
        btn.setProperty("class", qss_class)
        return btn
