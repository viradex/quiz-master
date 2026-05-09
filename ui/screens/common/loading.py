from PyQt6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QWidget
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt

from ui.screens.base_screen import BaseScreen
from ui.components.spinner import Spinner


class CommonLoadingScreen(BaseScreen):
    title_text = "Quiz Master – Loading..."

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setup_ui()

    def setup_ui(self):
        loading_font = QFont()
        loading_font.setPointSize(32)

        # TODO spinner becomes invisible in light mode!
        self.spinner = Spinner(
            self, size=40, color=QColor(255, 255, 255), interval_ms=20
        )

        self.loading_lbl = QLabel("Loading...")
        self.loading_lbl.setFont(loading_font)

        hbox_loading = QHBoxLayout()
        hbox_loading.addWidget(self.spinner)
        hbox_loading.addSpacing(10)
        hbox_loading.addWidget(self.loading_lbl)

        hbox_container = QWidget()
        hbox_container.setLayout(hbox_loading)

        self.status_lbl = QLabel("Preparing game...")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_lbl.setStyleSheet("color: #888888;" "font-size: 22px;")

        vbox = QVBoxLayout()
        vbox.addStretch()
        vbox.addWidget(hbox_container, alignment=Qt.AlignmentFlag.AlignCenter)
        vbox.addWidget(self.status_lbl)
        vbox.addStretch()

        self.setLayout(vbox)

    def on_enter(self):
        self.spinner.start()

    def on_leave(self):
        self.spinner.stop()
