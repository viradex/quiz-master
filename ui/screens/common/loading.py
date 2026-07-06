from PyQt6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QWidget
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt

from ui.screens.base_screen import BaseScreen
from ui.components.spinner import Spinner

DEFAULT_LOADING_TEXT = "Loading..."


class CommonLoadingScreen(BaseScreen):
    title_text = f"Quiz Master – {DEFAULT_LOADING_TEXT}"

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setup_ui()

    def setup_ui(self) -> None:
        ## FONTS SETUP ##
        loading_font = QFont()
        loading_font.setPointSize(32)

        ## WIDGETS SETUP ##
        self.spinner = Spinner(size=40, color=QColor(255, 255, 255), interval_ms=20)

        self.loading_lbl = QLabel(DEFAULT_LOADING_TEXT)
        self.loading_lbl.setFont(loading_font)

        self.status_lbl = QLabel()
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_lbl.setStyleSheet("color: #888888;" "font-size: 22px;")

        ## LAYOUTS SETUP ##
        hbox_loading = QHBoxLayout()
        hbox_loading.addWidget(self.spinner)
        hbox_loading.addSpacing(10)
        hbox_loading.addWidget(self.loading_lbl)

        hbox_loading_container = QWidget()
        hbox_loading_container.setLayout(hbox_loading)

        vbox = QVBoxLayout()
        vbox.addStretch()
        vbox.addWidget(hbox_loading_container, alignment=Qt.AlignmentFlag.AlignCenter)
        vbox.addWidget(self.status_lbl)
        vbox.addStretch()

        self.setLayout(vbox)

    def set_loading_status(self, loading: str, status: str) -> None:
        """Set loading text and subtext status, and the window title."""
        self.set_title(loading)

        self.loading_lbl.setText(loading)
        self.status_lbl.setText(status)

    def on_enter(self, payload=None) -> None:
        self.spinner.start()

        if payload:
            loading_msg = payload.get("loading_msg", DEFAULT_LOADING_TEXT)
            self.set_loading_status(loading_msg, payload.get("status_msg", ""))

    def on_leave(self) -> None:
        self.spinner.stop()
        self.set_loading_status(DEFAULT_LOADING_TEXT, "")
