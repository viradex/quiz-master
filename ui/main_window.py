from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget
from PyQt6.QtGui import QGuiApplication

from core.screen_ids import Screens
from core.screen_factory import create_screen

WIDTH = 1000
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

        self.layout = QHBoxLayout(self.central)

        self.stack = QStackedWidget()
        self.layout.addWidget(self.stack)

    def build_screens(self):
        self.screen_widgets = {}

        for screen in Screens:
            widget = create_screen(screen, self)
            self.screen_widgets[screen] = widget
            self.stack.addWidget(widget)

    def wire_navigation(self):
        for screen in self.screen_widgets.values():
            screen.navigate.connect(self.go_to)

    def go_to(self, screen: Screens):
        widget = self.screen_widgets[screen]
        self.stack.setCurrentWidget(widget)

        self.setWindowTitle(widget.title_text)
        widget.on_enter()
