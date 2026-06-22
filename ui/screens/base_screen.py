from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal

from core.app.screen_ids import Screens


class BaseScreen(QWidget):
    """Base screen for all screens of the app."""

    navigate = pyqtSignal(Screens, dict)
    title_text = "Quiz Master"

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

    def go_to(self, screen: Screens, payload: dict | None = None):
        """Navigate to another screen of the app with an optional data payload."""
        if payload is None:
            payload = {}

        self.navigate.emit(screen, payload)

    def on_enter(self, payload: dict | None = None):
        pass

    def on_leave(self):
        pass
