"""
setup.py

The client setup UI screen. Allows configuring the IP address to connect to and the nickname
to connect with, then allows joining the server.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from core.app.screen_ids import Screen
from core.config.constants import MAX_NICKNAME_LENGTH, PORT
from ui.components.button import create_return_button
from ui.components.input import CharacterCountLineEdit
from ui.screens.base_screen import BaseScreen
from utils.networking import is_valid_ipv4


class ClientSetupScreen(BaseScreen):
    """
    Creates the client setup screen, inheriting BaseScreen. This screen is part of the 'client' category.

    This screen is responsible for allowing users to enter a server IP address and the nickname to use to
    connect to the server, then allows connecting to it.

    Attributes:
        title_text: The default text of the screen when entered. A string is used as that is what the
            title changing code requires.

        save_requested: A `pyqtSignal` that emits when the user wishes to try to connect to the server. A
            dictionary containing relevant connection data is provided as an argument.

    Arguments:
        parent: The parent of this screen, or None. Typically, this is the MainWindow.
    """

    title_text = "Quiz Master – Client Setup"

    submitted = pyqtSignal(dict)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._setup_ui()

    def _setup_ui(self) -> None:
        """
        Internal method. Sets up the screen UI for the first time. This method should only be called once,
        preferably in the initialization logic.

        Returns:
            None.
        """
        self._setup_fonts()
        self._setup_widgets()
        self._setup_layouts()

    def _setup_fonts(self) -> None:
        """
        Internal method. Sets up all `QFont` instances and their properties that the widgets will utilize. If
        a font is modified via QSS stylesheets, they are not included here.

        Returns:
            None.
        """
        self.title_font = QFont()
        self.title_font.setPointSize(20)

        self.form_font = QFont()
        self.form_font.setPointSize(14)

    def _setup_widgets(self) -> None:
        """
        Internal method. Sets up all widgets used by the screen, including styling and slots, if needed. These
        widgets are not added to any global layout in this method, however.

        Returns:
            None.
        """
        # Title of screen
        self.title = QLabel("Enter connection details:")
        self.title.setFont(self.title_font)

        # IP entry row
        self.ip_lbl = QLabel("Server IP:")
        self.ip_lbl.setFont(self.form_font)

        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("e.g. 192.168.1.100")
        self.ip_input.setFont(self.form_font)
        self.ip_input.returnPressed.connect(self._on_submit)

        # Static port text below IP for technical information
        self.port_lbl = QLabel(f"Connecting to port: {PORT}")
        self.port_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.port_lbl.setStyleSheet("font-size: 12px;" "color: #A7A7A7;")

        # Nickname entry row
        self.nickname_lbl = QLabel("Nickname:")
        self.nickname_lbl.setFont(self.form_font)

        self.nickname_counter = CharacterCountLineEdit(MAX_NICKNAME_LENGTH)
        self.nickname_counter.line_edit.setFont(self.form_font)
        self.nickname_counter.line_edit.returnPressed.connect(self._on_submit)

        # Action buttons
        self.return_btn = create_return_button(
            "Return to Menu", btn_width=200, btn_font_size=16
        )
        self.return_btn.setFixedHeight(45)
        self.return_btn.clicked.connect(lambda: self.go_to(Screen.COMMON_MENU))

        self.join_btn = QPushButton("Join")
        self.join_btn.setFixedSize(240, 50)
        self.join_btn.setStyleSheet("font-size: 22px;")
        self.join_btn.clicked.connect(self._on_submit)

    def _setup_layouts(self) -> None:
        """
        Internal method. Sets up all the layouts on this screen, adding widgets and controlling alignment, spacing,
        and stretching. The main layout is also applied as this screen's primary layout via `setLayout()`.

        Returns:
            None.
        """
        form_layout = QFormLayout()
        form_layout.setHorizontalSpacing(25)

        # QFormLayout doesn't support .addSpacing(), hence the QSpacerItem
        form_layout.addRow(self.ip_lbl, self.ip_input)
        form_layout.addRow(self.port_lbl)
        form_layout.addItem(QSpacerItem(0, 10))
        form_layout.addRow(self.nickname_lbl, self.nickname_counter)

        # Button row at bottom of screen
        btn_hbox = QHBoxLayout()
        btn_hbox.addWidget(self.return_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        btn_hbox.addWidget(self.join_btn, alignment=Qt.AlignmentFlag.AlignRight)

        # Ensures entire screen contents does not exceed 1000px width
        vbox_wrapper = QWidget()
        vbox_wrapper.setMaximumWidth(1000)

        # Adds 1:2 ratio for contents to align with brain's perceived center
        # rather than actual geometric center
        vbox = QVBoxLayout(vbox_wrapper)
        vbox.setContentsMargins(20, 20, 20, 20)
        vbox.addStretch(1)
        vbox.addWidget(self.title)
        vbox.addSpacing(50)
        vbox.addLayout(form_layout)
        vbox.addSpacing(40)
        vbox.addLayout(btn_hbox)
        vbox.addStretch(2)

        # HBox wrapper to ensure contents don't get too wide and stay at certain ratio
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(vbox_wrapper, stretch=6)
        hbox.addStretch(1)

        self.setLayout(hbox)

    def get_data_entered(self) -> dict[str, str]:
        """
        Get all data entered from the form, as a dictionary. All text is stripped of leading and trailing
        whitespace.

        Data returned:
        - ip_address: The server IP address to connect to as supplied by the user.
        - nickname: The nickname entered by the user to connect to the server with.

        Returns:
            A dictionary with the data entered by the user. The values in the dictionary are documented above.
            A dictionary is used as it provides simple identifiable key-value pairs for each value entered.
        """
        return {
            "ip_address": self.ip_input.text().strip(),
            "nickname": self.nickname_counter.line_edit.text().strip(),
        }

    def validate_data(self, data: dict) -> bool:
        """
        Validate the data given, showing an error message box if the data does not fulfill the requirements.
        The data is expected to be given directly from `get_data_entered()`.

        Arguments:
            data: A dictionary with all the data entered by the user. The dictionary is expected to follow the same
                structure as the data provided from `get_data_entered()`. A dictionary is used as it provides multiple
                values in a single argument for multiple data fields provided by the user.

        Returns:
            A boolean identifying if validation passed or failed. Returns True if validation passed, else, returns
            False. A boolean is used as it allows for simple boolean logic checks for if validation passed or failed.
        """
        ip_address = data["ip_address"]
        nickname = data["nickname"]

        if not ip_address or not nickname:
            self.show_error(
                "Empty Fields", "Please ensure all fields are filled in and try again."
            )
            return False
        elif not is_valid_ipv4(ip_address, allow_localhost=True):
            self.show_error(
                "Invalid IP Address",
                "The IP address is not valid. Please enter a valid IPv4 address (e.g. 192.168.1.100) or use 'localhost' for a local connection, and try again.",
            )
            return False
        elif len(nickname) > MAX_NICKNAME_LENGTH:
            self.show_error(
                "Nickname Too Long",
                f"The nickname exceeds the maximum length of {MAX_NICKNAME_LENGTH} characters. Please shorten it and try again.",
            )
            return False

        # All tests passed
        return True

    def _on_submit(self) -> None:
        """
        Internal method. Intended to be called upon pressing the Join button. This method validates the data,
        and if all checks pass, attempts to connect to the server with the provided information.

        Returns:
            None.
        """
        data = self.get_data_entered()

        # Automatically shows error modal boxes as well
        if not self.validate_data(data):
            return

        self.submitted.emit(data)

    def on_enter(self, payload: None = None) -> None:
        # Fields are not cleared as users will likely want to connect to the same
        # IP with the same nickname if they are connecting to a server more than
        # once in the same session. Just set focus to the IP input field in case.
        self.ip_input.setFocus()
