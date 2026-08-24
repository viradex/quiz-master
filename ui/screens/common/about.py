"""
about.py

The about UI screen. Contains author and license information about this application, and Qt.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QKeyEvent
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.app.screen_ids import Screen
from ui.screens.base_screen import BaseScreen
from utils.paths import get_base_dir


class CommonAboutScreen(BaseScreen):
    """
    Creates the about screen, inheriting BaseScreen. This screen is part of the 'common' category.

    This screen is responsible for showing information about this program, including the author and
    year, as well as the full license text. Information relating to the Qt framework is also shown.

    Attributes:
        title_text: The default text of the screen when entered. A string is used as that is what the
            title changing code requires.

    Arguments:
        parent: The parent of this screen, or None. Typically, this is the MainWindow.
    """

    title_text = "Quiz Master – About"

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # Rather than hardcoding license text, retrieve it dynamically
        # from the license file itself, in case the license ever changes.
        self.license_path = get_base_dir() / "LICENSE"
        self.license_text = self.get_license_text()

        self._setup_ui()
        self._setup_keys()

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
        self.title_font.setPointSize(18)
        self.title_font.setBold(True)

        self.desc_font = QFont()
        self.desc_font.setPointSize(12)

        self.license_info_font = QFont()
        self.license_info_font.setPointSize(10)

    def _setup_widgets(self) -> None:
        """
        Internal method. Sets up all widgets used by the screen, including styling and slots, if needed. These
        widgets are not added to any global layout in this method, however.

        Returns:
            None.
        """
        self.title = QLabel("About Quiz Master")
        self.title.setFont(self.title_font)

        self.menu_btn = QPushButton("Return to Menu")
        self.menu_btn.setFixedSize(140, 40)
        self.menu_btn.setStyleSheet("font-size: 14px;")
        self.menu_btn.clicked.connect(lambda: self.go_to(Screen.COMMON_MENU))

        self.desc = QLabel("Designed, programmed, and tested by Arnav Thorat (2026).")
        self.desc.setFont(self.desc_font)

        self.license_info = QLabel(
            "Quiz Master is open-source software licensed under the GNU GPL v3.0.\nThis application uses PyQt, which is licensed under the GNU GPL."
        )
        self.license_info.setWordWrap(True)
        self.license_info.setFont(self.license_info_font)

        # Enable rich text on this QLabel to allow the interactive "About Qt" link
        # while keeping link handling on the same line as non-interactive text, rather
        # than using a ClickableLabel, which would make the entire text clickable.
        self.license_below = QLabel(
            'The full license text is provided below. <a href="aboutqt">About Qt</a>'
        )
        self.license_below.setFont(self.license_info_font)
        self.license_below.setTextFormat(Qt.TextFormat.RichText)

        # Allows link to be clicked and also interacted with by keyboard
        self.license_below.setTextInteractionFlags(
            Qt.TextInteractionFlag.LinksAccessibleByMouse
            | Qt.TextInteractionFlag.LinksAccessibleByKeyboard
        )

        # Prevents PyQt from opening links in the default web browser
        self.license_below.setOpenExternalLinks(False)

        # Opens Qt's built-in About Qt dialog box
        self.license_below.linkActivated.connect(lambda _: QApplication.aboutQt())

        # Limit license text width to prevent it from stretching across the screen
        self.license_area = QPlainTextEdit()
        self.license_area.setReadOnly(True)
        self.license_area.setFixedWidth(520)
        self.license_area.setPlainText(self.license_text)

    def _setup_layouts(self) -> None:
        """
        Internal method. Sets up all the layouts on this screen, adding widgets and controlling alignment, spacing,
        and stretching. The main layout is also applied as this screen's primary layout via `setLayout()`.

        Returns:
            None.
        """
        # Allows the return button to be on the same row as the title at the top of the screen
        title_hbox = QHBoxLayout()
        title_hbox.addWidget(self.title)
        title_hbox.addWidget(self.menu_btn, alignment=Qt.AlignmentFlag.AlignRight)

        vbox = QVBoxLayout()
        vbox.setContentsMargins(20, 20, 20, 20)
        vbox.addLayout(title_hbox)
        vbox.addSpacing(2)
        vbox.addWidget(self.desc)
        vbox.addSpacing(10)
        vbox.addWidget(self.license_info)
        vbox.addWidget(self.license_below)
        vbox.addSpacing(5)

        # Allow license text to take up remaining screen area
        vbox.addWidget(self.license_area, stretch=1)

        self.setLayout(vbox)

    def _setup_keys(self) -> None:
        """
        Internal method. Sets up all attributes relating to keyboard keys, including the target to type and
        certain properties to track progress. Also, allows the screen to listen to keyboard input directly.

        Returns:
            None.
        """
        # Set starting information
        self.target = "catsarebetterthandogs"
        self.index = 0

        # Makes the screen eligible for focus to listen for keyboard input
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def get_license_text(self) -> str:
        """
        Reads the license text from disk, as defined in the `LICENSE` file in the base directory of the program.
        The path to the license file is defined in `license_path`. This method expects the path to be defined beforehand,
        as it simply reads the text.

        If the license file could not be read, it returns a placeholder error text.

        Returns:
            The license text as defined in the `LICENSE` file, or an error text. A string is returned to allow easy
                display, and because the license text is a string.
        """
        try:
            license_text = self.license_path.read_text(encoding="utf-8")
        except OSError:
            license_text = "Could not load license file."

        return license_text

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """
        Called automatically by PyQt when a keyboard key is pressed and the window is in focus. This is not called
        when another child widget has focus, such as a `QPlainTextEdit`.

        Matches the key to the next expected key in the sequence. If it is the correct key, adds one to the completion,
        and if the sequence has been completed, runs the respective function and resets progress. If the incorrect
        key is pressed, the sequence is reset.

        Arguments:
            event: An argument passed automatically by PyQt upon this method being run. Allows getting the key that
                was pressed.

        Returns:
            None.
        """
        # Get the key pressed in string representation
        key = event.text().lower()

        if not key:
            super().keyPressEvent(event)
            return

        expected = self.target[self.index]

        # Compares expected key with actual key: if it matches,
        # the sequence progresses, else, their progress fully resets
        if key == expected:
            self.index += 1

            # If entire sequence has been done, run the completion method and reset
            if self.index == len(self.target):
                self._on_sequence_completion()
                self.index = 0
        else:
            self.index = 0

    def _on_sequence_completion(self) -> None:
        """
        Internal method. Intended to be run when the keyboard sequence is complete. Replaces the license text
        with some information about cats.

        Returns:
            None.
        """
        # Originally, the license text would revert if the cats text was already shown.
        # However, the text already resets when leaving the window, and it is very unlikely
        # someone who wants to go through the effort of triggering this Easter egg would want
        # to revert it, let alone know how to. Leaving and re-entering the window to reset it
        # is a more understandable user experience, without the added complexity and flags
        # of toggling the license text.

        # Raw string used to treat backslashes as literal characters rather than escape
        # sequences, for the ASCII art.
        self.license_area.setPlainText(
            r"""Why are you being so one-sided? All animals are equal!

...

But some animals are more equal than others.

|\---/|
| o_o |
 \_^_/

Meow."""
        )

    def on_leave(self) -> None:
        # Reset license to normal license text, regardless of state
        self.license_area.setPlainText(self.license_text)
