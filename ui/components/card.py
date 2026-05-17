from PyQt6.QtWidgets import QFrame, QGraphicsDropShadowEffect
from PyQt6.QtGui import QColor


class Card(QFrame):
    def __init__(
        self,
        parent=None,
        radius=20,
        blur_radius=30,
        accent=None,
    ):
        super().__init__(parent)
        self.blur_radius = blur_radius
        self.radius = radius
        self.accent = self._to_color(accent) if accent else None

        self.setObjectName("card")

        self._apply_style()
        self._apply_shadow()

    def _apply_style(self):
        border_color = "#2A2A2A"

        if self.accent:
            border_color = self.accent.name()

        self.setStyleSheet(f"""
            QFrame#card {{
                background-color: #1E1E1E;
                border: 1px solid {border_color};
                border-radius: {self.radius}px;
            }}
        """)

    def _apply_shadow(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(self.blur_radius)
        shadow.setOffset(0, 6)

        if self.accent:
            color = QColor(self.accent)
            color.setAlpha(120)
        else:
            color = QColor(0, 0, 0, 160)

        shadow.setColor(color)
        self.setGraphicsEffect(shadow)

    def set_accent(self, accent):
        self.accent = self._to_color(accent)
        self._apply_style()
        self._apply_shadow()

    def clear_accent(self):
        self.accent = None
        self._apply_style()
        self._apply_shadow()

    def _to_color(self, value):
        if isinstance(value, QColor):
            return value
        return QColor(value)
