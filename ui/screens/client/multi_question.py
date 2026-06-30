from PyQt6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from core.app.screen_ids import Screens
from ui.screens.base_screen import BaseScreen
from ui.components.question_timer import QuestionTimer
from ui.components.answer_button_grid import AnswerButtonGrid
from ui.components.button import LeaveButton


class ClientMultiQuestionScreen(BaseScreen):
    title_text = "Quiz Master – Question 1 / 2"

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setup_ui()

    def setup_ui(self):
        question_num_font = QFont()
        question_num_font.setPointSize(12)

        self.question_num = QLabel("Question 1 / 2")
        self.question_num.setFont(question_num_font)

        question_font = QFont()
        question_font.setPointSize(26)
        question_font.setBold(True)

        self.question_lbl = QLabel("What is the largest planet in the solar system?")
        self.question_lbl.setWordWrap(True)
        self.question_lbl.setFont(question_font)

        self.answer_button_grid = AnswerButtonGrid("live")
        self.answer_button_grid.set_answers(["Jupiter", "Saturn", "Uranus", "Neptune"])
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

        self.question_timer = QuestionTimer(total_ms=20000, parent=self)
        # TODO use this for calling func when timer ends
        # self.question_timer.timeup.connect()

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

    def on_answer_select(self, index):
        self.question_timer.lock()

    def on_enter(self, payload=None):
        self.question_timer.start()

    def on_leave(self):
        self.question_timer.stop()
        self.answer_button_grid.reset_buttons()
