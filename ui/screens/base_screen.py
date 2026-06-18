from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal

from core.app.screen_ids import Screens


class BaseScreen(QWidget):
    navigate = pyqtSignal(Screens, dict)
    title_text = "Quiz Master"

    def __init__(self, parent=None):
        super().__init__(parent)

    def go_to(self, screen: Screens, payload=None):
        if payload is None:
            payload = {}

        self.navigate.emit(screen, payload)

    def on_enter(self, payload: dict = None):
        pass

    def on_leave(self):
        pass
