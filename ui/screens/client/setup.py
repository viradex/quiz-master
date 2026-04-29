from PyQt6.QtWidgets import (
    QLabel,
    QPushButton,
    QLineEdit,
    QSpacerItem,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QSizePolicy,
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from core.screen_ids import Screens
from ui.screens.base_screen import BaseScreen


class ClientSetupScreen(BaseScreen):
    title_text = "Quiz Master – Client Setup"

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setup_ui()

    def setup_ui(self):
        title_font = QFont()
        title_font.setPointSize(20)

        title = QLabel("Enter connection details:")
        title.setFont(title_font)

        form_font = QFont()
        form_font.setPointSize(14)

        # TODO add IP hint if users get confused in testing
        # something like "see server screen for IP"
        ip_lbl = QLabel("Server IP:")
        ip_lbl.setFont(form_font)
        ip_lbl.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)

        # TODO remove default value for prod
        self.ip_input = QLineEdit("127.0.0.1")
        self.ip_input.setFont(form_font)

        # TODO after prototype, make '7878' part dynamic
        self.port_lbl = QLabel("Connecting to port: 7878")
        self.port_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.port_lbl.setStyleSheet("font-size: 12px;" "color: #A7A7A7;")

        nickname_lbl = QLabel("Nickname:")
        nickname_lbl.setFont(form_font)
        nickname_lbl.setSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred
        )

        self.nickname_input = QLineEdit()
        self.nickname_input.setFont(form_font)

        form_layout = QFormLayout()
        form_layout.setHorizontalSpacing(25)

        form_layout.addRow(ip_lbl, self.ip_input)
        form_layout.addRow(self.port_lbl)
        form_layout.addItem(QSpacerItem(0, 10))
        form_layout.addRow(nickname_lbl, self.nickname_input)

        self.menu_btn = QPushButton("Return to Menu")
        self.menu_btn.setFixedSize(200, 45)
        self.menu_btn.setProperty("class", "medium_btn")
        self.menu_btn.clicked.connect(lambda: self.go_to(Screens.COMMON_MENU))

        self.join_btn = QPushButton("Join")
        self.join_btn.setFixedSize(240, 50)
        self.join_btn.setProperty("class", "large_btn")
        self.join_btn.clicked.connect(lambda: self.go_to(Screens.CLIENT_LOBBY))

        btn_hbox = QHBoxLayout()
        btn_hbox.addWidget(self.menu_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        btn_hbox.addWidget(self.join_btn, alignment=Qt.AlignmentFlag.AlignRight)

        self.setStyleSheet("""
            QPushButton[class="large_btn"] {
                font-size: 22px;
            }
            QPushButton[class="medium_btn"] {
                font-size: 16px;
            }
""")

        vbox = QVBoxLayout()
        vbox.setContentsMargins(150, 0, 150, 0)

        vbox.addStretch(1)
        vbox.addWidget(title)

        vbox.addSpacing(50)
        vbox.addLayout(form_layout)

        vbox.addSpacing(40)
        vbox.addLayout(btn_hbox)

        vbox.addStretch(2)

        self.setLayout(vbox)
