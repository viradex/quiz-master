from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6.QtCore import pyqtSignal

from core.app.screen_ids import Screens


class BaseScreen(QWidget):
    """Base screen for all screens of the app."""

    navigate = pyqtSignal(Screens, dict)
    status = pyqtSignal(str, int)
    status_reset = pyqtSignal()

    title_text = "Quiz Master"

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

    def go_to(self, screen: Screens, payload: dict | None = None) -> None:
        """Navigate to another screen of the app with an optional data payload."""
        if payload is None:
            payload = {}

        self.navigate.emit(screen, payload)

    def set_status(self, message: str, timeout: int = 0) -> None:
        """Set status bar message, with optional timeout (in milliseconds).
        A timeout of 0 is treated as a permanent message and will not change unless reset with `clear_status()`.
        """
        self.status.emit(message, timeout)

    def reset_status(self) -> None:
        """Clear status bar message, resetting it to the default."""
        self.status_reset.emit()

    def show_error(self, title: str, desc: str) -> None:
        """Show an error modal window."""
        QMessageBox.critical(self, title, desc)

    def show_warning(self, title: str, desc: str) -> None:
        """Show a warning modal window."""
        QMessageBox.warning(self, title, desc)

    def show_info(self, title: str, desc: str) -> None:
        """Show an informational modal window."""
        QMessageBox.information(self, title, desc)

    def on_enter(self, payload: dict | None = None) -> None:
        pass

    def on_leave(self) -> None:
        pass
