import sys
from PyQt6.QtWidgets import QApplication, QMessageBox

from ui.main_window import MainWindow
from core.services.app_context import Services


def run() -> None:
    """Create and run the application's main GUI window."""
    app = QApplication(sys.argv)

    # UI elements can appear broken on macOS, so show warning
    if sys.platform == "darwin":
        QMessageBox.warning(
            None,
            "Compatibility Warning",
            "This program does not officially support macOS. While it may run, you may encounter bugs, crashes, or unexpected behavior. Continue at your own risk.",
        )

    services = Services()

    window = MainWindow(services)
    window.show()

    sys.exit(app.exec())
