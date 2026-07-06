from PyQt6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal

from ui.screens.base_screen import BaseScreen
from ui.components.card import Card, StatCard
from ui.components.answer_button_grid import AnswerButtonGrid
from models.payloads import ClientResultsPayload

from ui.components.button import create_return_button
from ui.components.dialogs import confirm_warning
from utils.color import darken_color


class ClientMultiResultScreen(BaseScreen):
    title_text = "Quiz Master – Results"

    left_server = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setup_ui()

    def setup_ui(self) -> None:
        ## WIDGETS SETUP ##
        # Header
        self.result_lbl = QLabel()
        self.result_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_lbl.setStyleSheet("font-size: 42px;" "font-weight: 600;")

        self.your_answer = QLabel()
        self.your_answer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.your_answer.setStyleSheet("font-size: 16px;" "color: #A0A0A0;")

        # Left side
        self.left_card = Card()

        self.question_lbl = QLabel()
        self.question_lbl.setWordWrap(True)
        self.question_lbl.setStyleSheet("font-size: 24px;" "font-weight: 600;")

        self.correct_answer = QLabel()
        self.correct_answer.setStyleSheet("font-size: 16px;" "color: #A0A0A0;")

        self.answer_button_grid = AnswerButtonGrid("result")
        self.answer_button_grid.setMaximumHeight(500)

        # Right side
        right_card = Card()

        stats_heading = QLabel("Your Progress")
        stats_heading.setWordWrap(True)
        stats_heading.setStyleSheet("font-size: 24px;" "font-weight: 600;")

        self.nickname = QLabel()
        self.nickname.setWordWrap(True)
        self.nickname.setStyleSheet("font-size: 14px;" "color: #6E6E6E;")

        self.time_stat = StatCard("Time", "")
        self.points_stat = StatCard("Total Points", "")
        self.rank_stat = StatCard("Leaderboard Rank", "")

        leave_btn = create_return_button("Leave")
        leave_btn.clicked.connect(self.leave_game)

        ## LAYOUTS SETUP ##
        vbox_header = QVBoxLayout()
        vbox_header.addWidget(self.result_lbl)
        vbox_header.addSpacing(2)
        vbox_header.addWidget(self.your_answer)
        vbox_header.addSpacing(20)

        vbox_left = QVBoxLayout(self.left_card)
        vbox_left.setContentsMargins(20, 20, 20, 20)
        vbox_left.addWidget(self.question_lbl)
        vbox_left.addSpacing(5)
        vbox_left.addWidget(self.correct_answer)
        vbox_left.addSpacing(10)
        vbox_left.addWidget(self.answer_button_grid, 4)
        vbox_left.addStretch(1)

        vbox_right = QVBoxLayout(right_card)
        vbox_right.setContentsMargins(20, 20, 20, 20)
        vbox_right.addWidget(stats_heading)
        vbox_right.addSpacing(2)
        vbox_right.addWidget(self.nickname)
        vbox_right.addSpacing(15)
        vbox_right.addWidget(self.time_stat)
        vbox_right.addSpacing(10)
        vbox_right.addWidget(self.points_stat)
        vbox_right.addSpacing(10)
        vbox_right.addWidget(self.rank_stat)
        vbox_right.addStretch(1)
        vbox_right.addWidget(leave_btn, alignment=Qt.AlignmentFlag.AlignRight)

        hbox = QHBoxLayout()
        hbox.addWidget(self.left_card, 5)
        hbox.addSpacing(20)
        hbox.addWidget(right_card, 2)

        vbox = QVBoxLayout()
        vbox.setContentsMargins(40, 20, 40, 20)
        vbox.addLayout(vbox_header)
        vbox.addLayout(hbox, 1)

        self.setLayout(vbox)

    def leave_game(self) -> None:
        """Displays a warning modal box before leaving the game."""
        confirm = confirm_warning(
            self,
            "Confirm Leaving",
            "Are you sure you want to disconnect and return to menu? You won't be able to reconnect and your progress in the game will be lost.",
        )

        if confirm:
            self.left_server.emit()

    def on_enter(self, payload: ClientResultsPayload):
        # Correct: #3DDC84
        # Incorrect: #FF5C5C
        theme_color = "#3DDC84" if payload.is_correct else "#FF5C5C"

        # If user didn't answer, show specialized text
        if payload.selected_answer is not None:
            selected_answer = payload.answer_options[payload.selected_answer]
        else:
            selected_answer = "No answer"

        correct_answer = payload.answer_options[payload.correct_answer]

        self.result_lbl.setText(
            f"{'Correct!' if payload.is_correct else 'Incorrect!'} +{payload.gained_points}"
        )
        self.result_lbl.setStyleSheet(
            f"font-size: 42px; font-weight: 600; color: {theme_color};"
        )

        self.your_answer.setText(f"Your answer: {selected_answer}")

        self.left_card.set_accent(darken_color(theme_color, factor=0.6))
        self.question_lbl.setText(payload.question_text)
        self.correct_answer.setText(f"Correct answer: {correct_answer}")

        # If no selected answer due to running out of time, mimic a correct answer by only showing tick
        selected_answer_index = (
            payload.selected_answer
            if payload.selected_answer is not None
            else payload.correct_answer
        )
        self.answer_button_grid.set_answers(payload.answer_options)
        self.answer_button_grid.set_result(
            payload.correct_answer, selected_answer_index
        )

        self.nickname.setText(f"Nickname: {payload.nickname}")

        # If user didn't answer in time, don't show the card
        if payload.time_taken is not None:
            self.time_stat.set_value(f"{payload.time_taken:.2f}s")
        else:
            self.time_stat.setHidden(True)

        self.points_stat.set_value(str(payload.total_points))

        # If the question is the final question, don't show the rank
        if payload.rank is not None:
            self.rank_stat.set_value(f"#{payload.rank}")
        else:
            self.rank_stat.setHidden(True)

    def on_leave(self) -> None:
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
        self.rank_stat.setHidden(False)
