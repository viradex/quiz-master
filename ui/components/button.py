from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import pyqtSignal

from ui.components.dialogs import confirm_warning


# TODO this class was only really good for the prototype.
# Now, it's only really used for the styling. It should either
# have its extra features removed or be ported to a function.
class LeaveButton(QPushButton):
    """Configure a button that is styled to denote leaving the current screen for UI consistency."""

    confirm_leave = pyqtSignal()

    def __init__(
        self, btn_text: str, btn_width: int = 60, do_confirm: bool = True
    ) -> None:
        super().__init__()
        self.btn_text = btn_text
        self.btn_width = btn_width
        self.do_confirm = do_confirm

        self.setup_component()
        self.clicked.connect(self.on_clicked)

    def setup_component(self) -> None:
        self.setText(self.btn_text)
        self.setFixedWidth(self.btn_width)

        self.setObjectName("leave")
        self.setStyleSheet(f"""
            QPushButton#leave {{
                background-color: transparent;
                color: #bbb;
                border: 1px solid #444;
                border-radius: 8px;
                padding: 6px;
                font-size: 12px;
            }}

            QPushButton#leave:hover {{
                background-color: #333;
                color: white;
            }}

            QPushButton#leave:pressed {{
                background-color: #222;
            }}
        """)

    def on_clicked(self):
        if self.do_confirm:
            confirm = confirm_warning(
                self,
                "Confirm Leaving",
                "Are you sure you want to leave and return to menu?",
            )
        else:
            confirm = True

        if confirm:
            self.confirm_leave.emit()
