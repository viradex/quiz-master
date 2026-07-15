from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QKeyEvent
from PyQt6.QtWidgets import (
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
)

from core.app.screen_ids import Screens
from ui.screens.base_screen import BaseScreen


class CommonAboutScreen(BaseScreen):
    title_text = "Quiz Master – About"

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.base_dir = Path(__file__).resolve().parent.parent.parent.parent
        self.license_path = self.base_dir / "LICENSE"

        self.license_text = self.get_license_text()

        self.setup_ui()
        self.setup_keys()

    def setup_ui(self) -> None:
        ## FONTS SETUP ##
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)

        desc_font = QFont()
        desc_font.setPointSize(12)

        license_info_font = QFont()
        license_info_font.setPointSize(10)

        ## WIDGETS SETUP ##
        title = QLabel("About Quiz Master")
        title.setFont(title_font)

        menu_btn = QPushButton("Return to Menu")
        menu_btn.setFixedSize(140, 40)
        menu_btn.setStyleSheet("font-size: 14px;")
        menu_btn.clicked.connect(lambda: self.go_to(Screens.COMMON_MENU))

        desc = QLabel("Designed, programmed, and tested by Arnav Thorat (2026)!")
        desc.setFont(desc_font)

        license_info = QLabel(
            "Quiz Master is open-source software licensed under the GNU GPL v3.0.\nThis application uses PyQt6, which is licensed under the GNU GPL. The full license text is provided below."
        )
        license_info.setWordWrap(True)
        license_info.setFont(license_info_font)

        self.license_area = QPlainTextEdit()
        self.license_area.setReadOnly(True)
        self.license_area.setFixedWidth(520)
        self.license_area.setPlainText(self.license_text)

        ## LAYOUTS SETUP ##
        title_hbox = QHBoxLayout()
        title_hbox.addWidget(title)
        title_hbox.addWidget(menu_btn, alignment=Qt.AlignmentFlag.AlignRight)

        vbox = QVBoxLayout()
        vbox.setContentsMargins(20, 20, 20, 20)
        vbox.addLayout(title_hbox)
        vbox.addSpacing(2)
        vbox.addWidget(desc)
        vbox.addSpacing(10)
        vbox.addWidget(license_info)
        vbox.addSpacing(5)
        vbox.addWidget(self.license_area, stretch=1)

        self.setLayout(vbox)

    def setup_keys(self) -> None:
        self.target = "catsarebetterthandogs"
        self.index = 0
        self.showing_license = True

        # Allows the screen to accept focus
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def get_license_text(self) -> None:
        """Read license text from disk."""
        try:
            license_text = self.license_path.read_text(encoding="utf-8")
        except OSError:
            license_text = "Could not load license file."

        return license_text

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Called automatically by PyQt when a keyboard key is pressed."""
        key = event.text().lower()
        if not key:
            return

        expected = self.target[self.index]

        if key == expected:
            self.index += 1

            # If entire sequence has been done, reset
            if self.index == len(self.target):
                self.on_sequence_completion()
                self.index = 0
        else:
            self.index = 0

    def on_sequence_completion(self) -> None:
        # Treats sequence completion as a toggle rather than a one-way switch
        if self.showing_license:
            self.license_area.setPlainText(
                r"""Why are you being so one-sided? All animals are equal!

...

But some animals are more equal than others.

|\---/|
| o_o |
 \_^_/

Meow."""
            )
            self.showing_license = False
        else:
            self.license_area.setPlainText(self.license_text)
            self.showing_license = True

    def on_leave(self) -> None:
        self.license_area.setPlainText(self.license_text)
        self.showing_license = True
