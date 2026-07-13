import sys
import ctypes
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QStackedWidget,
    QMessageBox,
    QStatusBar,
)
from PyQt6.QtGui import QIcon, QFontMetrics, QCloseEvent
from PyQt6.QtCore import Qt, QTimer

from core.app.screen_ids import Screens
from core.services.app_context import Services
from logic.app_controller.client import ClientAppController
from logic.app_controller.server import ServerAppController
from logic.app_controller.common import CommonAppController
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
        self.setup_theme()
        self.setup_font()
        self.setup_app_controllers()
        self.build_screens()

        self.go_to(STARTUP_SCREEN)

    def center_window(self) -> None:
        """Move the window to the center of the primary screen."""
        screen = QApplication.primaryScreen().availableGeometry()

        x = (screen.width() - WINDOW_WIDTH) // 2
        y = (screen.height() - WINDOW_HEIGHT) // 2

        self.move(x, y)

    def setup_icon(self) -> None:
        """Set up application icon."""
        base_dir = Path(__file__).resolve().parent
        icon_path = base_dir / "assets" / "icons" / "icon.ico"

        self.setWindowIcon(QIcon(str(icon_path)))

        # Set taskbar icon on Windows
        if sys.platform == "win32":
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "com.viradex.quizmaster"
            )

    def setup_theme(self) -> None:
        """Set up application theme. Forces dark mode even if the system is in light mode."""
        try:
            # Some versions don't have the setColorScheme() method
            QApplication.styleHints().setColorScheme(Qt.ColorScheme.Dark)
        except AttributeError:
            pass

    def setup_font(self) -> None:
        """Set up font details. Preloads emojis/glyphs width details so they do not lag the UI when rendering."""
        # Emojis/glyphs can cause a noticeable lag when showing a screen containing them for the first time.
        # To prevent that lag spike, make PyQt pre-calculate the width of the emojis to help with the rendering.
        metrics = QFontMetrics(self.font())
        metrics.horizontalAdvance("✔")
        metrics.horizontalAdvance("✖")

    def setup_ui(self) -> None:
        """Create MainWindow UI with the stacked widget for showing individual screens, as well as the status bar."""
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

        self.set_status(self.status_text)

    def setup_app_controllers(self) -> None:
        """Set up app controllers (global logic)."""
        self.client_app_controller = ClientAppController(self, self.services)
        self.server_app_controller = ServerAppController(self, self.services)
        self.common_app_controller = CommonAppController(self, self.services)

    def build_screens(self) -> None:
        """Initialize screen widgets and logic dictionary and build all eager screens."""
        self.screen_widgets: dict[Screens, BaseScreen] = {}
        self.screen_logic: dict[Screens, BaseLogic] = {}

        for screen in EAGER_SCREENS:
            self._build_screen(screen)

    def get_screen(self, screen: Screens) -> BaseScreen:
        """Gets a screen reference. If it does not exist, builds the screen."""
        if screen not in self.screen_widgets:
            self._build_screen(screen)

        return self.screen_widgets[screen]

    def go_to(self, screen: Screens, payload=None) -> None:
        """Navigate to another screen of the app with an optional data payload."""
        # Call lifecycle functions if screen is shown
        if self.current_screen is not None:
            self.current_screen.on_leave()
            self.current_logic.on_leave()

        # Setup screen and logic
        widget = self.get_screen(screen)
        logic = self.screen_logic[screen]

        self.stack.setCurrentWidget(widget)
        self.setWindowTitle(widget.title_text)

        # Call lifecycle functions
        widget.on_enter(payload)
        logic.on_enter()

        self.current_screen = widget
        self.current_logic = logic

    def set_title(self, title: str) -> None:
        """Change the application window title."""
        self.setWindowTitle(title)

    def set_status(self, message: str, timeout: int = 0) -> None:
        """Set status bar message, with optional timeout (in milliseconds).
        A timeout of 0 is treated as a permanent message and will not change unless reset with `reset_status()`.
        """
        self.status_bar.showMessage(message, timeout)

        # Permanent status
        if timeout == 0:
            self.status_text = message

        # Temporary status
        if timeout > 0:
            # Calls function once after the delay
            QTimer.singleShot(timeout, self._set_status_after_timeout)

    def reset_status(self) -> None:
        """Clear status bar message, resetting it to the default."""
        self.status_text = DEFAULT_STATUS_BAR_MESSAGE
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

    def closeEvent(self, event: QCloseEvent):
        if self.current_screen is not None:
            self.current_screen.on_window_close(event)

    def _build_screen(self, screen: Screens) -> None:
        """Build an individual screen and its respective logic."""
        widget, logic = create_screen_bundle(screen, self.services, self)

        self.screen_widgets[screen] = widget
        self.screen_logic[screen] = logic

        # Add screen to stacked widget
        self.stack.addWidget(widget)

        # Connect signals from the window to this main window
        widget.navigate.connect(self.go_to)
        widget.title_change.connect(self.set_title)
        widget.status.connect(self.set_status)
        widget.status_reset.connect(self.reset_status)

    def _set_status_after_timeout(self) -> None:
        """Gets the original status after a temporary one concludes."""
        self.status_bar.showMessage(self.status_text)
