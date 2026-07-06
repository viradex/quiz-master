from PyQt6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal

from ui.screens.base_screen import BaseScreen
from ui.components.question_timer import QuestionTimer
from ui.components.answer_button_grid import AnswerButtonGrid
from models.payloads import QuestionPayload

from ui.components.button import create_return_button
from ui.components.dialogs import confirm_warning


class ServerMultiQuestionScreen(BaseScreen):
    title_text = "Quiz Master – Question"

    question_skipped = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.submissions = 0

        self.setup_ui()

    def setup_ui(self) -> None:
        ## FONTS SETUP ##
        # Left side
        question_num_font = QFont()
        question_num_font.setPointSize(12)

        question_font = QFont()
        question_font.setPointSize(26)
        question_font.setBold(True)

        ## WIDGETS SETUP ##
        # Left side
        self.question_num = QLabel()
        self.question_num.setFont(question_num_font)

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

        self.question_lbl = QLabel()
        self.question_lbl.setWordWrap(True)
        self.question_lbl.setFont(question_font)

        self.answer_button_grid = AnswerButtonGrid("server")

        # Right side
        skip_btn = create_return_button("Skip", btn_width=50)
        skip_btn.clicked.connect(self.skip_question)

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
        vbox_left.addWidget(self.answer_button_grid, 1)
        vbox_left.addSpacing(10)

        vbox_right = QVBoxLayout()
        vbox_right.addSpacing(5)
        vbox_right.addWidget(skip_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        vbox_right.addWidget(
            self.question_timer, 1, alignment=Qt.AlignmentFlag.AlignRight
        )

        hbox = QHBoxLayout()
        hbox.setContentsMargins(50, 20, 20, 20)
        hbox.addLayout(vbox_left, 1)
        hbox.addSpacing(40)
        hbox.addLayout(vbox_right)

        self.setLayout(hbox)

    def update_submission_count(self, amount: int) -> None:
        """Update the amount of submissions by adding to the total."""
        self.submissions += amount
        self.submitted.setText(str(self.submissions))

    def skip_question(self) -> None:
        """Skips the question early."""
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

        self.question_num.setText(f"Question {question_progress}")
        self.question_lbl.setText(payload.question_text)

        self.answer_button_grid.set_answers(payload.answer_options)

        # Set time limit in milliseconds from seconds
        self.question_timer.set_duration(payload.time_limit * 1000)
        self.question_timer.start()

    def on_leave(self) -> None:
        self.set_title("Quiz Master – Question")

        self.question_num.setText("")
        self.question_lbl.setText("")

        self.submissions = 0
        self.submitted.setText("0")

        self.question_timer.stop()
