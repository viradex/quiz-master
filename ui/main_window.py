import sys
import ctypes
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QStackedWidget,
    QMessageBox,
)
from PyQt6.QtGui import QGuiApplication, QIcon
from PyQt6.QtCore import QUrl

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
        """Create MainWindow UI with the stacked widget for showing individual screens."""
        self.central = QWidget()
        self.setCentralWidget(self.central)

        self.stack = QStackedWidget()

        hbox = QHBoxLayout(self.central)
        hbox.addWidget(self.stack)

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

    def build_screens(self) -> None:
        """Build all eager screens."""
        self.screen_widgets = {}
        self.screen_logic = {}

        for screen in EAGER_SCREENS:
            self._build_screen(screen)

    def get_screen(self, screen: Screens) -> None:
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

    def show_warning(self, title: str, text: str) -> None:
        """Show warning modal box. Only intended to be used by AppController."""
        QMessageBox.warning(self, title, text)

    def show_error(self, title: str, text: str) -> None:
        """Show error modal box. Only intended to be used by AppController."""
        QMessageBox.critical(self, title, text)
