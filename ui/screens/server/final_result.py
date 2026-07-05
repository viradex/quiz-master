from pathlib import Path
import random
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
from PyQt6.QtGui import QFont, QColor

from core.app.screen_ids import Screens
from ui.screens.base_screen import BaseScreen
from ui.components.card import Card, StatCard
from utils.color import darken_color


class ServerFinalResultScreen(BaseScreen):
    title_text = "Quiz Master – Final Results"

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setup_ui()

    def setup_ui(self):
        heading = QLabel("Final Results")
        heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        heading.setStyleSheet("font-size: 36px;" "font-weight: 600;")

        self.winner = QLabel()
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

        self.leaderboard_table = QTableWidget()
        self.leaderboard_table.setFont(table_font)
        self.leaderboard_table.setShowGrid(False)
        self.leaderboard_table.setAlternatingRowColors(True)
        self.leaderboard_table.setColumnCount(3)
        self.leaderboard_table.setHorizontalHeaderLabels(["Rank", "Name", "Total"])
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

        left_card = Card(accent=darken_color("#8A5CFF", factor=0.6))
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

        self.winner_stat = StatCard("Winner", "", icons_path / "trophy.png")
        self.highest_points_stat = StatCard(
            "Highest Points", "", icons_path / "star.png"
        )
        self.fastest_answer_stat = StatCard(
            "Fastest Answer", "", icons_path / "lightning.png"
        )
        self.average_accuracy_stat = StatCard(
            "Average Accuracy", "", icons_path / "bullseye.png"
        )
        self.players_stat = StatCard("Total Players", "", icons_path / "users.png")
        self.questions_stat = StatCard(
            "Total Questions", "", icons_path / "question.png"
        )

        stats_grid = QGridLayout()
        stats_grid.setSpacing(10)

        stats_grid.addWidget(self.winner_stat, 0, 0)
        stats_grid.addWidget(self.highest_points_stat, 0, 1)
        stats_grid.addWidget(self.fastest_answer_stat, 1, 0)
        stats_grid.addWidget(self.average_accuracy_stat, 1, 1)
        stats_grid.addWidget(self.players_stat, 2, 0)
        stats_grid.addWidget(self.questions_stat, 2, 1)

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
        right_layout.addSpacing(10)
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

    def show_leaderboard_values(self, players: list[tuple[str, str, str]]) -> None:
        for index, (rank, name, total) in enumerate(players):
            row = self.leaderboard_table.rowCount()
            self.leaderboard_table.insertRow(row)

            rank_item = QTableWidgetItem(rank)
            name_item = QTableWidgetItem(name)
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
            total_item.setForeground(color)

            if index <= 2:
                for item in (rank_item, name_item, total_item):
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)

            rank_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.leaderboard_table.setItem(row, 0, rank_item)
            self.leaderboard_table.setItem(row, 1, name_item)
            self.leaderboard_table.setItem(row, 2, total_item)

    def clear_leaderboard(self) -> None:
        self.leaderboard_table.setRowCount(0)

    def on_enter(self, payload: dict) -> None:
        average_accuracy = round(payload["average_accuracy"] * 100)

        message_choices = [
            "{player} takes 1st place!",
            "{player} claims the top spot!",
            "{player} secures the victory!",
            "{player} takes the crown!",
            "{player} tops the leaderboard!",
        ]

        winner_text = random.choice(message_choices).format(player=payload["winner"])
        self.winner.setText(winner_text)

        self.winner_stat.set_value(payload["winner"])
        self.highest_points_stat.set_value(str(payload["highest_points"]))
        self.fastest_answer_stat.set_value(f"{payload['fastest_answer']:.2f}s")
        self.average_accuracy_stat.set_value(f"{average_accuracy}%")
        self.players_stat.set_value(str(payload["total_players"]))
        self.questions_stat.set_value(str(payload["total_questions"]))

        leaderboard_players = []
        for player in payload["leaderboard"]:
            leaderboard_players.append(
                (
                    f"#{player['rank']}",
                    player["name"],
                    str(player["total"]),
                )
            )

        self.show_leaderboard_values(leaderboard_players)

    def on_leave(self):
        self.winner_stat.set_value("")
        self.highest_points_stat.set_value("")
        self.fastest_answer_stat.set_value("")
        self.average_accuracy_stat.set_value("")
        self.players_stat.set_value("")
        self.questions_stat.set_value("")

        self.clear_leaderboard()
