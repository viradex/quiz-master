"""
multi_question.py

The server multi-question UI screen. Allows displaying a question to the host, and allows the host
to skip the question.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from core.app.enums import AnswerButtonGridMode
from models.payloads import QuestionPayload
from ui.components.answer_button_grid import AnswerButtonGrid
from ui.components.button import create_return_button
from ui.components.dialog import confirm_warning
from ui.components.question_timer import QuestionTimer
from ui.screens.base_screen import BaseScreen


class ServerMultiQuestionScreen(BaseScreen):
    """
    Creates the server multi-question screen, inheriting BaseScreen. This screen is part of the 'server' category.

    This screen is responsible for allowing the host to view the question the clients are answering, view the
    total number of submissions, and skip the question prematurely, if required.

    Attributes:
        title_text: The default text of the screen when entered. A string is used as that is what the
            title changing code requires.

        question_skipped: A `pyqtSignal` that emits when the user wishes to skip the current question. No
            arguments are provided.

    Arguments:
        parent: The parent of this screen, or None. Typically, this is the MainWindow.
    """

    title_text = "Quiz Master – Question"

    question_skipped = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # Total player submissions, used purely for UI display
        self.submissions: int = 0

        self._setup_ui()

    def _setup_ui(self) -> None:
        ## FONTS SETUP ##
        question_num_font = QFont()
        question_num_font.setPointSize(12)

        question_font = QFont()
        question_font.setPointSize(26)
        question_font.setBold(True)

        ## WIDGETS SETUP ##
        # Left side (main section)
        self.question_num = QLabel()
        self.question_num.setFont(question_num_font)

        # Setting border-radius QSS property to half of the height/width of
        # widget makes the label a circle.
        self.submitted = QLabel("0")
        self.submitted.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.submitted.setFixedSize(40, 40)
        self.submitted.setStyleSheet("""
            QLabel {
                background-color: #2a2a2a;
                border-radius: 20px;
                color: white;
                font-size: 20px;
                font-weight: 600;
            }
        """)

        # Set word wrap to ensure question does not extend beyond view and overflow
        self.question_lbl = QLabel()
        self.question_lbl.setWordWrap(True)
        self.question_lbl.setFont(question_font)

        self.answer_button_grid = AnswerButtonGrid(AnswerButtonGridMode.SERVER)

        # Right side column
        self.skip_btn = create_return_button("Skip", btn_width=50)
        self.skip_btn.clicked.connect(self._on_skip_question)

        self.question_timer = QuestionTimer()

        ## LAYOUTS SETUP ##
        question_info_hbox = QHBoxLayout()
        question_info_hbox.addWidget(self.question_num)
        question_info_hbox.addWidget(
            self.submitted, alignment=Qt.AlignmentFlag.AlignRight
        )

        vbox_left = QVBoxLayout()
        vbox_left.addSpacing(20)
        vbox_left.addLayout(question_info_hbox)
        vbox_left.addSpacing(2)
        vbox_left.addWidget(self.question_lbl)
        vbox_left.addSpacing(20)

        # Ensure button grid takes up majority of screen
        vbox_left.addWidget(self.answer_button_grid, stretch=1)
        vbox_left.addSpacing(10)

        # Makes question timer take up rest of column
        vbox_right = QVBoxLayout()
        vbox_right.addSpacing(5)
        vbox_right.addWidget(self.skip_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        vbox_right.addWidget(
            self.question_timer, stretch=1, alignment=Qt.AlignmentFlag.AlignRight
        )

        # Left side takes up the rest of the space that right side doesn't use
        hbox = QHBoxLayout()
        hbox.setContentsMargins(50, 20, 20, 20)
        hbox.addLayout(vbox_left, stretch=1)
        hbox.addSpacing(40)
        hbox.addLayout(vbox_right)

        self.setLayout(hbox)

    def add_submission(self) -> None:
        """
        Add a single submission to the counter and update the UI to reflect the change.

        Returns:
            None.
        """
        self.submissions += 1
        self.submitted.setText(str(self.submissions))

    def reset_submissions(self) -> None:
        """
        Reset the submissions counter to 0 and update the UI to reflect the change.

        Returns:
            None.
        """
        self.submissions = 0
        self.submitted.setText("0")

    def _on_skip_question(self) -> None:
        """
        Internal method. Intended to be run when the user clicks the Skip button. Shows a warning confirmation
        dialog to ensure the user wishes to skip the current question, then skips it if they consent.

        Returns:
            None.
        """
        confirm = confirm_warning(
            self,
            "Confirm Skipping",
            "Are you sure you want to skip this question? Players who haven't answered will lose the chance to respond.",
        )

        if confirm:
            self.question_skipped.emit()

    def on_enter(self, payload: QuestionPayload) -> None:
        question_progress = f"{payload.question_num} / {payload.total_questions}"
        self.set_title(f"Quiz Master – Question {question_progress}")

        # Set all UI elements to reflect payload data
        self.question_num.setText(f"Question {question_progress}")
        self.question_lbl.setText(payload.question_text)

        self.answer_button_grid.set_answers(payload.answer_options)

        # Set time limit in milliseconds from seconds, and start timer immediately
        self.question_timer.set_duration(payload.time_limit * 1000)
        self.question_timer.start()

    def on_leave(self) -> None:
        # Reset all dynamic UI elements
        self.set_title("Quiz Master – Question")

        self.question_num.setText("")
        self.question_lbl.setText("")

        self.reset_submissions()

        # Stop timer to prevent CPU usage
        self.question_timer.stop()
