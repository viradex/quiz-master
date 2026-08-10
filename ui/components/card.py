"""
card.py

Contains various types of UI cards for different parts of the application.
"""

from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QIcon, QMouseEvent, QPixmap
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from models.question import Question
from models.quiz import Quiz
from ui.components.button import create_tool_icon_button
from ui.components.input import ClickableLabel
from utils.formatting import format_datetime
from utils.paths import get_icons_dir


class Card(QFrame):
    """
    Creates a card. This serves no purpose other than for visual UI purposes and section separation while
    appearing modern and cleaner than separator lines. Contains a background blur as well and custom accent
    color, if specified. Inherits `QFrame`.

    Arguments:
        radius: The radius of the corners of the card, in pixels. Defaults to 20. An integer is used as the
            radius must be a whole number.

        blur_radius: The amount to spread the blue (higher values give more spreading). Defaults to 30.
            An integer is used as the radius must be a whole number.

        accent: The color to set the accent color to (aka the border color). Defaults to None, in which case
            it will be set as #2a2a2a. A string or QColor is accepted as the value is turned into a QColor.

        parent: The parent to make this card a child of, or None to set no parent. Defaults to None.
    """

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

        # Set accent to a QColor from a string, or None
        self.accent: QColor | None = QColor(accent) if accent else None

        self._setup_component()

    def _setup_component(self) -> None:
        """
        Internal method. Sets up the component UI, such as widgets. This method can be called when wanting to
        refresh the card UI, for example, when resetting the accent.

        Returns:
            None.
        """
        # Default border color if no accent specified
        border_color = "#2a2a2a"

        if self.accent:
            border_color = self.accent.name()

        # Set object name to prevent child QFrames from being styled the same
        self.setObjectName("card")
        self.setStyleSheet(f"""
            QFrame#card {{
                background-color: #1e1e1e;
                border: 1px solid {border_color};
                border-radius: {self.radius}px;
            }}
        """)

        # Set blur
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(self.blur_radius)
        shadow.setOffset(0, 6)

        # Sets blur to the same color as the accent, or black
        if self.accent:
            color = QColor(self.accent)
            color.setAlpha(120)
        else:
            color = QColor(0, 0, 0, 160)

        shadow.setColor(color)
        self.setGraphicsEffect(shadow)

    def set_accent(self, accent: QColor | str) -> None:
        """
        Change the accent of the card to the specified accent and refresh the card to reflect changes.

        Arguments:
            accent: The color to set the accent color to (aka the border color).

        Returns:
            None.
        """
        self.accent = QColor(accent)
        self._setup_component()

    def reset_accent(self) -> None:
        """
        Reset the accent of the card to be the default accent of #2a2a2a and refresh the card to reflect
        changes.

        Returns:
            None.
        """
        self.accent = None
        self._setup_component()


class StatCard(QFrame):
    """
    Creates a statistic card. This serves no purpose other than for visual UI purposes and consistency with
    multiple statistic cards, as well as providing a clean API for modifying the values of the cards.
    Inherits `QFrame`.

    Arguments:
        title: The title of the statistic card. A string is used as it easily accepts various characters.

        value: The value, or actual statistic, of the statistic card. A string is used as it easily accepts
            various characters.

        icon_path: Optionally specify the icon that the statistic card should utilize. Defaults to None, in
            which case no icon will be used. A Path and string are both accepted as the Path will be turned
            into a string, but the Path is accepted for convenience.

        parent: The parent to make this card a child of, or None to set no parent. Defaults to None.
    """

    def __init__(
        self,
        title: str,
        value: str,
        icon_path: Path | str | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.title: str = title
        self.value: str = value
        self.icon_path: Path | str = icon_path

        self._setup_component()

    def _setup_component(self) -> None:
        """
        Internal method. Sets up the component UI, such as widgets and layouts. This method should only be
        called once, preferably in the initialization logic.

        Returns:
            None.
        """
        # Ensure styles don't apply to children QFrames by setting object name
        self.setObjectName("statCard")
        self.setStyleSheet("""
            QFrame#statCard {
                background-color: #2b2b2b;
                border-radius: 10px;
            }
        """)

        # Widgets setup
        self.icon_lbl = QLabel(self)

        # Shows icon if provided
        if self.icon_path is not None:
            self.set_icon(self.icon_path)
        else:
            self.icon_lbl.hide()

        self.title_lbl = QLabel(self.title)
        self.title_lbl.setStyleSheet("font-size: 14px;" "color: #8a8a8a;")

        self.value_lbl = QLabel(self.value)
        self.value_lbl.setStyleSheet("font-size: 24px;" "font-weight: 600;")

        # Layouts setup
        hbox_header = QHBoxLayout()
        hbox_header.setSpacing(6)
        hbox_header.addWidget(self.icon_lbl)
        hbox_header.addWidget(self.title_lbl)
        hbox_header.addStretch()

        vbox = QVBoxLayout()
        vbox.setContentsMargins(12, 10, 12, 10)
        vbox.setSpacing(2)
        vbox.addLayout(hbox_header)
        vbox.addSpacing(5)
        vbox.addWidget(self.value_lbl)

        self.setLayout(vbox)

    def set_title(self, title: str) -> None:
        """
        Set and update the title of the statistic card on the UI.

        Arguments:
            title: The title of the statistic card. A string is used as it easily accepts various characters.

        Returns:
            None.
        """
        self.title = title
        self.title_lbl.setText(self.title)

    def set_value(self, value: str) -> None:
        """
        Set and update the value/statistic of the statistic card on the UI.

        Arguments:
            value: The value, or actual statistic, of the statistic card. A string is used as it easily accepts
                various characters.

        Returns:
            None.
        """
        self.value = value
        self.value_lbl.setText(self.value)

    def set_icon(self, icon_path: Path | str) -> None:
        """
        Set and update the icon of the statistic card by providing a direct path to the asset to use. The icon
        keeps its aspect ratio, but is scaled to be 16x16 pixels.

        icon_path: The path to an icon that the statistic card should utilize. A Path and string are both
            accepted as the Path will be turned into a string, but the Path is accepted for convenience.

        Returns:
            None.
        """
        self.icon_path = icon_path

        # Resize image to 16x16 while keeping aspect ratio and ensuring icon
        # does not lose clarity by doing a smooth (bilinear filtering) transformation.
        pixmap = QPixmap(str(self.icon_path)).scaled(
            16,
            16,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self.icon_lbl.setPixmap(pixmap)


class QuestionCard(QFrame):
    """
    Creates a question card. Used for showing a card representing a question on the sidebar in the quiz
    editor, and allows clicking the card to switch to the question. Inherits `QFrame`.

    Attributes:
        clicked: A `pyqtSignal` that emits when the user clicks this question card. The Question object that
            this card is connected to is passed as an argument, primarily for the question ID.

    Arguments:
        question: The Question that the card represents, used for emitting the signal when clicked and passing
            the Question, and for also getting the question text. A Question is used to ensure ease of use
            without multiple separate parameters for the ID and question text.

        question_num: The question number of this question. Both a string and integer are accepted, for ease
            of use, however it is converted to a string for UI display.

        parent: The parent to make this card a child of, or None to set no parent. Defaults to None.
    """

    clicked = pyqtSignal(Question)

    def __init__(
        self, question: Question, question_num: int | str, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.question: Question = question
        self.question_num: int | str = question_num

        self.selected: bool = False

        self._setup_component()

    def _setup_component(self) -> None:
        """
        Internal method. Sets up the component UI, such as widgets and layouts. This method should only be
        called once, preferably in the initialization logic.

        Returns:
            None.
        """
        # Main widget setup
        self.setFixedHeight(90)

        # Set cursor to a hand to visually show it can be clicked
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Set object name to prevent child QFrames from being styled the same,
        # and property to change the type of style without manually specifying
        # new QSS.
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

        # Child widgets setup
        # The number is shown at the top on its own strip on the left of the card
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

        # The question text is displayed on the remaining area of the card
        self.question_lbl = QLabel()
        self.question_lbl.setText(self.question.question_text)
        self.question_lbl.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.question_lbl.setWordWrap(True)
        self.question_lbl.setStyleSheet(
            "font-size: 16px;" "background-color: #2b2b2b;" "padding: 8px 0px 8px 0px;"
        )

        # Layout setup, set no margins to ensure no wasted space
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(self.question_num_lbl)
        hbox.addWidget(self.question_lbl)

        self.setLayout(hbox)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Called automatically by PyQt when the widget is clicked. If the left mouse button was clicked, emits
        a signal identifying that the question was clicked.

        Arguments:
            event: An argument passed automatically by PyQt upon this method being run. This attribute is used
                to identify the type of mouse button that was pressed.

        Returns:
            None.
        """
        # Inform window to switch to the question if left clicked
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.question)

        super().mousePressEvent(event)

    def select(self) -> None:
        """
        Changes the card style to visually display that the card is currently selected. This does not actually
        select the card.

        Returns:
            None.
        """
        self.setProperty("state", "selected")
        self.selected = True

        self._refresh_styles()

    def deselect(self) -> None:
        """
        Changes the card style to visually display that the card is currently not selected. This does not
        actually deselect the card.

        Returns:
            None.
        """
        self.setProperty("state", "deselected")
        self.selected = False

        self._refresh_styles()

    def error(self) -> None:
        """
        Changes the card style to visually display that the card is currently not selected and that the question
        currently contains an error. This does not actually deselect the card.

        Returns:
            None.
        """
        self.setProperty("state", "error")
        self.selected = False

        self._refresh_styles()

    def update_question_text(self, text: str) -> None:
        """
        Update the question text of the UI on the card. This does not modify the actual Question object.

        Arguments:
            text: The new question text to replace the old one with and to display on the UI. A string is used
                as it is an easy way to display a vast array of characters.

        Returns:
            None.
        """
        self.question_lbl.setText(text)

    def update_question_num(self, question_num: int | str) -> None:
        """
        Update the question number of the UI on the card.

        Arguments:
            question_num: The question number of this question. Both a string and integer are accepted, for ease
                of use, however it is converted to a string for UI display.

        Returns:
            None.
        """
        self.question_num = question_num
        self.question_num_lbl.setText(str(self.question_num))

    def _refresh_styles(self) -> None:
        """
        Internal method. Update styles so changes to the property of the QSS stylesheet are applied visually.
        This method should be called anytime after running `setProperty()`.

        Returns:
            None.
        """
        # Refresh styles to reflect any changes to the property
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()


class QuizCard(QFrame):
    """
    Creates a quiz card. Used for showing a card representing a quiz in the quiz manager, containing information
    about the quiz. Also allows performing actions on a quiz through action buttons. Inherits `QFrame`.

    Attributes:
        edit_quiz_requested: A `pyqtSignal` that emits when the user clicks the Edit button, or Preview button if
            the quiz is a premade/default quiz. The Quiz object that this card is connected to is passed as an
            argument, primarily for the quiz ID.

        delete_quiz_requested: A `pyqtSignal` that emits when the user clicks the Delete button. The Quiz object
            that this card is connected to is passed as an argument, primarily for the quiz ID.

    Arguments:
        quiz: The Quiz that the card represents, used for emitting signals when clicking the action buttons and
            passing the Question, and for also getting certain quiz metadata. A Quiz is used to ensure ease of
            use without multiple separate parameters for different quiz details.

        parent: The parent to make this card a child of, or None to set no parent. Defaults to None.
    """

    edit_quiz_requested = pyqtSignal(Quiz)
    delete_quiz_requested = pyqtSignal(Quiz)

    def __init__(self, quiz: Quiz, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.quiz: Quiz = quiz

        # Used to count the number of times the 'default quiz' label was clicked
        self._default_clicked_counter: int = 0

        self._setup_component()

    def _setup_component(self) -> None:
        """
        Internal method. Sets up the component UI, such as widgets and layouts. This method should only be
        called once, preferably in the initialization logic.

        Returns:
            None.
        """
        # Set object name to prevent child QFrames from being styled the same
        self.setObjectName("quizCard")
        self.setStyleSheet("""
            QFrame#quizCard {
                background-color: #2b2b2b;
                border-radius: 10px;
            }
        """)

        # Widgets setup
        # Make title color red if it is incomplete
        self.title_lbl = QLabel(self.quiz.quiz_title)
        self.title_lbl.setStyleSheet(f"""
            QLabel {{
                font-size: 20px;
                font-weight: 600;
                color: {'#D86B6B' if not self.quiz.is_complete else 'white'};
            }}
        """)

        # Show tooltip warning if incomplete
        if not self.quiz.is_complete:
            self.title_lbl.setToolTip("This quiz cannot be played")

        # Shows number of questions
        total_questions = len(self.quiz.questions)

        self.questions_lbl = QLabel(
            f"{total_questions} {'question' if total_questions == 1 else 'questions'}",
        )
        self.questions_lbl.setStyleSheet("font-size: 14px;" "color: #8a8a8a;")

        # Formats datetime to start with lowercase as it is in the middle of a sentence
        if self.quiz.updated_at is not None:
            formatted_date = format_datetime(self.quiz.updated_at, start_lower=True)
        else:
            formatted_date = "-"

        # This label is hidden if the quiz is a default quiz, therefore must explicitly set parent=self
        self.updated_lbl = QLabel(f"Updated {formatted_date}", self)
        self.updated_lbl.setHidden(self.quiz.is_premade)
        self.updated_lbl.setStyleSheet("font-size: 12px;" "color: #8a8a8a;")

        # Create action buttons
        delete_icon = get_icons_dir() / "delete.png"
        edit_icon = get_icons_dir() / "edit.png"

        self.delete_btn = create_tool_icon_button(delete_icon, "Delete", icon_size=24)
        self.delete_btn.clicked.connect(
            lambda: self.delete_quiz_requested.emit(self.quiz)
        )

        # Must be explicitly made a child of 'self' otherwise it will briefly appear as a pop-up window
        self.edit_btn = create_tool_icon_button(
            edit_icon, "Edit", icon_size=24, parent=self
        )
        self.edit_btn.clicked.connect(lambda: self.edit_quiz_requested.emit(self.quiz))

        # Must add parent=self, otherwise it will appear as a top-level window temporarily
        # Using ClickableLabel for a little surprise ;)
        self.default_lbl = ClickableLabel("Default Quiz", self)
        self.default_lbl.setToolTip("This quiz cannot be edited or deleted")
        self.default_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.default_lbl.setFixedSize(100, 30)

        # Hides label until it is confirmed this is a premade quiz, and makes
        # cursor not change when hovering over as it is not meant to be clicked.
        self.default_lbl.hide()
        self.default_lbl.unsetCursor()

        # Trigger the counter when clicked
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

        # If default quiz, hide delete button and make Edit button the Preview
        # button instead, and show the default quiz label.
        if self.quiz.is_premade:
            self.delete_btn.hide()

            # Change edit button to a preview button
            view_icon = get_icons_dir() / "preview.png"
            self.edit_btn.setIcon(QIcon(str(view_icon)))
            self.edit_btn.setToolTip("View as read-only")

            self.edit_btn.show()
            self.default_lbl.show()

        # Layouts setup
        vbox = QVBoxLayout()
        vbox.addWidget(self.title_lbl)
        vbox.addWidget(self.questions_lbl)
        vbox.addWidget(self.updated_lbl)

        # There will always be a space of 5px between either Edit and Delete
        # or Preview and default label.
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
        """
        Internal method. This method is intended to be called when the 'default quiz' label is clicked.
        After a certain amount of clicks, various popups show up...

        This method only runs if the quiz that this card is representing is a default quiz.

        Returns:
            None.
        """
        if not self.quiz.is_premade:
            return

        self._default_clicked_counter += 1

        # Labels have feelings too... <3
        if self._default_clicked_counter == 10:
            QMessageBox.information(
                self,
                " ",
                "Just a heads up, I'm not a button, even though I might look like one. Don't worry, it's a common mistake, for some reason.",
            )
        elif self._default_clicked_counter == 20:
            QMessageBox.warning(self, " ", "So we're just gonna keep clicking me, huh?")
        elif self._default_clicked_counter == 30:
            QMessageBox.warning(
                self, " ", "This isn't even funny anymore, just stop please."
            )
        elif self._default_clicked_counter == 40:
            QMessageBox.warning(self, " ", "This is your final warning...")
        elif self._default_clicked_counter == 50:
            QMessageBox.critical(
                self, " ", "Can't you listen? I'm a label, not a button! I'm done here."
            )

            # They walked off the job. I mean, who can blame them?
            self.default_lbl.hide()
