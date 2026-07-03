from PyQt6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal

from core.app.screen_ids import Screens
from ui.screens.base_screen import BaseScreen
from ui.components.question_timer import QuestionTimer
from ui.components.answer_button_grid import AnswerButtonGrid
from ui.components.button import LeaveButton


class ClientMultiQuestionScreen(BaseScreen):
    title_text = "Quiz Master – Question 1 / 2"

    answer_submit = pyqtSignal(int)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setup_ui()

    def setup_ui(self) -> None:
        question_num_font = QFont()
        question_num_font.setPointSize(12)

        self.question_num = QLabel()
        self.question_num.setFont(question_num_font)

        question_font = QFont()
        question_font.setPointSize(26)
        question_font.setBold(True)

        self.question_lbl = QLabel()
        self.question_lbl.setWordWrap(True)
        self.question_lbl.setFont(question_font)

        self.answer_button_grid = AnswerButtonGrid("live")
        self.answer_button_grid.answer_select.connect(
            lambda index: self.on_answer_select(index)
        )

        vbox_left = QVBoxLayout()
        vbox_left.addSpacing(20)
        vbox_left.addWidget(self.question_num)
        vbox_left.addSpacing(10)
        vbox_left.addWidget(self.question_lbl)
        vbox_left.addSpacing(20)
        vbox_left.addWidget(self.answer_button_grid, 1)
        vbox_left.addSpacing(20)

        leave_btn = LeaveButton("Leave")
        leave_btn.confirm_leave.connect(lambda: self.go_to(Screens.COMMON_MENU))

        self.question_timer = QuestionTimer()

        right_vbox = QVBoxLayout()
        right_vbox.addWidget(leave_btn, 0, alignment=Qt.AlignmentFlag.AlignRight)
        right_vbox.addWidget(
            self.question_timer, 1, alignment=Qt.AlignmentFlag.AlignRight
        )

        hbox = QHBoxLayout()
        hbox.setContentsMargins(50, 20, 20, 20)
        hbox.addLayout(vbox_left, 1)
        hbox.addSpacing(40)
        hbox.addLayout(right_vbox)

        self.setLayout(hbox)

    def on_answer_select(self, index: int) -> None:
        self.answer_submit.emit(index)
        self.question_timer.lock()

    def on_enter(self, payload: dict | None = None) -> None:
        self.question_num.setText(
            f"Question {payload['question_num']} / {payload['total_questions']}"
        )
        self.question_lbl.setText(payload["question_text"])

        self.answer_button_grid.set_answers(payload["answer_options"])
        self.question_timer.set_duration(payload["time_limit"] * 1000)

        self.question_timer.start()

    def on_leave(self) -> None:
        self.question_num.setText("")
        self.question_lbl.setText("")

        self.question_timer.stop()
        self.answer_button_grid.reset_buttons()
