from PyQt6.QtWidgets import (
    QLabel,
    QPushButton,
    QLineEdit,
    QSpacerItem,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QSizePolicy,
    QMessageBox,
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal

from core.app.screen_ids import Screens
from ui.screens.base_screen import BaseScreen
from utils.networking import is_valid_ipv4
from core.config.constants import DEFAULT_IP_ADDRESS, PORT, MAX_NICKNAME_LENGTH


class ClientSetupScreen(BaseScreen):
    title_text = "Quiz Master – Client Setup"

    submitted = pyqtSignal(dict)

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

        self.ip_input = QLineEdit(DEFAULT_IP_ADDRESS)
        self.ip_input.setFont(form_font)
        self.ip_input.returnPressed.connect(self.on_submit)

        self.port_lbl = QLabel(f"Connecting to port: {PORT}")
        self.port_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.port_lbl.setStyleSheet("font-size: 12px;" "color: #A7A7A7;")

        nickname_lbl = QLabel("Nickname:")
        nickname_lbl.setFont(form_font)
        nickname_lbl.setSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred
        )

        self.nickname_input = QLineEdit()
        self.nickname_input.setFont(form_font)
        self.nickname_input.returnPressed.connect(self.on_submit)

        form_layout = QFormLayout()
        form_layout.setHorizontalSpacing(25)

        form_layout.addRow(ip_lbl, self.ip_input)
        form_layout.addRow(self.port_lbl)
        form_layout.addItem(QSpacerItem(0, 10))
        form_layout.addRow(nickname_lbl, self.nickname_input)

        self.menu_btn = QPushButton("Return to Menu")
        self.menu_btn.setFixedSize(200, 45)
        self.menu_btn.setStyleSheet("font-size: 16px;")
        self.menu_btn.clicked.connect(self.on_return)

        self.join_btn = QPushButton("Join")
        self.join_btn.setFixedSize(240, 50)
        self.join_btn.setStyleSheet("font-size: 22px;")
        self.join_btn.clicked.connect(self.on_submit)

        btn_hbox = QHBoxLayout()
        btn_hbox.addWidget(self.menu_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        btn_hbox.addWidget(self.join_btn, alignment=Qt.AlignmentFlag.AlignRight)

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

    def on_submit(self):
        data = {
            "ip": self.ip_input.text().strip(),
            "nickname": self.nickname_input.text().strip(),
        }

        if not self.validate_data():
            return

        self.submitted.emit(data)

    def on_return(self):
        self.ip_input.setText(DEFAULT_IP_ADDRESS)
        self.nickname_input.setText("")

        self.go_to(Screens.COMMON_MENU)

    def validate_data(self):
        ip_address = self.ip_input.text().strip()
        nickname = self.nickname_input.text().strip()

        if not ip_address or not nickname:
            QMessageBox.critical(
                self,
                "Empty Fields",
                "Please ensure all fields are filled in and try again.",
            )
            return False
        elif not is_valid_ipv4(ip_address):
            QMessageBox.critical(
                self,
                "Invalid IP Address",
                "The IP address is not valid. Please ensure it is in the format of X.X.X.X and try again.",
            )
            return False
        elif len(nickname) > MAX_NICKNAME_LENGTH:
            QMessageBox.critical(
                self,
                "Nickname Too Long",
                f"The nickname exceeds the maximum length of {MAX_NICKNAME_LENGTH} characters. Please shorten it and try again.",
            )
            return False

        return True

    def show_connection_error(self):
        QMessageBox.critical(
            self,
            "Failed to Connect",
            f"Failed to connect to the server. Please verify the IP is correct and try again.",
        )
