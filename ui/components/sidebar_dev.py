# TODO remove entire file when logic-based navigation implemented
from PyQt6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import pyqtSignal

from core.app.screen_ids import Screens


class SidebarDev(QWidget):
    screen_requested = pyqtSignal(Screens)

    def __init__(self, parent=None):
        super().__init__(parent)

        print(
            "WARNING!\nThe sidebar dev feature should not be used anymore - use logic-based switching instead! Using the sidebar to switch directly to screens can lead to bugs!"
        )

        self._setup_component()

    def _setup_component(self):
        title = QLabel("Screen Switcher\n(Dev)")
        title.setStyleSheet("font-size: 24px;" "font-weight: bold;")

        self.btn_grid = QGridLayout()
        self._setup_ui_nav()

        vbox = QVBoxLayout()
        vbox.addWidget(title)

        vbox.addLayout(self.btn_grid)
        vbox.addStretch(1)

        self.setLayout(vbox)

    def _setup_ui_nav(self):
        row = 0
        categories = {}

        for screen in Screens:
            category = screen.name.split("_")[0]

            if category not in categories:
                categories[category] = []

            categories[category].append(screen)

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
