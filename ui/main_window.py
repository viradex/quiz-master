from pathlib import Path
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtCore import QUrl

from core.screen_ids import Screens
from core.screen_factory import create_screen
from core.screen_config import EAGER_SCREENS

from ui.components.sidebar_dev import SidebarDev
from ui.components.music_player import BackgroundMusicPlayer

# TODO change width from 1220 to 1000 when removing dev navbar
DEV_NAVBAR_WIDTH = 220
WIDTH = 1000 + DEV_NAVBAR_WIDTH
HEIGHT = 600

# TODO make it a ui setting
PLAY_BACKGROUND_MUSIC = False


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.current_screen = None

        self.setMinimumSize(WIDTH, HEIGHT)
        self.center_window()

        if PLAY_BACKGROUND_MUSIC:
            self.setup_music()

        self.setup_ui()
        self.build_screens()
        self.wire_navigation()

        self.go_to(Screens.COMMON_MENU)

    def center_window(self):
        screen = QGuiApplication.primaryScreen().availableGeometry()

        x = (screen.width() - WIDTH) // 2
        y = (screen.height() - HEIGHT) // 2

        self.move(x, y)

    def setup_music(self):
        base_dir = Path(__file__).resolve().parent
        music_path = base_dir / "assets" / "audio" / "background.wav"
        url = QUrl.fromLocalFile(music_path.as_posix())

        self.background_music_player = BackgroundMusicPlayer(url)
        self.background_music_player.start()

    def setup_ui(self):
        self.central = QWidget()
        self.setCentralWidget(self.central)

        # TODO temp dev navigation navbar
        # remove when logic-based screen switching implemented
        self.sidebar = SidebarDev(self)
        self.sidebar.setFixedWidth(DEV_NAVBAR_WIDTH)

        # TODO remove when dev navbar removed
        line = QWidget()
        line.setStyleSheet("background-color: #444;")
        line.setFixedWidth(1)

        self.stack = QStackedWidget()

        # TODO remove when dev navbar removed
        hbox = QHBoxLayout(self.central)
        hbox.addWidget(self.sidebar)
        hbox.addWidget(line)
        hbox.addWidget(self.stack)

    def _build_screen(self, screen):
        widget = create_screen(screen, self)
        self.screen_widgets[screen] = widget
        self.stack.addWidget(widget)

        widget.navigate.connect(self.go_to)

    def build_screens(self):
        self.screen_widgets = {}

        for screen in EAGER_SCREENS:
            self._build_screen(screen)

    def get_screen(self, screen: Screens):
        if screen not in self.screen_widgets:
            self._build_screen(screen)

        return self.screen_widgets[screen]

    def wire_navigation(self):
        for screen in self.screen_widgets.values():
            screen.navigate.connect(self.go_to)

        self.sidebar.screen_requested.connect(self.go_to)

    def go_to(self, screen: Screens):
        if self.current_screen is not None:
            self.current_screen.on_leave()

        widget = self.get_screen(screen)
        self.stack.setCurrentWidget(widget)

        self.setWindowTitle(widget.title_text)
        widget.on_enter()

        self.current_screen = widget
