from PyQt6.QtWidgets import (
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QAbstractItemView,
    QHeaderView,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QBrush, QColor

from core.screen_ids import Screens
from ui.screens.base_screen import BaseScreen
from ui.components.answer_bar_chart import AnswerBarChart
from ui.components.answer_button_grid import AnswerButtonGrid
from ui.components.card import Card
from ui.components.button import LeaveButton
from ui.utils.color import darken_color


class ServerMultiResultScreen(BaseScreen):
    title_text = "Quiz Master – Results"

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setup_ui()

    def setup_ui(self):
        header = QLabel("Question Results")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Correct: #3DDC84
        # Incorrect: #FF5C5C
        header.setStyleSheet("font-size: 42px;" "font-weight: 600;" "color: #3DDC84;")

        self.accuracy = QLabel("Question 1 / 2 • 60% answered correctly")
        self.accuracy.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.accuracy.setStyleSheet("font-size: 16px;" "color: #A0A0A0;")

        header_layout = QVBoxLayout()
        header_layout.addWidget(header)
        header_layout.addSpacing(2)
        header_layout.addWidget(self.accuracy)
        header_layout.addSpacing(20)

        self.question_lbl = QLabel("What is the largest planet in the solar system?")
        self.question_lbl.setWordWrap(True)
        self.question_lbl.setStyleSheet("font-size: 24px;" "font-weight: 600;")

        self.correct_answer = QLabel("Correct answer: Jupiter")
        self.correct_answer.setStyleSheet("font-size: 16px;" "color: #A0A0A0;")

        self.answer_bar_chart = AnswerBarChart()
        self.answer_bar_chart.set_values([3, 1, 2, 1])

        self.answer_button_grid = AnswerButtonGrid("result")
        self.answer_button_grid.set_answers(["Jupiter", "Saturn", "Uranus", "Neptune"])
        self.answer_button_grid.set_result(0, 0)
        self.answer_button_grid.setMaximumHeight(500)

        left_card = Card(
            accent=darken_color("#3DDC84", 0.6),
            blur_radius=35,
        )
        left_layout = QVBoxLayout(left_card)
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
            ["Place", "Name", "Gained", "Total"]
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

        # TODO round table corners
        self.leaderboard_table.setStyleSheet("""
            QTableWidget::item {
                padding: 6px;
            }
        """)

        # TODO only for prototype
        data = [
            ("#1", "Peptalker101", "+982", "982"),
            ("#2", "ItsJakePlayz21", "+980", "980"),
            ("#3", "Viradex", "+978", "978"),
            ("#4", "TrexGamerGirl", "+972", "972"),
            ("#5", "Scyrist", "+966", "966"),
        ]

        for index, (place, name, gained, total) in enumerate(data):
            row = self.leaderboard_table.rowCount()
            self.leaderboard_table.insertRow(row)

            place_item = QTableWidgetItem(place)
            name_item = QTableWidgetItem(name)
            gained_item = QTableWidgetItem(gained)
            total_item = QTableWidgetItem(total)

            if index == 0:
                color = QBrush(QColor("#F5C542"))
            elif index == 1:
                color = QBrush(QColor("#C9CED6"))
            elif index == 2:
                color = QBrush(QColor("#CD7F32"))
            else:
                color = QBrush(QColor("#D6D1C7"))

            place_item.setForeground(color)
            name_item.setForeground(color)
            gained_item.setForeground(color)
            total_item.setForeground(color)

            place_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            gained_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.leaderboard_table.setItem(row, 0, place_item)
            self.leaderboard_table.setItem(row, 1, name_item)
            self.leaderboard_table.setItem(row, 2, gained_item)
            self.leaderboard_table.setItem(row, 3, total_item)

        end_game_btn = LeaveButton("End Game", btn_width=80)
        end_game_btn.confirm_leave.connect(lambda: self.go_to(Screens.COMMON_MENU))

        return_btn = QPushButton("Next Question")
        return_btn.setFixedSize(140, 40)
        return_btn.clicked.connect(lambda: self.go_to(Screens.SERVER_MULTI_QUESTION))
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
        hbox.addWidget(left_card, 5)
        hbox.addSpacing(20)
        hbox.addWidget(right_card, 4)

        vbox = QVBoxLayout()
        vbox.setContentsMargins(40, 20, 40, 20)

        vbox.addLayout(header_layout)
        vbox.addLayout(hbox, 1)

        self.setLayout(vbox)
