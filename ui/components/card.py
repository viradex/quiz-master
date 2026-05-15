from PyQt6.QtWidgets import QFrame
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QGraphicsDropShadowEffect


class Card(QFrame):
    def __init__(
        self,
        parent=None,
        radius=20,
        blur_radius=30,
    ):
        super().__init__(parent)
        self.blur_radius = blur_radius

        self.setObjectName("Card")
        self.setStyleSheet(f"""
            QFrame#Card {{
                background-color: #1E1E1E;
                border: 1px solid #2A2A2A;
                border-radius: {radius}px;
            }}
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(self.blur_radius)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 160))
        self.setGraphicsEffect(shadow)
