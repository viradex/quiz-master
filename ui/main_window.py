import sys
import ctypes
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QStackedWidget,
    QMessageBox,
    QStatusBar,
)
from PyQt6.QtGui import QGuiApplication, QIcon
from PyQt6.QtCore import QTimer

from core.app.screen_ids import Screens
from core.services.app_context import Services
from logic.app_controller import AppController
from logic.base_logic import BaseLogic
from ui.screens.base_screen import BaseScreen

from core.app.screen_factory import create_screen_bundle
from core.config.constants import (
    EAGER_SCREENS,
    STARTUP_SCREEN,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    DEFAULT_STATUS_BAR_MESSAGE,
)


class MainWindow(QMainWindow):
    """Set up the main window, including UI screens and logic."""

    def __init__(self, services: Services) -> None:
        """Initialize MainWindow instance, setting up UI and building screens."""
        super().__init__()
        self.services = services

        self.current_screen: BaseScreen | None = None
        self.current_logic: BaseLogic | None = None

        self.setMinimumSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.center_window()

        self.setup_ui()
        self.setup_icon()
        self.setup_app_controller()
        self.build_screens()

        self.go_to(STARTUP_SCREEN)

    def center_window(self) -> None:
        """Move the window to the center of the primary screen."""
        screen = QGuiApplication.primaryScreen().availableGeometry()

        x = (screen.width() - WINDOW_WIDTH) // 2
        y = (screen.height() - WINDOW_HEIGHT) // 2

        self.move(x, y)

    def setup_icon(self) -> None:
        """Set up application icon."""
        base_dir = Path(__file__).resolve().parent
        icon_path = base_dir / "assets" / "icons" / "icon.ico"

        self.setWindowIcon(QIcon(icon_path.as_posix()))

        # Set taskbar icon on Windows
        if sys.platform == "win32":
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "com.viradex.quizmaster"
            )

    def setup_ui(self) -> None:
        """Create MainWindow UI with the stacked widget for showing individual screens, as well as status bar."""
        self.central = QWidget()
        self.setCentralWidget(self.central)

        self.stack = QStackedWidget()

        hbox = QHBoxLayout(self.central)
        hbox.addWidget(self.stack)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_text = DEFAULT_STATUS_BAR_MESSAGE

        self.status_bar.setStyleSheet("border-top: 1px solid #444;" "font-size: 11px;")
        self.status_bar.setSizeGripEnabled(False)

        self.handle_status(self.status_text, 0)

    def setup_app_controller(self) -> None:
        """Set up app controller (global logic)."""
        self.app_controller = AppController(self, self.services)

    def _build_screen(self, screen: Screens) -> None:
        """Build an individual screen and its respective logic."""
        widget, logic = create_screen_bundle(screen, self.services, self)

        self.screen_widgets[screen] = widget
        self.screen_logic[screen] = logic

        # Add screen to stacked widget
        self.stack.addWidget(widget)

        widget.navigate.connect(self.go_to)
        widget.status.connect(self.handle_status)
        widget.status_reset.connect(self.handle_status_reset)

    def build_screens(self) -> None:
        """Build all eager screens."""
        self.screen_widgets: dict[Screens, BaseScreen] = {}
        self.screen_logic: dict[Screens, BaseLogic] = {}

        for screen in EAGER_SCREENS:
            self._build_screen(screen)

    def get_screen(self, screen: Screens) -> BaseScreen:
        """Gets a screen reference. If it does not exist, builds the screen."""
        if screen not in self.screen_widgets:
            self._build_screen(screen)

        return self.screen_widgets[screen]

    def go_to(self, screen: Screens, payload: dict | None = None) -> None:
        # Call lifecycle functions if screen is shown
        if self.current_screen is not None:
            self.current_screen.on_leave()
            self.current_logic.on_leave()

        widget = self.get_screen(screen)
        logic = self.screen_logic[screen]

        self.stack.setCurrentWidget(widget)
        self.setWindowTitle(widget.title_text)

        widget.on_enter(payload)
        logic.on_enter()

        self.current_screen = widget
        self.current_logic = logic

    def handle_status(self, message: str, timeout: int = 0) -> None:
        """Set status bar message. If no message is shown, display default message.
        A timeout of 0 is treated as a permanent message and will not change unless reset with `clear_status()`.
        """
        self.status_bar.showMessage(message, timeout)

        if timeout == 0:
            self.status_text = message

        if timeout > 0:
            # Calls function once after the delay
            QTimer.singleShot(timeout, self._set_status_after_timeout)

    def handle_status_reset(self) -> None:
        """Reset status message to the default status message (not the last permanent one)."""
        self.status_text = DEFAULT_STATUS_BAR_MESSAGE
        self.status_bar.showMessage(self.status_text)

    def _set_status_after_timeout(self) -> None:
        """Gets the original status after a temporary one concludes."""
        self.status_bar.showMessage(self.status_text)

    def show_error(self, title: str, desc: str) -> None:
        """Show an error modal window. Only intended to be used by AppController."""
        QMessageBox.critical(self, title, desc)

    def show_warning(self, title: str, desc: str) -> None:
        """Show a warning modal window. Only intended to be used by AppController."""
        QMessageBox.warning(self, title, desc)

    def show_info(self, title: str, desc: str) -> None:
        """Show an informational modal window. Only intended to be used by AppController."""
        QMessageBox.information(self, title, desc)
