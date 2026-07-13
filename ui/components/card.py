from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QGraphicsDropShadowEffect,
    QMessageBox,
)
from PyQt6.QtGui import QColor, QPixmap
from PyQt6.QtCore import Qt, pyqtSignal

from ui.components.input import ClickableLabel
from models.question import Question

from ui.components.button import create_tool_icon_button
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
            self.icon_lbl.hide()

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

        pixmap = QPixmap(str(self.icon_path)).scaled(
            16,
            16,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self.icon_lbl.setPixmap(pixmap)


class QuestionCard(QFrame):
    clicked = pyqtSignal(object)

    def __init__(
        self, question: Question, question_num: int | str, parent=None
    ) -> None:
        super().__init__(parent)
        self.question = question
        self.question_num = question_num

        self.selected = False

        # TODO add max height with ellipsis for question text if needed
        self.setup_component()

    def setup_component(self) -> None:
        # TODO PyQt won't wrap the text if it's unbroken (no spaces)
        # and the card will get infinitely longer
        self.question_num_lbl = QLabel(str(self.question_num))
        self.question_num_lbl.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )
        self.question_num_lbl.setFixedWidth(20)
        self.question_num_lbl.setStyleSheet("""
            QLabel {
                font-size: 16px;
                background-color: #404040;
                padding-top: 4px;
                font-weight: bold;
            }
        """)

        self.question_lbl = QLabel()
        self.question_lbl.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.question_lbl.setWordWrap(True)
        self.question_lbl.setStyleSheet(
            "font-size: 16px;" "background-color: #2b2b2b;" "padding: 8px 0px 8px 0px;"
        )
        self.update_question_text(self.question.question_text)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(self.question_num_lbl)
        hbox.addWidget(self.question_lbl)

        self.setFixedHeight(90)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("questionCard")
        self.setProperty("state", "deselected")
        self.setStyleSheet("""
            QFrame#questionCard[state="selected"] {
                border: 2px solid #57C6FF;
                background-color: #2b2b2b;
                border-radius: 4px;
            }
                           
            QFrame#questionCard[state="deselected"] {
                border: 2px solid #555;
                background-color: #2b2b2b;
                border-radius: 4px;
            }
                           
            QFrame#questionCard[state="error"] {
                border: 2px solid #C75A5A;
                background-color: #2b2b2b;
                border-radius: 4px;
            }
        """)
        self.setLayout(hbox)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.question)

        super().mousePressEvent(event)

    def select(self) -> None:
        self.setProperty("state", "selected")
        self.selected = True

        self._update_styles()

    def deselect(self) -> None:
        self.setProperty("state", "deselected")
        self.selected = False

        self._update_styles()

    def error(self) -> None:
        self.setProperty("state", "error")
        self.selected = False

        self._update_styles()

    def update_question_text(self, text: str) -> None:
        self.question_lbl.setText(text)

    def update_question_num(self, question_num: int | str) -> None:
        self.question_num = question_num
        self.question_num_lbl.setText(str(self.question_num))

    def _update_styles(self) -> None:
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()


class QuizCard(QFrame):
    """Creates a quiz card, which is for the quiz manager and contains information and actions for a single quiz."""

    edit_quiz_requested = pyqtSignal(str, str)
    delete_quiz_requested = pyqtSignal(str, str)

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

        self.default_clicked_counter = 0

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

        no_questions = int(self.total_questions) <= 0

        self.questions_lbl = QLabel(
            f"{self.total_questions} {'question' if int(self.total_questions) == 1 else 'questions'}",
        )
        self.questions_lbl.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                color: {'#C75A5A' if no_questions else '#8A8A8A'};
            }}
        """)

        if no_questions:
            self.questions_lbl.setToolTip("This quiz cannot be played")

        if self.last_updated is not None:
            formatted_date = format_datetime(self.last_updated, start_lower=True)
        else:
            formatted_date = "-"

        self.updated_lbl = QLabel(f"Updated {formatted_date}")
        self.updated_lbl.setStyleSheet("font-size: 12px;" "color: #8A8A8A;")

        if self.is_premade:
            self.updated_lbl.hide()

        delete_icon = self.icons_path / "delete.png"
        edit_icon = self.icons_path / "edit.png"

        self.delete_btn = create_tool_icon_button(delete_icon, "Delete", icon_size=24)
        self.delete_btn.clicked.connect(
            lambda: self.delete_quiz_requested.emit(self.quiz_id, self.quiz_title)
        )

        self.edit_btn = create_tool_icon_button(edit_icon, "Edit", icon_size=24)
        self.edit_btn.clicked.connect(
            lambda: self.edit_quiz_requested.emit(self.quiz_id, self.quiz_title)
        )

        # Must add parent=self, otherwise it will appear as a top-level window temporarily
        self.default_lbl = ClickableLabel("Default Quiz", self)
        self.default_lbl.setToolTip("This quiz cannot be edited or deleted")
        self.default_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.default_lbl.setFixedSize(100, 30)
        self.default_lbl.hide()
        self.default_lbl.unsetCursor()
        self.default_lbl.clicked.connect(self._on_default_clicked)
        self.default_lbl.setStyleSheet("""
            QLabel {
                background-color: #383838;
                color: #dadada;
                border: 1px solid #5a5a5a;
                border-radius: 15px;
                font-size: 12px;
            }
        """)

        if self.is_premade:
            self.delete_btn.hide()
            self.edit_btn.hide()
            self.default_lbl.setHidden(False)

        vbox = QVBoxLayout()
        vbox.addWidget(self.title_lbl)
        vbox.addWidget(self.questions_lbl)
        vbox.addWidget(self.updated_lbl)

        btn_hbox = QHBoxLayout()
        btn_hbox.addStretch()
        btn_hbox.addWidget(self.edit_btn)
        btn_hbox.addSpacing(5)
        btn_hbox.addWidget(self.delete_btn)
        btn_hbox.addWidget(self.default_lbl)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(16, 12, 16, 12)
        hbox.addLayout(vbox)
        hbox.addLayout(btn_hbox)

        self.setLayout(hbox)

    def _on_default_clicked(self) -> None:
        if not self.is_premade:
            return

        self.default_clicked_counter += 1

        if self.default_clicked_counter == 10:
            QMessageBox.information(
                self,
                " ",
                "Just a heads up, I'm not a button, even though I might look like one. Don't worry, it's a common mistake, for some reason.",
            )
        elif self.default_clicked_counter == 20:
            QMessageBox.warning(self, " ", "So we're just gonna keep clicking me, huh?")
        elif self.default_clicked_counter == 30:
            QMessageBox.warning(
                self, " ", "This isn't even funny anymore, just stop please."
            )
        elif self.default_clicked_counter == 40:
            QMessageBox.warning(self, " ", "This is your final warning...")
        elif self.default_clicked_counter == 50:
            QMessageBox.critical(
                self, " ", "Can't you listen? I'm a label, not a button! I'm done here."
            )
            self.default_lbl.hide()
