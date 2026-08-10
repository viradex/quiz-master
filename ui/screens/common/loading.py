"""
loading.py

The loading UI screen. Contains a simple loading spinner and text in the center of the screen.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ui.components.spinner import Spinner
from ui.screens.base_screen import BaseScreen

# Default loading text to show when no loading text is provided
DEFAULT_LOADING_TEXT = "Loading..."

# Default status text to show when no status text is provided
DEFAULT_STATUS_TEXT = "Please wait..."


class CommonLoadingScreen(BaseScreen):
    """
    Creates the loading screen, inheriting BaseScreen. This screen is part of the 'common' category.

    This screen is responsible for showing a loading spinner and primary loading text, as well as
    loading subtext for describing the current process briefly in a bit more detail.

    Attributes:
        title_text: The default text of the screen when entered. A string is used as that is what the
            title changing code requires.

    Arguments:
        parent: The parent of this screen, or None. Typically, this is the MainWindow.
    """

    title_text = f"Quiz Master – {DEFAULT_LOADING_TEXT}"

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
        loading_font = QFont()
        loading_font.setPointSize(32)

        ## WIDGETS SETUP ##
        # Make a large white loading spinner as the primary loading indicator
        self.spinner = Spinner(size=40)

        self.loading_lbl = QLabel(DEFAULT_LOADING_TEXT)
        self.loading_lbl.setFont(loading_font)

        self.status_lbl = QLabel()
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_lbl.setStyleSheet("color: #888;" "font-size: 22px;")

        ## LAYOUTS SETUP ##
        # Contains the primary text and loading spinner
        hbox_loading = QHBoxLayout()
        hbox_loading.addWidget(self.spinner)
        hbox_loading.addSpacing(10)
        hbox_loading.addWidget(self.loading_lbl)

        # Puts primary text and loading spinner in a wrapper QWidget to
        # allow both widgets to be centered
        hbox_loading_container = QWidget()
        hbox_loading_container.setLayout(hbox_loading)

        # Add same stretch on top and bottom to ensure widgets appear in the middle
        vbox = QVBoxLayout()
        vbox.addStretch()
        vbox.addWidget(hbox_loading_container, alignment=Qt.AlignmentFlag.AlignCenter)
        vbox.addWidget(self.status_lbl)
        vbox.addStretch()

        self.setLayout(vbox)

    def set_loading_text(
        self, loading: str | None = None, status: str | None = None
    ) -> None:
        """
        Sets the loading text and status text of the screen, as well as the window title to reflect the loading
        text. If the loading text and/or the status text is None, the default loading/status text is used,
        respectively, which can be used as a fallback or to reset the screen.

        Attributes:
            loading: A string or None, describing the main loading text and title text. If None, default loading
                text is assumed. A string is used to easily set the title and text for type requirements, and None
                to easily signify a default value. Default is None.

            status: A string or None, describing the main status text. If None, default status text is assumed.
                A string is used to easily set the text for type requirements, and None to easily signify a
                default value. Default is None.

        Returns:
            None.
        """
        # Sets loading and status to their defaults if explicit custom values were not provided
        loading = loading if loading is not None else DEFAULT_LOADING_TEXT
        status = status if status is not None else DEFAULT_STATUS_TEXT

        self.set_title(f"Quiz Master – {loading}")

        self.loading_lbl.setText(loading)
        self.status_lbl.setText(status)

    def on_enter(self, payload: dict | None = None) -> None:
        self.spinner.start()

        if payload is None:
            # Set default text if no payload dictionary was provided at all
            self.set_loading_text()
        else:
            # If payload is provided, get loading and status messages if provided, else set default text
            loading_msg = payload.get("loading_msg")
            status_msg = payload.get("status_msg")

            self.set_loading_text(loading_msg, status_msg)

    def on_leave(self) -> None:
        # Stop spinner to reduce CPU usage as spinner is no longer shown, and reset all text
        self.spinner.stop()
        self.set_loading_text()
