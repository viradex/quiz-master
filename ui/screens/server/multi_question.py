from PyQt6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from core.screen_ids import Screens
from ui.screens.base_screen import BaseScreen
from ui.components.question_timer import QuestionTimer
from ui.components.answer_button_grid import AnswerButtonGrid
from ui.components.button import LeaveButton


class ServerMultiQuestionScreen(BaseScreen):
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

        self.answer_button_grid = AnswerButtonGrid(
            ["Jupiter", "Saturn", "Uranus", "Neptune"], "server"
        )

        skip_btn = LeaveButton(
            "Skip Question", btn_width=120, do_confirm=False, margin_left=10
        )
        skip_btn.confirm_leave.connect(lambda: self.go_to(Screens.SERVER_MULTI_RESULT))

        vbox_left = QVBoxLayout()
        vbox_left.addSpacing(20)
        vbox_left.addWidget(self.question_num)
        vbox_left.addSpacing(10)
        vbox_left.addWidget(self.question_lbl)
        vbox_left.addSpacing(20)
        vbox_left.addWidget(self.answer_button_grid, 1)
        vbox_left.addSpacing(5)
        vbox_left.addWidget(skip_btn)

        self.submitted = QLabel("3")
        self.submitted.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.submitted.setFixedSize(40, 40)
        self.submitted.setStyleSheet("""
            QLabel {
                background-color: #2a2a2a;
                border-radius: 20px;
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
        """)

        self.question_timer = QuestionTimer(total_ms=20000, parent=self)
        # TODO use this for calling func when timer ends
        # self.question_timer.timeup.connect()

        right_vbox = QVBoxLayout()
        right_vbox.addSpacing(5)
        right_vbox.addWidget(self.submitted, alignment=Qt.AlignmentFlag.AlignCenter)
        right_vbox.addWidget(
            self.question_timer, 1, alignment=Qt.AlignmentFlag.AlignRight
        )

        hbox = QHBoxLayout()
        hbox.setContentsMargins(50, 20, 20, 20)
        hbox.addLayout(vbox_left, 1)
        hbox.addSpacing(40)
        hbox.addLayout(right_vbox)

        self.setLayout(hbox)

    def on_enter(self):
        self.question_timer.on_enter()

    def on_leave(self):
        self.question_timer.on_leave()
