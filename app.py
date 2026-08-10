"""
app.py

Defines the application bootstrapper, and compatibility checks against macOS and Windows versions
below Windows 11. Also runs the GUI window.
"""

import sys

from PyQt6.QtWidgets import QApplication, QMessageBox

from core.services.app_context import Services
from ui.main_window import MainWindow


def run() -> None:
    """
    Runs the application bootstrapper.

    This should only be run once, by the entry point of the program. Creates a `QApplication`
    and runs compatibility platform checks against macOS and Windows, showing a warning if
    checks fail. The main GUI window is then displayed and the app is run.

    Returns:
        None.
    """
    app = QApplication(sys.argv)

    # Shows a warning messagebox if any checks fail
    _run_compatibility_checks()

    # Create app services to ensure MainWindow does not know about
    # the initialization of individual services
    services = Services()

    window = MainWindow(services)
    window.show()

    # Run the QApplication, and exit when done
    sys.exit(app.exec())


def _run_compatibility_checks() -> None:
    """
    Internal function. Runs compatibility checks on the system the program is running on, and shows a
    user-facing warning dialog if any checks fail. The user is allowed to proceed, but they are warned
    to proceed with caution.

    Checks performed explicitly against:
    - **macOS**: macOS is officially unsupported. Therefore, there is no guarantee that the application
        will not crash or appear broken.
    - **Windows 10 and below**: On Windows 10 and below, dark mode is not officially supported. This program
        relies on dark mode due to the styling being centered around the assumption that the theme is in
        dark mode. The application is not expected to crash, but UI elements can appear broken.

    Returns:
        None.
    """
    # App can crash on macOS, and UI elements can appear broken
    if sys.platform == "darwin":
        QMessageBox.warning(
            None,
            "Compatibility Warning",
            "This program does not officially support macOS. While it may run, you may encounter bugs, crashes, or unexpected behavior. Continue at your own risk.",
        )

    # While app will not crash on Windows 10, Windows 10 does not support PyQt dark mode
    # 22000 is the first build of Windows 11
    if sys.platform == "win32" and sys.getwindowsversion().build < 22000:
        QMessageBox.warning(
            None,
            "Compatibility Warning",
            "This program is designed for Windows 11. On Windows 10 and earlier, some visual features (such as native dark mode) are unavailable, and UI elements may not render as intended. Continue at your own risk.",
        )
