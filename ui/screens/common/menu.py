from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal

from core.app.screen_ids import Screens
from ui.screens.base_screen import BaseScreen


# TODO Make menu look prettier, right now it's mostly a placeholder screen
class CommonMenuScreen(BaseScreen):
    started_server = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setup_ui()

    def setup_ui(self) -> None:
        ## FONTS SETUP ##
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)

        desc_font = QFont()
        desc_font.setPointSize(14)

        ## WIDGETS SETUP ##
        title = QLabel("Welcome to Quiz Master!")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(title_font)

        desc = QLabel("Select game mode:")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setFont(desc_font)

        self.client_btn = QPushButton("Join as Client")
        self.client_btn.setFixedSize(275, 60)
        self.client_btn.setStyleSheet("font-size: 22px;")
        self.client_btn.clicked.connect(lambda: self.go_to(Screens.CLIENT_SETUP))

        self.server_btn = QPushButton("Start as Server")
        self.server_btn.setFixedSize(275, 60)
        self.server_btn.setStyleSheet("font-size: 22px;")
        self.server_btn.clicked.connect(self.on_start_server)

        self.manage_quizzes_btn = QPushButton("Manage Quizzes")
        self.manage_quizzes_btn.setFixedSize(275, 45)
        self.manage_quizzes_btn.setStyleSheet("font-size: 16px;")
        self.manage_quizzes_btn.clicked.connect(
            lambda: self.go_to(Screens.COMMON_QUIZ_MANAGER)
        )

        self.about_btn = QPushButton("About")
        self.about_btn.setFixedSize(135, 35)
        self.about_btn.setStyleSheet("font-size: 12px;")
        self.about_btn.clicked.connect(lambda: self.go_to(Screens.COMMON_ABOUT))

        self.exit_btn = QPushButton("Exit")
        self.exit_btn.setFixedSize(135, 35)
        self.exit_btn.setStyleSheet("font-size: 12px;")
        self.exit_btn.clicked.connect(QApplication.exit)

        ## LAYOUTS SETUP ##
        small_btn_hbox = QHBoxLayout()
        small_btn_hbox.addStretch()
        small_btn_hbox.addWidget(self.about_btn)
        small_btn_hbox.addWidget(self.exit_btn)
        small_btn_hbox.addStretch()

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
        vbox.addLayout(small_btn_hbox)
        vbox.addStretch(2)

        self.setLayout(vbox)

    def on_start_server(self) -> None:
        self.started_server.emit()
