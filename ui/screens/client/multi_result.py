"""
multi_result.py

The client multi-question results UI screen. Allows viewing the result of the question that the user
just answered, along with some statistics.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from core.app.enums import AnswerButtonGridMode
from models.payloads import ClientResultsPayload
from ui.components.answer_button_grid import AnswerButtonGrid
from ui.components.button import create_return_button
from ui.components.card import Card, StatCard
from ui.components.dialog import confirm_warning
from ui.screens.base_screen import BaseScreen
from utils.color import darken_color


class ClientMultiResultScreen(BaseScreen):
    """
    Creates the client multi-question results screen, inheriting BaseScreen. This screen is part of the
    'client' category.

    This screen is responsible for allowing users to view their results and statistics. It does not progress
    the quiz itself.

    Attributes:
        title_text: The default text of the screen when entered. A string is used as that is what the
            title changing code requires.

        left_server: A `pyqtSignal` that emits when the user wishes to leave the server. No arguments are
            provided.

    Arguments:
        parent: The parent of this screen, or None. Typically, this is the MainWindow.
    """

    title_text = "Quiz Master – Results"

    left_server = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._setup_ui()

    def _setup_ui(self) -> None:
        """
        Internal method. Sets up the screen UI for the first time. This method should only be called once,
        preferably in the initialization logic.

        Returns:
            None.
        """
        self._setup_widgets()
        self._setup_layouts()

    def _setup_widgets(self) -> None:
        """
        Internal method. Sets up all widgets used by the screen, including styling and slots, if needed. These
        widgets are not added to any global layout in this method, however.

        Returns:
            None.
        """
        # Header title result label, with dynamic styling
        self.result_lbl = QLabel()
        self.result_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_lbl.setStyleSheet("font-size: 42px;" "font-weight: 600;")

        self.leave_btn = create_return_button("Leave")
        self.leave_btn.clicked.connect(self._on_leave_game)

        # Description
        self.your_answer = QLabel()
        self.your_answer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.your_answer.setStyleSheet("font-size: 16px;" "color: #A0A0A0;")

        # Left side
        self.left_card = Card()

        # Set word wrap to ensure question does not extend beyond view and overflow
        self.question_lbl = QLabel()
        self.question_lbl.setWordWrap(True)
        self.question_lbl.setStyleSheet("font-size: 24px;" "font-weight: 600;")

        self.correct_answer = QLabel()
        self.correct_answer.setStyleSheet("font-size: 16px;" "color: #A0A0A0;")

        self.answer_button_grid = AnswerButtonGrid(AnswerButtonGridMode.RESULT)
        self.answer_button_grid.setMaximumHeight(500)

        # Right side
        self.right_card = Card()

        self.stats_heading = QLabel("Your Progress")
        self.stats_heading.setStyleSheet("font-size: 24px;" "font-weight: 600;")

        self.nickname = QLabel()
        self.nickname.setStyleSheet("font-size: 14px;" "color: #6E6E6E;")

        self.time_stat = StatCard("Time", "")
        self.points_stat = StatCard("Total Points", "")
        self.rank_stat = StatCard("Rank", "")

    def _setup_layouts(self) -> None:
        """
        Internal method. Sets up all the layouts on this screen, adding widgets and controlling alignment, spacing,
        and stretching. The main layout is also applied as this screen's primary layout via `setLayout()`.

        Returns:
            None.
        """
        # Create header using grid layout to ensure buttons and heading are aligned evenly
        nav_grid = QGridLayout()
        nav_grid.addWidget(self.leave_btn, 0, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        nav_grid.addWidget(
            self.result_lbl, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter
        )
        nav_grid.setColumnStretch(0, 1)
        nav_grid.setColumnStretch(1, 0)
        nav_grid.setColumnStretch(2, 1)

        # Top row header with description
        vbox_header = QVBoxLayout()
        vbox_header.addLayout(nav_grid)
        vbox_header.addSpacing(2)
        vbox_header.addWidget(self.your_answer)
        vbox_header.addSpacing(20)

        vbox_left = QVBoxLayout(self.left_card)
        vbox_left.setContentsMargins(20, 20, 20, 20)
        vbox_left.addWidget(self.question_lbl)
        vbox_left.addSpacing(5)
        vbox_left.addWidget(self.correct_answer)
        vbox_left.addSpacing(10)

        # Ensure answer button grid takes up majority of space with a little bit of padding below
        vbox_left.addWidget(self.answer_button_grid, stretch=4)
        vbox_left.addStretch(1)

        vbox_right = QVBoxLayout(self.right_card)
        vbox_right.setContentsMargins(20, 20, 20, 20)
        vbox_right.addWidget(self.stats_heading)
        vbox_right.addSpacing(2)
        vbox_right.addWidget(self.nickname)
        vbox_right.addSpacing(15)
        vbox_right.addWidget(self.time_stat)
        vbox_right.addSpacing(10)
        vbox_right.addWidget(self.points_stat)
        vbox_right.addSpacing(10)
        vbox_right.addWidget(self.rank_stat)
        vbox_right.addStretch(1)

        # Ensure left card takes more width with 5:2 ratio
        hbox = QHBoxLayout()
        hbox.addWidget(self.left_card, stretch=5)
        hbox.addSpacing(20)
        hbox.addWidget(self.right_card, stretch=2)

        vbox = QVBoxLayout()
        vbox.setContentsMargins(20, 20, 20, 20)
        vbox.addLayout(vbox_header)
        vbox.addLayout(hbox, stretch=1)

        self.setLayout(vbox)

    def _on_leave_game(self) -> None:
        """
        Internal method. Intended to be run when the user clicks the Leave button. Displays a warning confirmation
        dialog to ensure the user wishes to leave the server, then disconnects from the server.

        Returns:
            None.
        """
        confirm = confirm_warning(
            self,
            "Confirm Leaving",
            "Are you sure you want to disconnect and return to menu? You won't be able to reconnect and your progress in the game will be lost.",
        )

        if confirm:
            self.left_server.emit()

    def on_enter(self, payload: ClientResultsPayload) -> None:
        # Correct: #3DDC84
        # Incorrect: #FF5C5C
        # Theme color for the card and title
        theme_color = "#3DDC84" if payload.is_correct else "#FF5C5C"

        # If user didn't answer, show specialized text
        selected_answer = (
            payload.answer_options[payload.selected_answer]
            if payload.selected_answer is not None
            else "No answer"
        )

        correct_answer = payload.answer_options[payload.correct_answer]

        # Set result label text and stylings
        self.result_lbl.setText(
            f"{'Correct!' if payload.is_correct else 'Incorrect!'} +{payload.gained_points}"
        )
        self.result_lbl.setStyleSheet(
            f"font-size: 42px; font-weight: 600; color: {theme_color};"
        )

        self.your_answer.setText(f"Your answer: {selected_answer}")

        # Make accent color darker for border to make it blend more into the background
        self.left_card.set_accent(darken_color(theme_color, factor=0.4))

        # Set question and correct answer
        self.question_lbl.setText(payload.question_text)
        self.correct_answer.setText(f"Correct answer: {correct_answer}")

        # Configure answer button grid with answer options, and the result from the question
        self.answer_button_grid.set_answers(payload.answer_options)
        self.answer_button_grid.set_result(
            payload.correct_answer, payload.selected_answer
        )

        self.nickname.setText(f"Nickname: {payload.nickname}")

        # If user didn't answer in time, don't show the card
        if payload.time_taken is None:
            self.time_stat.hide()
        else:
            self.time_stat.set_value(f"{payload.time_taken:.2f}s")

        self.points_stat.set_value(str(payload.total_points))

        # If the question is the final question, don't show the rank
        if payload.rank is None:
            self.rank_stat.hide()
        else:
            self.rank_stat.set_value(f"#{payload.rank}")

    def on_leave(self) -> None:
        # Reset and re-show all widgets to prevent stale data from showing if the
        # UI doesn't update fast enough on next showing.
        self.result_lbl.setText("")
        self.result_lbl.setStyleSheet(
            "font-size: 42px;" "font-weight: 600;" "color: white;"
        )

        self.your_answer.setText("")

        self.left_card.reset_accent()
        self.question_lbl.setText("")
        self.correct_answer.setText("")

        self.answer_button_grid.reset_buttons()
        self.nickname.setText("")

        self.time_stat.set_value("")
        self.time_stat.show()

        self.points_stat.set_value("")

        self.rank_stat.set_value("")
        self.rank_stat.show()
