from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget, QFrame
from PyQt6.QtGui import QGuiApplication

from core.screen_ids import Screens
from core.screen_factory import create_screen

from ui.components.sidebar_dev import SidebarDev

# TODO change width from 1220 to 1000 when removing dev navbar
DEV_NAVBAR_WIDTH = 220
WIDTH = 1000 + DEV_NAVBAR_WIDTH
HEIGHT = 600


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setMinimumSize(WIDTH, HEIGHT)
        self.center_window()

        self.setup_ui()
        self.build_screens()
        self.wire_navigation()

        self.go_to(Screens.COMMON_MENU)

    def center_window(self):
        screen = QGuiApplication.primaryScreen().availableGeometry()

        x = (screen.width() - WIDTH) // 2
        y = (screen.height() - HEIGHT) // 2

        self.move(x, y)

    def setup_ui(self):
        self.central = QWidget()
        self.setCentralWidget(self.central)

        # TODO temp dev navigation navbar
        # remove when logic-based screen switching implemented
        self.sidebar = SidebarDev(self)
        self.sidebar.setFixedWidth(DEV_NAVBAR_WIDTH)

        # TODO remove when dev navbar removed
        line = QFrame()
        line.setStyleSheet("background-color: #444;")
        line.setFixedWidth(1)

        self.stack = QStackedWidget()

        # TODO remove when dev navbar removed
        hbox = QHBoxLayout(self.central)
        hbox.addWidget(self.sidebar)
        hbox.addWidget(line)
        hbox.addWidget(self.stack)

    def build_screens(self):
        self.screen_widgets = {}

        for screen in Screens:
            widget = create_screen(screen, self)
            self.screen_widgets[screen] = widget
            self.stack.addWidget(widget)

    def wire_navigation(self):
        for screen in self.screen_widgets.values():
            screen.navigate.connect(self.go_to)

        self.sidebar.screen_requested.connect(self.go_to)

    def go_to(self, screen: Screens):
        widget = self.screen_widgets[screen]
        self.stack.setCurrentWidget(widget)

        self.setWindowTitle(widget.title_text)
        widget.on_enter()
