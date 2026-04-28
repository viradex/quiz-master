from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal

from core.screen_ids import Screens


class BaseScreen(QWidget):
    navigate = pyqtSignal(Screens)
    title_text = "Quiz Master"

    def __init__(self, parent=None):
        super().__init__(parent)

    def go_to(self, screen: Screens):
        self.navigate.emit(screen)

    def on_enter(self):
        pass

    def on_leave(self):
        pass
