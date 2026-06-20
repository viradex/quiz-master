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
from logic.app_controller import AppController
from ui.components.music_player import BackgroundMusicPlayer

from core.app.screen_factory import create_screen_bundle
from core.config.constants import (
    EAGER_SCREENS,
    STARTUP_SCREEN,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
)

# TODO make it a ui setting
PLAY_BACKGROUND_MUSIC = False


class MainWindow(QMainWindow):
    def __init__(self, services):
        super().__init__()
        self.services = services

        self.current_screen = None
        self.current_logic = None

        self.setMinimumSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.center_window()

        if PLAY_BACKGROUND_MUSIC:
            self.setup_music()

        self.setup_ui()
        self.setup_icon()
        self.setup_app_controller()
        self.build_screens()

        self.go_to(STARTUP_SCREEN)

    def center_window(self):
        screen = QGuiApplication.primaryScreen().availableGeometry()

        x = (screen.width() - WINDOW_WIDTH) // 2
        y = (screen.height() - WINDOW_HEIGHT) // 2

        self.move(x, y)

    def setup_music(self):
        base_dir = Path(__file__).resolve().parent
        music_path = base_dir / "assets" / "audio" / "background.wav"
        url = QUrl.fromLocalFile(music_path.as_posix())

        self.background_music_player = BackgroundMusicPlayer(url)
        self.background_music_player.start()

    def setup_icon(self):
        base_dir = Path(__file__).resolve().parent
        icon_path = base_dir / "assets" / "icons" / "icon.ico"

        self.setWindowIcon(QIcon(icon_path.as_posix()))

        # Set taskbar icon on Windows
        if sys.platform == "win32":
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "com.viradex.quizmaster"
            )

    def setup_ui(self):
        self.central = QWidget()
        self.setCentralWidget(self.central)

        self.stack = QStackedWidget()

        hbox = QHBoxLayout(self.central)
        hbox.addWidget(self.stack)

    def setup_app_controller(self):
        self.app_controller = AppController(self, self.services)

    def _build_screen(self, screen):
        widget, logic = create_screen_bundle(screen, self.services, self)

        self.screen_widgets[screen] = widget
        self.screen_logic[screen] = logic

        self.stack.addWidget(widget)

        widget.navigate.connect(self.go_to)

    def build_screens(self):
        self.screen_widgets = {}
        self.screen_logic = {}

        for screen in EAGER_SCREENS:
            self._build_screen(screen)

    def get_screen(self, screen: Screens):
        if screen not in self.screen_widgets:
            self._build_screen(screen)

        return self.screen_widgets[screen]

    def go_to(self, screen: Screens, payload=None):
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

    def show_warning(self, title, text):
        QMessageBox.warning(self, title, text)
