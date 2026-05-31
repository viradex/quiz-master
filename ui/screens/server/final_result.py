from pathlib import Path
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
from ui.components.card import Card, make_stat_card
from ui.utils.color import darken_color


class ServerFinalResultScreen(BaseScreen):
    title_text = "Quiz Master – Final Results"

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setup_ui()

    def setup_ui(self):
        heading = QLabel("Final Results")
        heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        heading.setStyleSheet("font-size: 36px;" "font-weight: 600;")

        self.winner = QLabel("Peptalker101 takes 1st place!")
        self.winner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.winner.setStyleSheet("font-size: 20px;" "color: #F5C542;")

        header_layout = QVBoxLayout()
        header_layout.addWidget(heading)
        header_layout.addSpacing(2)
        header_layout.addWidget(self.winner)
        header_layout.addSpacing(20)

        leaderboard_heading = QLabel("Leaderboard")
        leaderboard_heading.setStyleSheet("font-size: 24px;" "font-weight: 600;")

        leaderboard_desc = QLabel("Final standings")
        leaderboard_desc.setStyleSheet("font-size: 14px;" "color: #6E6E6E;")

        table_font = QFont()
        table_font.setPointSize(12)

        table_bold_font = QFont()
        table_bold_font.setPointSize(12)
        table_bold_font.setBold(True)

        self.leaderboard_table = QTableWidget()
        self.leaderboard_table.setFont(table_font)
        self.leaderboard_table.setShowGrid(False)
        self.leaderboard_table.setAlternatingRowColors(True)
        self.leaderboard_table.setColumnCount(3)
        self.leaderboard_table.setHorizontalHeaderLabels(["Place", "Name", "Total"])
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

        self.leaderboard_table.setColumnWidth(0, 80)
        self.leaderboard_table.setColumnWidth(2, 80)

        self.leaderboard_table.setStyleSheet("""
            QTableWidget::item {
                padding: 6px;
            }
        """)

        # TODO only for prototype
        data = [
            ("#1", "Peptalker101", "1837"),
            ("#2", "ItsJakePlayz21", "1835"),
            ("#3", "Viradex", "978"),
            ("#4", "TrexGamerGirl", "972"),
            ("#5", "Scyrist", "966"),
        ]

        for index, (place, name, total) in enumerate(data):
            row = self.leaderboard_table.rowCount()
            self.leaderboard_table.insertRow(row)

            place_item = QTableWidgetItem(place)
            name_item = QTableWidgetItem(name)
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
            total_item.setForeground(color)

            if index <= 2:
                for item in (place_item, name_item, total_item):
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)

            place_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.leaderboard_table.setItem(row, 0, place_item)
            self.leaderboard_table.setItem(row, 1, name_item)
            self.leaderboard_table.setItem(row, 2, total_item)

        left_card = Card(
            accent=darken_color("#8A5CFF", 0.6),
            blur_radius=35,
        )
        left_layout = QVBoxLayout(left_card)
        left_layout.setContentsMargins(20, 20, 20, 20)

        left_layout.addWidget(leaderboard_heading)
        left_layout.addSpacing(2)
        left_layout.addWidget(leaderboard_desc)
        left_layout.addSpacing(15)
        left_layout.addWidget(self.leaderboard_table, stretch=5)
        left_layout.addStretch(1)

        stats_heading = QLabel("Game Stats")
        stats_heading.setStyleSheet("font-size: 24px;" "font-weight: 600;")

        stats_desc = QLabel("Overall game stats")
        stats_desc.setStyleSheet("font-size: 14px;" "color: #6E6E6E;")

        base_dir = Path(__file__).resolve().parent.parent.parent
        icons_path = base_dir / "assets" / "icons"

        winner_stat = make_stat_card(
            "Winner", "Peptalker101", icons_path / "trophy.png"
        )
        highest_points_stat = make_stat_card(
            "Highest Points", "1837", icons_path / "star.png"
        )
        fastest_answer_stat = make_stat_card(
            "Fastest Answer", "0.7s", icons_path / "lightning.png"
        )
        hardest_question_stat = make_stat_card(
            "Hardest Question", "Q2", icons_path / "cross.png"
        )
        players_stat = make_stat_card("Total Players", "5", icons_path / "users.png")
        questions_stat = make_stat_card(
            "Total Questions", "2", icons_path / "question.png"
        )

        stats_grid = QGridLayout()
        stats_grid.setSpacing(10)

        stats_grid.addWidget(winner_stat, 0, 0)
        stats_grid.addWidget(highest_points_stat, 0, 1)
        stats_grid.addWidget(fastest_answer_stat, 1, 0)
        stats_grid.addWidget(hardest_question_stat, 1, 1)
        stats_grid.addWidget(players_stat, 2, 0)
        stats_grid.addWidget(questions_stat, 2, 1)

        return_btn = QPushButton("Return to Menu")
        return_btn.setFixedSize(140, 40)
        return_btn.clicked.connect(lambda: self.go_to(Screens.COMMON_MENU))
        return_btn.setStyleSheet("font-size: 14px;")

        right_card = Card()
        right_layout = QVBoxLayout(right_card)
        right_layout.setContentsMargins(20, 20, 20, 20)

        right_layout.addWidget(stats_heading)
        right_layout.addSpacing(2)
        right_layout.addWidget(stats_desc)
        right_layout.addSpacing(15)
        right_layout.addLayout(stats_grid)
        right_layout.addSpacing(20)
        right_layout.addWidget(return_btn, alignment=Qt.AlignmentFlag.AlignRight)
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
