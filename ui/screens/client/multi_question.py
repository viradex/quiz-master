from PyQt6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal

from ui.screens.base_screen import BaseScreen
from ui.components.question_timer import QuestionTimer
from ui.components.answer_button_grid import AnswerButtonGrid
from models.payloads import QuestionPayload

from ui.components.button import create_return_button
from ui.components.dialogs import confirm_warning


class ClientMultiQuestionScreen(BaseScreen):
    title_text = "Quiz Master – Question"

    answer_submitted = pyqtSignal(int)
    left_server = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setup_ui()

    def setup_ui(self) -> None:
        ## FONTS SETUP ##
        question_num_font = QFont()
        question_num_font.setPointSize(12)

        question_font = QFont()
        question_font.setPointSize(26)
        question_font.setBold(True)

        ## WIDGETS SETUP ##
        # Left side
        self.question_num = QLabel()
        self.question_num.setFont(question_num_font)

        self.question_lbl = QLabel()
        self.question_lbl.setWordWrap(True)
        self.question_lbl.setFont(question_font)

        self.answer_button_grid = AnswerButtonGrid("live")
        self.answer_button_grid.answer_select.connect(
            lambda index: self.on_answer_select(index)
        )

        # Right side
        leave_btn = create_return_button("Leave")
        leave_btn.clicked.connect(self.leave_game)

        self.question_timer = QuestionTimer()

        ## LAYOUTS SETUP ##
        vbox_left = QVBoxLayout()
        vbox_left.addSpacing(20)
        vbox_left.addWidget(self.question_num)
        vbox_left.addSpacing(10)
        vbox_left.addWidget(self.question_lbl)
        vbox_left.addSpacing(20)
        vbox_left.addWidget(self.answer_button_grid, 1)
        vbox_left.addSpacing(20)

        vbox_right = QVBoxLayout()
        vbox_right.addWidget(leave_btn, 0, alignment=Qt.AlignmentFlag.AlignRight)
        vbox_right.addWidget(
            self.question_timer, 1, alignment=Qt.AlignmentFlag.AlignRight
        )

        hbox = QHBoxLayout()
        hbox.setContentsMargins(50, 20, 20, 20)
        hbox.addLayout(vbox_left, 1)
        hbox.addSpacing(40)
        hbox.addLayout(vbox_right)

        self.setLayout(hbox)

    def on_answer_select(self, index: int) -> None:
        """Called when the user selects an answer in the answer button grid."""
        self.answer_submitted.emit(index)
        self.question_timer.lock()

    def leave_game(self) -> None:
        """Displays a warning modal box before leaving the game."""
        confirm = confirm_warning(
            self,
            "Confirm Leaving",
            "Are you sure you want to disconnect and return to menu? You won't be able to reconnect and your progress in the game will be lost.",
        )

        if confirm:
            self.left_server.emit()

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

        self.question_timer.stop()
        self.answer_button_grid.reset_buttons()
