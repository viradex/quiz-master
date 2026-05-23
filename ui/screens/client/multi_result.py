from PyQt6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt

from core.screen_ids import Screens
from ui.screens.base_screen import BaseScreen
from ui.components.card import Card, make_stat_card
from ui.components.answer_button_grid import AnswerButtonGrid
from ui.components.button import LeaveButton
from ui.utils.color import darken_color


class ClientMultiResultScreen(BaseScreen):
    title_text = "Quiz Master – Results"

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setup_ui()

    def setup_ui(self):
        self.result_lbl = QLabel("Correct! +978")
        self.result_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Correct: #3DDC84
        # Incorrect: #FF5C5C
        self.result_lbl.setStyleSheet(
            "font-size: 42px;" "font-weight: 600;" "color: #3DDC84;"
        )

        self.your_answer = QLabel("Your answer: Jupiter")
        self.your_answer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.your_answer.setStyleSheet("font-size: 16px;" "color: #A0A0A0;")

        header_layout = QVBoxLayout()
        header_layout.addWidget(self.result_lbl)
        header_layout.addSpacing(2)
        header_layout.addWidget(self.your_answer)
        header_layout.addSpacing(20)

        self.question_lbl = QLabel("What is the largest planet in the solar system?")
        self.question_lbl.setWordWrap(True)
        self.question_lbl.setStyleSheet("font-size: 24px;" "font-weight: 600;")

        self.correct_answer = QLabel("Correct answer: Jupiter")
        self.correct_answer.setStyleSheet("font-size: 16px;" "color: #A0A0A0;")

        self.answer_button_grid = AnswerButtonGrid(
            ["Jupiter", "Saturn", "Uranus", "Neptune"], "result"
        )
        self.answer_button_grid.set_result(0, 0)
        self.answer_button_grid.setMaximumHeight(500)

        # Correct: #3DDC84
        # Incorrect: #FF5C5C
        self.left_card = Card(accent=darken_color("#3DDC84", 0.6))
        left_layout = QVBoxLayout(self.left_card)
        left_layout.setContentsMargins(20, 20, 20, 20)

        left_layout.addWidget(self.question_lbl)
        left_layout.addSpacing(5)
        left_layout.addWidget(self.correct_answer)
        left_layout.addSpacing(10)
        left_layout.addWidget(self.answer_button_grid, 4)
        left_layout.addStretch(1)

        stats_heading = QLabel("Your Progress")
        stats_heading.setWordWrap(True)
        stats_heading.setStyleSheet("font-size: 24px;" "font-weight: 600;")

        self.nickname = QLabel("Nickname: Viradex")
        self.nickname.setStyleSheet("font-size: 14px;" "color: #6E6E6E;")

        time_stat = make_stat_card("Time", "12.4s")
        score_stat = make_stat_card("Total Score", "978")
        rank_stat = make_stat_card("Leaderboard Position", "#3")

        leave_btn = LeaveButton("Leave")
        leave_btn.confirm_leave.connect(lambda: self.go_to(Screens.COMMON_MENU))

        right_card = Card()
        right_layout = QVBoxLayout(right_card)
        right_layout.setContentsMargins(20, 20, 20, 20)

        right_layout.addWidget(stats_heading)
        right_layout.addSpacing(2)
        right_layout.addWidget(self.nickname)
        right_layout.addSpacing(15)
        right_layout.addWidget(time_stat)
        right_layout.addSpacing(10)
        right_layout.addWidget(score_stat)
        right_layout.addSpacing(10)
        right_layout.addWidget(rank_stat)
        right_layout.addStretch(1)
        right_layout.addWidget(leave_btn, alignment=Qt.AlignmentFlag.AlignRight)

        hbox = QHBoxLayout()
        hbox.addWidget(self.left_card, 5)
        hbox.addSpacing(20)
        hbox.addWidget(right_card, 2)

        vbox = QVBoxLayout()
        vbox.setContentsMargins(40, 20, 40, 20)

        vbox.addLayout(header_layout)
        vbox.addLayout(hbox, 1)

        self.setLayout(vbox)
