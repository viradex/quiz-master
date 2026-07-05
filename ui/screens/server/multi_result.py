from PyQt6.QtWidgets import (
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QHBoxLayout,
    QAbstractItemView,
    QHeaderView,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from core.app.screen_ids import Screens
from ui.screens.base_screen import BaseScreen
from ui.components.answer_bar_chart import AnswerBarChart
from ui.components.answer_button_grid import AnswerButtonGrid
from ui.components.card import Card
from ui.components.button import LeaveButton
from utils.color import darken_color


class ServerMultiResultScreen(BaseScreen):
    title_text = "Quiz Master – Results"

    next_question = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setup_ui()

    def setup_ui(self):
        self.heading = QLabel("Question Results")
        self.heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.heading.setStyleSheet("font-size: 36px;" "font-weight: 600;")

        self.accuracy = QLabel()
        self.accuracy.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.accuracy.setStyleSheet("font-size: 16px;" "color: #A0A0A0;")

        header_layout = QVBoxLayout()
        header_layout.addWidget(self.heading)
        header_layout.addSpacing(2)
        header_layout.addWidget(self.accuracy)
        header_layout.addSpacing(20)

        self.question_lbl = QLabel()
        self.question_lbl.setWordWrap(True)
        self.question_lbl.setStyleSheet("font-size: 24px;" "font-weight: 600;")

        self.correct_answer = QLabel()
        self.correct_answer.setStyleSheet("font-size: 16px;" "color: #A0A0A0;")

        self.answer_bar_chart = AnswerBarChart()

        self.answer_button_grid = AnswerButtonGrid("result")
        self.answer_button_grid.setMaximumHeight(500)

        self.left_card = Card()
        left_layout = QVBoxLayout(self.left_card)
        left_layout.setContentsMargins(20, 20, 20, 20)

        left_layout.addWidget(self.question_lbl)
        left_layout.addSpacing(2)
        left_layout.addWidget(self.correct_answer)
        left_layout.addWidget(self.answer_bar_chart, stretch=1)
        left_layout.addSpacing(15)
        left_layout.addWidget(self.answer_button_grid, stretch=1)

        leaderboard_heading = QLabel("Leaderboard")
        leaderboard_heading.setStyleSheet("font-size: 24px;" "font-weight: 600;")

        table_font = QFont()
        table_font.setPointSize(12)

        table_bold_font = QFont()
        table_bold_font.setPointSize(12)
        table_bold_font.setBold(True)

        self.leaderboard_table = QTableWidget()
        self.leaderboard_table.setFont(table_font)
        self.leaderboard_table.setShowGrid(False)
        self.leaderboard_table.setAlternatingRowColors(True)
        self.leaderboard_table.setColumnCount(4)
        self.leaderboard_table.setHorizontalHeaderLabels(
            ["Rank", "Name", "Gained", "Total"]
        )
        self.leaderboard_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.leaderboard_table.setSelectionMode(
            QAbstractItemView.SelectionMode.NoSelection
        )

        self.leaderboard_table.verticalHeader().setVisible(False)
        self.leaderboard_table.verticalHeader().setDefaultSectionSize(32)

        header = self.leaderboard_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)

        self.leaderboard_table.setColumnWidth(0, 80)
        self.leaderboard_table.setColumnWidth(2, 80)
        self.leaderboard_table.setColumnWidth(3, 80)

        self.leaderboard_table.setStyleSheet("""
            QTableWidget::item {
                padding: 6px;
            }
        """)

        end_game_btn = LeaveButton("End Game", btn_width=80)
        end_game_btn.clicked.connect(lambda: self.go_to(Screens.COMMON_MENU))

        return_btn = QPushButton("Next Question")
        return_btn.setFixedSize(140, 40)
        return_btn.clicked.connect(self.on_next_question)
        return_btn.setStyleSheet("font-size: 14px;")

        btn_footer = QHBoxLayout()
        btn_footer.addWidget(end_game_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        btn_footer.addWidget(return_btn, alignment=Qt.AlignmentFlag.AlignRight)

        right_card = Card()
        right_layout = QVBoxLayout(right_card)
        right_layout.setContentsMargins(20, 20, 20, 20)

        right_layout.addWidget(leaderboard_heading)
        right_layout.addSpacing(15)
        right_layout.addWidget(self.leaderboard_table, stretch=3)
        right_layout.addSpacing(20)
        right_layout.addLayout(btn_footer)
        right_layout.addStretch(1)

        hbox = QHBoxLayout()
        hbox.addWidget(self.left_card, 5)
        hbox.addSpacing(20)
        hbox.addWidget(right_card, 4)

        vbox = QVBoxLayout()
        vbox.setContentsMargins(40, 20, 40, 20)

        vbox.addLayout(header_layout)
        vbox.addLayout(hbox, 1)

        self.setLayout(vbox)

    def show_leaderboard_values(self, players: list[tuple[str, str, str, str]]) -> None:
        for index, (rank, name, gained, total) in enumerate(players):
            row = self.leaderboard_table.rowCount()
            self.leaderboard_table.insertRow(row)

            rank_item = QTableWidgetItem(rank)
            name_item = QTableWidgetItem(name)
            gained_item = QTableWidgetItem(gained)
            total_item = QTableWidgetItem(total)

            if index == 0:
                color = QColor("#F5C542")
            elif index == 1:
                color = QColor("#C9CED6")
            elif index == 2:
                color = QColor("#CD7F32")
            else:
                color = QColor("#D6D1C7")

            rank_item.setForeground(color)
            name_item.setForeground(color)
            gained_item.setForeground(color)
            total_item.setForeground(color)

            rank_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            gained_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.leaderboard_table.setItem(row, 0, rank_item)
            self.leaderboard_table.setItem(row, 1, name_item)
            self.leaderboard_table.setItem(row, 2, gained_item)
            self.leaderboard_table.setItem(row, 3, total_item)

    def clear_leaderboard(self) -> None:
        self.leaderboard_table.setRowCount(0)

    def on_next_question(self) -> None:
        self.next_question.emit()

    def on_enter(self, payload: dict) -> None:
        # Correct: #3DDC84
        # Incorrect: #FF5C5C
        accuracy = round(payload["accuracy"] * 100)
        theme_color = "#3DDC84" if accuracy >= 50 else "#FF5C5C"

        self.heading.setStyleSheet(
            f"font-size: 36px; font-weight: 600; color: {theme_color};"
        )
        self.accuracy.setText(
            f"Question {payload['question_num']} / {payload['total_questions']} • {accuracy}% answered correctly"
        )

        correct_answer = payload["answer_options"][payload["correct_answer"]]

        self.left_card.set_accent(darken_color(theme_color, factor=0.6))
        self.question_lbl.setText(payload["question_text"])
        self.correct_answer.setText(f"Correct answer: {correct_answer}")

        self.answer_bar_chart.set_values(
            payload["answer_frequency"], payload["correct_answer"]
        )

        self.answer_button_grid.set_answers(payload["answer_options"])
        self.answer_button_grid.set_result(
            payload["correct_answer"], payload["correct_answer"]
        )

        leaderboard_players = []
        for player in payload["leaderboard"]:
            leaderboard_players.append(
                (
                    f"#{player['rank']}",
                    player["name"],
                    f"+{player['gained']}",
                    str(player["total"]),
                )
            )

        self.show_leaderboard_values(leaderboard_players)

    def on_leave(self):
        self.heading.setStyleSheet("font-size: 36px;" "font-weight: 600;")
        self.accuracy.setText("")

        self.left_card.reset_accent()
        self.question_lbl.setText("")
        self.correct_answer.setText("")

        self.answer_button_grid.reset_buttons()

        self.clear_leaderboard()
