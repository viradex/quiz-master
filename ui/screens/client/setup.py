from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QSpacerItem,
    QVBoxLayout,
)

from core.app.screen_ids import Screens
from ui.components.input import CharacterCountInput
from ui.screens.base_screen import BaseScreen

from utils.networking import is_valid_ipv4
from ui.components.button import create_return_button
from core.config.constants import DEFAULT_IP_ADDRESS, MAX_NICKNAME_LENGTH, PORT


class ClientSetupScreen(BaseScreen):
    title_text = "Quiz Master – Client Setup"

    submitted = pyqtSignal(dict)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setup_ui()

    def setup_ui(self) -> None:
        ## FONTS SETUP ##
        title_font = QFont()
        title_font.setPointSize(20)

        form_font = QFont()
        form_font.setPointSize(14)

        ## WIDGETS SETUP ##
        # Connection form
        title = QLabel("Enter connection details:")
        title.setFont(title_font)

        ip_lbl = QLabel("Server IP:")
        ip_lbl.setFont(form_font)

        self.ip_input = QLineEdit(DEFAULT_IP_ADDRESS)
        self.ip_input.setFont(form_font)
        self.ip_input.returnPressed.connect(self.on_submit)

        # Static text for debugging purposes
        self.port_lbl = QLabel(f"Connecting to port: {PORT}")
        self.port_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.port_lbl.setStyleSheet("font-size: 12px;" "color: #A7A7A7;")

        nickname_lbl = QLabel("Nickname:")
        nickname_lbl.setFont(form_font)

        self.nickname_counter = CharacterCountInput(MAX_NICKNAME_LENGTH)
        self.nickname_counter.line_edit.setFont(form_font)
        self.nickname_counter.line_edit.returnPressed.connect(self.on_submit)

        # Action buttons
        self.return_btn = create_return_button(
            "Return to Menu", btn_width=200, btn_font_size=16
        )
        self.return_btn.setFixedHeight(45)
        self.return_btn.clicked.connect(lambda: self.go_to(Screens.COMMON_MENU))

        self.join_btn = QPushButton("Join")
        self.join_btn.setFixedSize(240, 50)
        self.join_btn.setStyleSheet("font-size: 22px;")
        self.join_btn.clicked.connect(self.on_submit)

        ## LAYOUTS SETUP ##
        form_layout = QFormLayout()
        form_layout.setHorizontalSpacing(25)

        # QFormLayout doesn't support .addSpacing(), hence the QSpacerItem
        form_layout.addRow(ip_lbl, self.ip_input)
        form_layout.addRow(self.port_lbl)
        form_layout.addItem(QSpacerItem(0, 10))
        form_layout.addRow(nickname_lbl, self.nickname_counter)

        btn_hbox = QHBoxLayout()
        btn_hbox.addWidget(self.return_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        btn_hbox.addWidget(self.join_btn, alignment=Qt.AlignmentFlag.AlignRight)

        vbox_wrapper = QWidget()
        vbox_wrapper.setMaximumWidth(1000)

        vbox = QVBoxLayout(vbox_wrapper)
        vbox.setContentsMargins(20, 20, 20, 20)
        vbox.addStretch(1)
        vbox.addWidget(title)
        vbox.addSpacing(50)
        vbox.addLayout(form_layout)
        vbox.addSpacing(40)
        vbox.addLayout(btn_hbox)
        vbox.addStretch(2)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(vbox_wrapper, stretch=6)
        hbox.addStretch(1)

        self.setLayout(hbox)

    def clear_fields(self) -> None:
        """Reset all form fields."""
        self.ip_input.setText(DEFAULT_IP_ADDRESS)
        self.nickname_counter.line_edit.setText("")

    def on_submit(self) -> None:
        """Gets text from form fields and validates it."""
        data = {
            "ip": self.ip_input.text().strip(),
            "nickname": self.nickname_counter.line_edit.text().strip(),
        }

        # Validate data (shows UI errors if failed)
        if not self.validate_data():
            return

        self.submitted.emit(data)

    def validate_data(self) -> bool:
        """Validate all form field data through basic validation."""
        ip_address = self.ip_input.text().strip()
        nickname = self.nickname_counter.line_edit.text().strip()

        if not ip_address or not nickname:
            self.show_error(
                "Empty Fields",
                "Please ensure all fields are filled in and try again.",
            )
            return False
        elif not is_valid_ipv4(ip_address):
            self.show_error(
                "Invalid IP Address",
                "The IP address is not valid. Please ensure it is in the format of X.X.X.X and try again.",
            )
            return False
        elif len(nickname) > MAX_NICKNAME_LENGTH:
            self.show_error(
                "Nickname Too Long",
                f"The nickname exceeds the maximum length of {MAX_NICKNAME_LENGTH} characters. Please shorten it and try again.",
            )
            return False

        return True

    def on_enter(self, payload: dict | None = None) -> None:
        # Keeps fields populated if an error occurred while connecting
        if payload is None or not payload["error_occurred"]:
            self.clear_fields()
