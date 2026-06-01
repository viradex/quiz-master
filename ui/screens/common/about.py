from pathlib import Path
from PyQt6.QtWidgets import QWidget, QTabWidget, QLabel, QPlainTextEdit, QVBoxLayout
from PyQt6.QtGui import QFont

from ui.screens.base_screen import BaseScreen


class CommonAboutScreen(BaseScreen):
    title_text = "Quiz Master – About"

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setup_ui()

    def setup_ui(self):
        vbox = QVBoxLayout()
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 0;
            }
        """)

        tabs.addTab(AboutTab(), "About")
        tabs.addTab(HelpTab(), "Help")

        vbox.addWidget(tabs, stretch=1)
        self.setLayout(vbox)


class AboutTab(QWidget):
    def __init__(self):
        super().__init__()

        self.license_text = self.get_license_text()

        self.setup_tab()
        self.setup_keys()

    def setup_tab(self):
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)

        title = QLabel("About Quiz Master")
        title.setFont(title_font)

        desc_font = QFont()
        desc_font.setPointSize(12)

        desc = QLabel("Designed, programmed, and tested by Arnav Thorat (2026).")
        desc.setFont(desc_font)

        license_info_font = QFont()
        license_info_font.setPointSize(10)

        license_info = QLabel(
            "Quiz Master is open-source software licensed under the GNU GPL v3.0.\nThis application uses PyQt6, which is licensed under the GNU GPL. The full license text is provided below."
        )
        license_info.setWordWrap(True)
        license_info.setFont(license_info_font)

        self.license_area = QPlainTextEdit()
        self.license_area.setReadOnly(True)
        self.license_area.setFixedWidth(500)
        self.license_area.setPlainText(self.license_text)

        vbox = QVBoxLayout()
        vbox.addWidget(title)
        vbox.addSpacing(2)
        vbox.addWidget(desc)
        vbox.addSpacing(10)
        vbox.addWidget(license_info)
        vbox.addSpacing(5)
        vbox.addWidget(self.license_area, stretch=1)

        self.setLayout(vbox)

    def setup_keys(self):
        self.target = "catsarebetterthandogs"
        self.index = 0
        self.showing_license = True

        self.setFocusPolicy(self.focusPolicy().StrongFocus)

    def get_license_text(self):
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        license_path = base_dir / "LICENSE"

        try:
            license_text = license_path.read_text(encoding="utf-8")
        except OSError:
            license_text = "Could not load license file."

        return license_text

    def keyPressEvent(self, event):
        key = event.text().lower()
        if not key:
            return

        expected = self.target[self.index]

        if key == expected:
            self.index += 1

            if self.index == len(self.target):
                self.on_sequence_completion()
                self.index = 0
        else:
            self.index = 0

    def on_sequence_completion(self):
        if self.showing_license:
            self.license_area.setPlainText(
                r"""Why are you being so one-sided? All animals are equal!

...

But some animals are more equal than others.

|\---/|
| o_o |
 \_^_/

Meow."""
            )
            self.showing_license = False
        else:
            self.license_area.setPlainText(self.license_text)
            self.showing_license = True


class HelpTab(QWidget):
    def __init__(self):
        super().__init__()

        self.setup_tab()

    def setup_tab(self):
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)

        title = QLabel("Program Help")
        title.setFont(title_font)

        desc_font = QFont()
        desc_font.setPointSize(12)

        desc = QLabel("This page is a work-in-progress!")
        desc.setFont(desc_font)

        vbox = QVBoxLayout()
        vbox.addWidget(title)
        vbox.addSpacing(2)
        vbox.addWidget(desc)
        vbox.addStretch(1)

        self.setLayout(vbox)
