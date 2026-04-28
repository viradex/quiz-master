# TODO remove entire file when logic-based navigation implemented
from PyQt6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import pyqtSignal

from core.screen_ids import Screens


class SidebarDev(QWidget):
    screen_requested = pyqtSignal(Screens)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setup_ui()

    def setup_ui(self):
        title = QLabel("Screen Switcher\n(Dev)")
        title.setStyleSheet("font-size: 24px;" "font-weight: bold;")

        self.btn_grid = QGridLayout()
        self.setup_ui_nav()

        vbox = QVBoxLayout()
        vbox.addWidget(title)

        vbox.addLayout(self.btn_grid)
        vbox.addStretch(1)

        self.setLayout(vbox)

    def setup_ui_nav(self):
        row = 0
        categories = {
            "CLIENT": [
                Screens.CLIENT_SETUP,
                Screens.CLIENT_LOBBY,
                Screens.CLIENT_MULTI_QUESTION,
                Screens.CLIENT_MULTI_RESULT,
                Screens.CLIENT_ENTRY_QUESTION,
                Screens.CLIENT_ENTRY_RESULT,
                Screens.CLIENT_FINAL_RESULT,
                Screens.CLIENT_DISCONNECT,
            ],
            "SERVER": [
                Screens.SERVER_LOBBY,
                Screens.SERVER_MULTI_QUESTION,
                Screens.SERVER_MULTI_RESULT,
                Screens.SERVER_ENTRY_QUESTION,
                Screens.SERVER_ENTRY_RESULT,
                Screens.SERVER_FINAL_RESULT,
            ],
            "COMMON": [
                Screens.COMMON_MENU,
                Screens.COMMON_LOADING,
                Screens.COMMON_ABOUT,
            ],
        }

        for category, screens in categories.items():
            heading = QLabel(category.title())
            heading.setStyleSheet("font-size: 18px;" "padding-top: 16px;")
            self.btn_grid.addWidget(heading, row, 0, 1, 3)

            row += 1

            for i, screen in enumerate(screens):
                btn_name = (
                    screen.name.replace(category + "_", " ").replace("_", " ").title()
                )

                button = QPushButton(btn_name)
                button.clicked.connect(lambda checked=False, s=screen: self.go_to(s))

                col = i % 2
                r = row + (i // 2)

                self.btn_grid.addWidget(button, r, col)

            row += (len(screens) + 2) // 2 + 1

    def go_to(self, screen: Screens):
        self.screen_requested.emit(screen)
