from PyQt6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt

from core.app.screen_ids import Screens
from ui.screens.base_screen import BaseScreen
from ui.components.card import Card, StatCard
from ui.components.answer_button_grid import AnswerButtonGrid
from ui.components.button import LeaveButton
from utils.color import darken_color


class ClientMultiResultScreen(BaseScreen):
    title_text = "Quiz Master – Results"

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setup_ui()

    def setup_ui(self):
        self.result_lbl = QLabel()
        self.result_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_lbl.setStyleSheet("font-size: 42px;" "font-weight: 600;")

        self.your_answer = QLabel()
        self.your_answer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.your_answer.setStyleSheet("font-size: 16px;" "color: #A0A0A0;")

        header_layout = QVBoxLayout()
        header_layout.addWidget(self.result_lbl)
        header_layout.addSpacing(2)
        header_layout.addWidget(self.your_answer)
        header_layout.addSpacing(20)

        self.question_lbl = QLabel()
        self.question_lbl.setWordWrap(True)
        self.question_lbl.setStyleSheet("font-size: 24px;" "font-weight: 600;")

        self.correct_answer = QLabel()
        self.correct_answer.setStyleSheet("font-size: 16px;" "color: #A0A0A0;")

        self.answer_button_grid = AnswerButtonGrid("result")
        self.answer_button_grid.setMaximumHeight(500)

        self.left_card = Card()
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

        self.nickname = QLabel()
        self.nickname.setWordWrap(True)
        self.nickname.setStyleSheet("font-size: 14px;" "color: #6E6E6E;")

        self.time_stat = StatCard("Time", "")
        self.points_stat = StatCard("Total Points", "")
        self.rank_stat = StatCard("Leaderboard Rank", "")

        leave_btn = LeaveButton("Leave")
        leave_btn.clicked.connect(lambda: self.go_to(Screens.COMMON_MENU))

        right_card = Card()
        right_layout = QVBoxLayout(right_card)
        right_layout.setContentsMargins(20, 20, 20, 20)

        right_layout.addWidget(stats_heading)
        right_layout.addSpacing(2)
        right_layout.addWidget(self.nickname)
        right_layout.addSpacing(15)
        right_layout.addWidget(self.time_stat)
        right_layout.addSpacing(10)
        right_layout.addWidget(self.points_stat)
        right_layout.addSpacing(10)
        right_layout.addWidget(self.rank_stat)
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

    def on_enter(self, payload: dict):
        # Correct: #3DDC84
        # Incorrect: #FF5C5C
        theme_color = "#3DDC84" if payload["is_correct"] else "#FF5C5C"

        if payload["selected_answer"] is not None:
            selected_answer = payload["answer_options"][payload["selected_answer"]]
        else:
            selected_answer = "No answer"

        correct_answer = payload["answer_options"][payload["correct_answer"]]

        self.result_lbl.setText(
            f"{'Correct!' if payload['is_correct'] else 'Incorrect!'} +{payload['gained_points']}"
        )
        self.result_lbl.setStyleSheet(
            f"font-size: 42px; font-weight: 600; color: {theme_color};"
        )

        self.your_answer.setText(f"Your answer: {selected_answer}")

        self.left_card.set_accent(darken_color(theme_color, factor=0.6))
        self.question_lbl.setText(payload["question_text"])
        self.correct_answer.setText(f"Correct answer: {correct_answer}")

        # If no selected answer due to running out of time, mimic a correct answer by only showing tick
        selected_answer_index = (
            payload["selected_answer"]
            if payload["selected_answer"] is not None
            else payload["correct_answer"]
        )
        self.answer_button_grid.set_answers(payload["answer_options"])
        self.answer_button_grid.set_result(
            payload["correct_answer"], selected_answer_index
        )

        self.nickname.setText(f"Nickname: {payload['nickname']}")

        if payload["time_taken"] is not None:
            self.time_stat.set_value(f"{payload['time_taken']:.2f}s")
        else:
            self.time_stat.setHidden(True)

        self.points_stat.set_value(str(payload["total_points"]))
        self.rank_stat.set_value(f"#{payload['rank']}")

    def on_leave(self):
        self.result_lbl.setText("")
        self.result_lbl.setStyleSheet("font-size: 42px;" "font-weight: 600;")

        self.your_answer.setText("")

        self.left_card.reset_accent()
        self.question_lbl.setText("")
        self.correct_answer.setText("")

        self.answer_button_grid.reset_buttons()
        self.nickname.setText("")

        self.time_stat.set_value("")
        self.time_stat.setHidden(False)

        self.points_stat.set_value("")
        self.rank_stat.set_value("")
