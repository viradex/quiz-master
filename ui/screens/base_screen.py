from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QWidget, QMessageBox

from core.app.screen_ids import Screens


class BaseScreen(QWidget):
    """Base screen for all screens of the app."""

    navigate = pyqtSignal(Screens, object)  # Screen ID, any payload type
    title_change = pyqtSignal(str)  # New title
    status = pyqtSignal(str, int)  # Status text, timeout
    status_reset = pyqtSignal()

    title_text = "Quiz Master"

    def go_to(self, screen: Screens, payload=None) -> None:
        """Navigate to another screen of the app with an optional data payload."""
        self.navigate.emit(screen, payload)

    def set_title(self, title: str) -> None:
        """Change the application window title.
        The title should preferably be "Quiz Master – {window name}"."""
        self.title_change.emit(title)

    def set_status(self, message: str, timeout: int = 0) -> None:
        """
        Set status bar message, with optional timeout (in milliseconds).
        A timeout of 0 is treated as a permanent message and will not change unless reset with `reset_status()`.
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

    def show_question(self, title: str, desc: str, default: str = "no") -> bool:
        """Show an question modal window. Returns True if Yes was selected."""
        default = default.lower()
        if default not in ("yes", "no"):
            raise ValueError(f"Invalid default value: {default}")

        default_button = (
            QMessageBox.StandardButton.No
            if default == "no"
            else QMessageBox.StandardButton.Yes
        )

        confirm = QMessageBox.question(
            self,
            title,
            desc,
            defaultButton=default_button,
        )

        return confirm == QMessageBox.StandardButton.Yes

    def on_enter(self, payload=None) -> None:
        """Called when the screen is shown, with an optional payload."""
        pass

    def on_leave(self) -> None:
        """Called when the screen is hidden."""
        pass

    def on_window_close(self, event: QCloseEvent) -> None:
        """Called when the application is about to be closed."""
        pass
