from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QToolButton,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QGraphicsDropShadowEffect,
)
from PyQt6.QtGui import QColor, QPixmap, QIcon
from PyQt6.QtCore import Qt, QSize, pyqtSignal

from utils.formatting import format_datetime


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
        self.icon_lbl = QLabel()
        if self.icon_path is not None:
            self.set_icon(self.icon_path)
        else:
            self.icon_lbl.setHidden(True)

        self.title_lbl = QLabel(self.title)
        self.title_lbl.setStyleSheet("font-size: 14px;" "color: #8A8A8A;")

        self.value_lbl = QLabel(self.value)
        self.value_lbl.setStyleSheet("font-size: 24px;" "font-weight: 600;")

        hbox_header = QHBoxLayout()
        hbox_header.setSpacing(6)
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

        file_path = self.icon_path.as_posix()
        pixmap = QPixmap(file_path).scaled(
            16,
            16,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self.icon_lbl.setPixmap(pixmap)


class QuizCard(QFrame):
    """Creates a quiz card, which is for the quiz manager and contains information and actions for a single quiz."""

    edit_quiz_requested = pyqtSignal(str)
    delete_quiz_requested = pyqtSignal(str)

    def __init__(
        self,
        quiz_id: str,
        quiz_title: str,
        total_questions: str | int,
        is_premade: bool,
        last_updated: datetime | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.quiz_id = quiz_id
        self.quiz_title = quiz_title
        self.total_questions = total_questions
        self.is_premade = is_premade
        self.last_updated = last_updated

        self.base_dir = Path(__file__).resolve().parent.parent
        self.icons_path = self.base_dir / "assets" / "icons"

        self.setup_component()

    def setup_component(self) -> None:
        self.setObjectName("quizCard")
        self.setStyleSheet("""
            QFrame#quizCard {
                background-color: #2B2B2B;
                border-radius: 10px;
            }
        """)

        self.title_lbl = QLabel(self.quiz_title)
        self.title_lbl.setStyleSheet("font-size: 20px;" "font-weight: 600;")

        self.questions_lbl = QLabel(
            f"{self.total_questions} {'question' if int(self.total_questions) == 1 else 'questions'}",
        )
        self.questions_lbl.setStyleSheet("font-size: 14px;" "color: #8A8A8A;")

        if self.last_updated is not None:
            formatted_date = format_datetime(self.last_updated, start_lower=True)
        else:
            formatted_date = "-"

        self.updated_lbl = QLabel(f"Updated {formatted_date}")
        self.updated_lbl.setStyleSheet("font-size: 12px;" "color: #8A8A8A;")

        if self.is_premade:
            self.updated_lbl.setHidden(True)

        delete_icon = self.icons_path / "delete.png"
        edit_icon = self.icons_path / "edit.png"

        self.delete_btn = QToolButton()
        self.delete_btn.setIcon(QIcon(delete_icon.as_posix()))
        self.delete_btn.setIconSize(QSize(24, 24))
        self.delete_btn.setFixedSize(28, 28)
        self.delete_btn.setToolTip("Delete")
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.setAutoRaise(True)
        self.delete_btn.clicked.connect(
            lambda: self.delete_quiz_requested.emit(self.quiz_id)
        )
        self.delete_btn.setStyleSheet("""
            QToolButton {
                background: transparent;
                border: none;
                padding: 0px;
            }
                                      
            QToolButton:hover {
                background: transparent;
                border: none;
            }
                                      
            QToolButton:pressed {
                background: transparent;
                border: none;
            }
        """)

        self.edit_btn = QToolButton()
        self.edit_btn.setIcon(QIcon(edit_icon.as_posix()))
        self.edit_btn.setIconSize(QSize(24, 24))
        self.edit_btn.setFixedSize(28, 28)
        self.edit_btn.setToolTip("Edit")
        self.edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.edit_btn.setAutoRaise(True)
        self.edit_btn.clicked.connect(
            lambda: self.edit_quiz_requested.emit(self.quiz_id)
        )
        self.edit_btn.setStyleSheet("""
            QToolButton {
                background: transparent;
                border: none;
                padding: 0px;
            }
                                      
            QToolButton:hover {
                background: transparent;
                border: none;
            }
                                      
            QToolButton:pressed {
                background: transparent;
                border: none;
            }
        """)

        # Must add parent=self, otherwise it will appear as a top-level window temporarily
        default_lbl = QLabel("Default Quiz", self)
        default_lbl.setToolTip("This quiz cannot be edited or deleted")
        default_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        default_lbl.setFixedSize(100, 30)
        default_lbl.setHidden(True)
        default_lbl.setStyleSheet("""
            QLabel {
                background-color: #383838;
                color: #dadada;
                border: 1px solid #5a5a5a;
                border-radius: 15px;
                font-size: 12px;
            }
        """)

        if self.is_premade:
            self.delete_btn.setHidden(True)
            self.edit_btn.setHidden(True)
            default_lbl.setHidden(False)

        vbox = QVBoxLayout()
        vbox.addWidget(self.title_lbl)
        vbox.addWidget(self.questions_lbl)
        vbox.addWidget(self.updated_lbl)

        btn_hbox = QHBoxLayout()
        btn_hbox.addStretch()
        btn_hbox.addWidget(self.edit_btn)
        btn_hbox.addSpacing(5)
        btn_hbox.addWidget(self.delete_btn)
        btn_hbox.addWidget(default_lbl)

        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(16, 12, 16, 12)
        hbox.addLayout(vbox)
        hbox.addLayout(btn_hbox)
