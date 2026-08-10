"""
disconnect.py

The client disconnection UI screen. Displays the reason of disconnection and allows the user to
return to the main menu.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from core.app.screen_ids import Screen
from ui.screens.base_screen import BaseScreen

# The default reason to display on the UI if none is given
DEFAULT_REASON = "Unknown"


class ClientDisconnectScreen(BaseScreen):
    """
    Creates the disconnect screen, inheriting BaseScreen. This screen is part of the 'client' category.

    This screen is responsible for showing the reason for disconnection and allowing the user to easily
    return to the main menu.

    Attributes:
        title_text: The default text of the screen when entered. A string is used as that is what the
            title changing code requires.

    Arguments:
        parent: The parent of this screen, or None. Typically, this is the MainWindow.
    """

    title_text = "Quiz Master – Disconnected"

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._setup_ui()

    def _setup_ui(self) -> None:
        """
        Internal method. Sets up the screen UI, including fonts, widgets, and layouts, for the first time.
        This method should only be called once, preferably in the initialization logic.

        Returns:
            None.
        """
        ## FONTS SETUP ##
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)

        reason_font = QFont()
        reason_font.setPointSize(16)

        ## WIDGETS SETUP ##
        # Informatory headings and description
        title = QLabel("Disconnected")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(title_font)

        desc = QLabel("You have been disconnected from the server.")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("font-size: 16px;" "color: #6E6E6E;")

        # Set word wrap in case reason is long, to avoid overflowing off the screen
        self.reason = QLabel()
        self.reason.setWordWrap(True)
        self.reason.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.reason.setFont(reason_font)

        self.return_btn = QPushButton("Return to Menu")
        self.return_btn.setFixedSize(275, 60)
        self.return_btn.clicked.connect(lambda: self.go_to(Screen.COMMON_MENU))
        self.return_btn.setStyleSheet("font-size: 22px;")

        ## LAYOUTS SETUP ##
        # Add same stretch on top and bottom to ensure widgets appear in the middle
        vbox = QVBoxLayout()
        vbox.addStretch()
        vbox.addWidget(title)
        vbox.addSpacing(5)
        vbox.addWidget(desc)
        vbox.addSpacing(10)
        vbox.addWidget(self.reason)
        vbox.addSpacing(40)
        vbox.addWidget(self.return_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        vbox.addStretch()

        self.setLayout(vbox)

    def set_reason(self, reason: str | None = None) -> None:
        """
        Sets the 'reason' text on the UI to the reason provided. If the reason provided is None, the default
        reason is set instead.

        Arguments:
            reason: The reason of disconnection, to display to the user. If None, displays the default reason.
                A string is used as it represents characters well for the disconnection reason. Optional;
                defaults to None, meaning the default reason is displayed if no value is entered.

        Returns:
            None.
        """
        reason = reason if reason is not None else DEFAULT_REASON
        self.reason.setText(f"Reason: {reason}")

    def on_enter(self, payload: dict | None = None) -> None:
        # If no payload provided, set default reason
        if payload is None:
            self.set_reason()

        # Get reason, if provided, else default
        reason = payload.get("reason", DEFAULT_REASON)
        self.set_reason(reason)

    def on_leave(self) -> None:
        # Reset reason to default
        self.set_reason()
