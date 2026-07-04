from PyQt6.QtWidgets import QPushButton


# TODO this class was only really good for the prototype.
# Now, it's only really used for the styling. It should either
# have its extra features removed or be ported to a function.
class LeaveButton(QPushButton):
    """Configure a button that is styled to denote leaving the current screen for UI consistency."""

    def __init__(
        self, btn_text: str, btn_width: int = 60, do_confirm: bool = True
    ) -> None:
        super().__init__()
        self.btn_text = btn_text
        self.btn_width = btn_width
        self.do_confirm = do_confirm

        self.setup_component()

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
