import sys
from PyQt6.QtWidgets import QApplication, QMessageBox

from core.services.app_context import Services
from ui.main_window import MainWindow


def run() -> None:
    """Create and run the application's main GUI window. Shows compatibility warnings."""
    app = QApplication(sys.argv)

    # App can crash on macOS, and UI elements can appear broken
    if sys.platform == "darwin":
        QMessageBox.warning(
            None,
            "Compatibility Warning",
            "This program does not officially support macOS. While it may run, you may encounter bugs, crashes, or unexpected behavior. Continue at your own risk.",
        )

    # While app will not crash on Windows 10, Windows 10 does not support PyQt dark mode
    # 22000 is the first build of Windows 11
    elif sys.platform == "win32" and sys.getwindowsversion().build < 22000:
        QMessageBox.warning(
            None,
            "Compatibility Warning",
            "This program is designed for Windows 11. On Windows 10 and earlier, some visual features (such as native dark mode) are unavailable, and UI elements may not render as intended. Continue at your own risk.",
        )

    services = Services()

    window = MainWindow(services)
    window.show()

    sys.exit(app.exec())
