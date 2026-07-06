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
    """Creates a card. This serves no purpose other than looking visually aesthetic."""

    def __init__(
        self,
        radius: int = 20,
        blur_radius: int = 30,
        accent: QColor | str | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.blur_radius: int = blur_radius
        self.radius: int = radius
        self.accent: QColor | None = self._to_color(accent) if accent else None

        self.setup_component()

    def setup_component(self) -> None:
        border_color = "#2A2A2A"

        if self.accent:
            border_color = self.accent.name()

        self.setObjectName("card")
        self.setStyleSheet(f"""
            QFrame#card {{
                background-color: #1E1E1E;
                border: 1px solid {border_color};
                border-radius: {self.radius}px;
            }}
        """)

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

    def set_accent(self, accent) -> None:
        """Set custom accent."""
        self.accent = self._to_color(accent)
        self.setup_component()

    def reset_accent(self) -> None:
        """Clear custom accent."""
        self.accent = None
        self.setup_component()

    def _to_color(self, value: QColor | str) -> QColor:
        """Convert a color to a QColor, if it not already one."""
        if isinstance(value, QColor):
            return value
        return QColor(value)


class StatCard(QFrame):
    """Creates a statistic card, which is smaller than a normal Card and has a pre-determined layout."""

    def __init__(
        self,
        title: str,
        value: str,
        icon_path: Path | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.title = title
        self.value = value
        self.icon_path = icon_path

        self.setup_component()

    def setup_component(self) -> None:
        self.setObjectName("statCard")
        self.setStyleSheet("""
            QFrame#statCard {
                background-color: #2B2B2B;
                border-radius: 10px;
            }
        """)

        # Shows icon if provided
        if self.icon_path is not None:
            self.icon_lbl = QLabel()
            self.set_icon(self.icon_path)

        self.title_lbl = QLabel(self.title)
        self.title_lbl.setStyleSheet("""
            font-size: 14px;
            color: #8A8A8A;
        """)

        self.value_lbl = QLabel(self.value)
        self.value_lbl.setStyleSheet("""
            font-size: 24px;
            font-weight: 600;
        """)

        hbox_header = QHBoxLayout()
        hbox_header.setSpacing(6)

        if self.icon_path is not None:
            hbox_header.addWidget(self.icon_lbl)

        hbox_header.addWidget(self.title_lbl)
        hbox_header.addStretch()

        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(12, 10, 12, 10)
        vbox.setSpacing(2)
        vbox.addLayout(hbox_header)
        vbox.addSpacing(5)
        vbox.addWidget(self.value_lbl)

    def set_title(self, title: str) -> None:
        """Set title of stat card."""
        self.title = title
        self.title_lbl.setText(title)

    def set_value(self, value: str) -> None:
        """Set value of stat card."""
        self.value = value
        self.value_lbl.setText(value)

    def set_icon(self, icon_path: Path) -> None:
        """Set icon of stat card. Must be a valid path."""
        self.icon_path = icon_path
        pixmap = QPixmap(self.icon_path.as_posix()).scaled(
            16,
            16,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self.icon_lbl.setPixmap(pixmap)
