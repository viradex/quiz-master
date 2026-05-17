from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import pyqtSignal

from ui.components.dialogs import confirm_warning


class LeaveButton(QPushButton):
    confirm_leave = pyqtSignal()

    def __init__(self, btn_text, btn_width=60):
        super().__init__()
        self.btn_text = btn_text
        self.btn_width = btn_width

        self.setup_component()
        self.clicked.connect(self.on_clicked)

    def setup_component(self):
        self.setText(self.btn_text)
        self.setFixedWidth(self.btn_width)

        self.setObjectName("leave")
        self.setStyleSheet("""
            QPushButton#leave {
                background-color: transparent;
                color: #bbb;
                border: 1px solid #444;
                border-radius: 8px;
                padding: 6px;
                font-size: 12px;
            }

            QPushButton#leave:hover {
                background-color: #333;
                color: white;
            }

            QPushButton#leave:pressed {
                background-color: #222;
            }
        """)

    def on_clicked(self):
        confirm = confirm_warning(
            self,
            "Confirm Leaving",
            "Are you sure you want to leave and return to menu?",
        )
        if confirm:
            self.confirm_leave.emit()
