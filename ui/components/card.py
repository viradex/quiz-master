from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QGraphicsDropShadowEffect,
)
from PyQt6.QtGui import QColor, QPixmap
from PyQt6.QtCore import Qt


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


# TODO change to class
# class has broken styling
def make_stat_card(title, value, icon_path: Path | None = None):
    container = QWidget()
    container.setStyleSheet("""
        background-color: #2B2B2B;
        border-radius: 10px;
    """)

    layout = QVBoxLayout(container)
    layout.setContentsMargins(12, 10, 12, 10)
    layout.setSpacing(2)

    header_layout = QHBoxLayout()
    header_layout.setSpacing(6)

    if icon_path is not None:
        icon_path = Path(icon_path)

        icon_lbl = QLabel()

        pixmap = QPixmap(str(icon_path))
        pixmap = pixmap.scaled(
            16,
            16,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        icon_lbl.setPixmap(pixmap)
        header_layout.addWidget(icon_lbl)

    title_lbl = QLabel(title)
    title_lbl.setStyleSheet("""
        font-size: 14px;
        color: #8A8A8A;
    """)

    header_layout.addWidget(title_lbl)
    header_layout.addStretch(1)

    value_lbl = QLabel(value)
    value_lbl.setStyleSheet("""
        font-size: 24px;
        font-weight: 600;
    """)

    layout.addLayout(header_layout)
    layout.addSpacing(5)
    layout.addWidget(value_lbl)

    return container
