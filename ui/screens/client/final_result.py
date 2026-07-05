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
from PyQt6.QtGui import QFont

from core.app.screen_ids import Screens
from ui.screens.base_screen import BaseScreen
from ui.components.card import Card, StatCard
from models.payloads import ClientFinalResultsPayload

from utils.color import darken_color
from utils.formatting import to_ordinal
from utils.feedback_generator import feedback_generator


class ClientFinalResultScreen(BaseScreen):
    title_text = "Quiz Master – Final Results"

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setup_ui()

    def setup_ui(self):
        self.ordinal_position = QLabel()
        self.ordinal_position.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ordinal_position.setStyleSheet("font-size: 42px;" "font-weight: 600;")

        self.position_feedback = QLabel()
        self.position_feedback.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.position_feedback.setStyleSheet("font-size: 16px;" "color: #A0A0A0;")

        header_layout = QVBoxLayout()
        header_layout.addWidget(self.ordinal_position)
        header_layout.addSpacing(2)
        header_layout.addWidget(self.position_feedback)
        header_layout.addSpacing(20)

        stats_heading = QLabel("Your Performance")
        stats_heading.setStyleSheet("font-size: 24px;" "font-weight: 600;")

        self.nickname = QLabel()
        self.nickname.setStyleSheet("font-size: 16px;" "color: #6E6E6E;")

        base_dir = Path(__file__).resolve().parent.parent.parent
        icons_path = base_dir / "assets" / "icons"

        self.rank_stat = StatCard("Rank", "", icons_path / "trophy.png")
        self.points_stat = StatCard("Points", "", icons_path / "star.png")
        self.correct_stat = StatCard("Correct", "", icons_path / "correct.png")
        self.accuracy_stat = StatCard("Accuracy", "", icons_path / "bullseye.png")

        stats_grid = QGridLayout()
        stats_grid.setSpacing(10)

        stats_grid.addWidget(self.rank_stat, 0, 0)
        stats_grid.addWidget(self.points_stat, 0, 1)
        stats_grid.addWidget(self.correct_stat, 1, 0)
        stats_grid.addWidget(self.accuracy_stat, 1, 1)

        feedback_font = QFont()
        feedback_font.setPointSize(11)

        self.feedback = QLabel()
        self.feedback.setWordWrap(True)
        self.feedback.setFont(feedback_font)
        self.feedback.setStyleSheet("""
            background-color: #262626;
            border-radius: 10px;
            padding: 12px;
            color: #C8C8C8;
        """)

        self.left_card = Card()
        left_layout = QVBoxLayout(self.left_card)
        left_layout.setContentsMargins(20, 20, 20, 20)

        left_layout.addWidget(stats_heading)
        left_layout.addSpacing(2)
        left_layout.addWidget(self.nickname)
        left_layout.addSpacing(15)
        left_layout.addLayout(stats_grid)
        left_layout.addSpacing(15)
        left_layout.addWidget(self.feedback)
        left_layout.addStretch(1)

        leaderboard_heading = QLabel("Leaderboard Snapshot")
        leaderboard_heading.setStyleSheet("font-size: 24px;" "font-weight: 600;")

        leaderboard_desc = QLabel("Nearby rankings")
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
        self.leaderboard_table.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
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

        return_btn = QPushButton("Return to Menu")
        return_btn.setFixedSize(140, 40)
        return_btn.clicked.connect(self.on_return)
        return_btn.setStyleSheet("font-size: 14px;")

        right_card = Card()
        right_layout = QVBoxLayout(right_card)
        right_layout.setContentsMargins(20, 20, 20, 20)

        right_layout.addWidget(leaderboard_heading)
        right_layout.addSpacing(2)
        right_layout.addWidget(leaderboard_desc)
        right_layout.addSpacing(15)
        right_layout.addWidget(self.leaderboard_table)
        right_layout.addSpacing(20)
        right_layout.addWidget(return_btn, alignment=Qt.AlignmentFlag.AlignRight)
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

    def _update_table_height(self):
        self.leaderboard_table.resizeRowsToContents()

        total = self.leaderboard_table.horizontalHeader().height()
        total += sum(
            self.leaderboard_table.rowHeight(i)
            for i in range(self.leaderboard_table.rowCount())
        )
        total += self.leaderboard_table.frameWidth() * 2

        self.leaderboard_table.setFixedHeight(total)

    def show_leaderboard_values(
        self, players: list[tuple[str, str, str]], own_nickname: str
    ) -> None:
        table_bold_font = QFont()
        table_bold_font.setPointSize(12)
        table_bold_font.setBold(True)

        for rank, name, total in players:
            is_you = name == own_nickname

            row = self.leaderboard_table.rowCount()
            self.leaderboard_table.insertRow(row)

            if is_you:
                name += " (you)"

            rank_item = QTableWidgetItem(rank)
            name_item = QTableWidgetItem(name)
            total_item = QTableWidgetItem(total)

            rank_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            if is_you:
                rank_item.setFont(table_bold_font)
                name_item.setFont(table_bold_font)
                total_item.setFont(table_bold_font)

            self.leaderboard_table.setItem(row, 0, rank_item)
            self.leaderboard_table.setItem(row, 1, name_item)
            self.leaderboard_table.setItem(row, 2, total_item)

        self._update_table_height()

    def clear_leaderboard(self) -> None:
        self.leaderboard_table.setRowCount(0)

    def on_return(self) -> None:
        self.reset_status()
        self.go_to(Screens.COMMON_MENU)

    def on_enter(self, payload: ClientFinalResultsPayload) -> None:
        # Gold: #F5C542
        # Silver: #C9CED6
        # Bronze: #CD7F32
        # Purple: #8A5CFF
        if payload.rank == 1:
            theme_color = "#F5C542"
        elif payload.rank == 2:
            theme_color = "#C9CED6"
        elif payload.rank == 3:
            theme_color = "#CD7F32"
        else:
            theme_color = "#8A5CFF"

        message_choices = [
            "Nice effort!",
            "Well played!",
            "Good game!",
            "Thanks for playing!",
            "Great participation!",
        ]

        accuracy = round(payload.accuracy * 100)

        self.ordinal_position.setText(f"{to_ordinal(payload.rank)} Place!")
        if payload.on_podium:
            self.ordinal_position.setStyleSheet(
                f"font-size: 42px; font-weight: 600; color: {theme_color};"
            )

        if payload.on_podium:
            self.position_feedback.setText("You finished on the podium!")
        else:
            self.position_feedback.setText(random.choice(message_choices))

        self.left_card.set_accent(darken_color(theme_color, factor=0.6))
        self.nickname.setText(f"Nickname: {payload.nickname}")

        self.rank_stat.set_value(f"#{payload.rank}")
        self.points_stat.set_value(f"{payload.total_points}")
        self.correct_stat.set_value(
            f"{payload.total_correct} / {payload.total_questions}"
        )
        self.accuracy_stat.set_value(f"{accuracy}%")

        self.feedback.setText(
            feedback_generator(
                payload.on_podium,
                payload.is_first,
                payload.is_last,
                payload.behind_nickname,
                payload.points_behind,
            )
        )

        leaderboard_players = []
        for player in payload.leaderboard:
            leaderboard_players.append(
                (
                    f"#{player['rank']}",
                    player["name"],
                    str(player["total"]),
                )
            )

        self.show_leaderboard_values(leaderboard_players, payload.nickname)

    def on_leave(self) -> None:
        self.ordinal_position.setText("")
        self.ordinal_position.setStyleSheet("font-size: 42px;" "font-weight: 600;")

        self.position_feedback.setText("")

        self.left_card.reset_accent()
        self.nickname.setText("")

        self.rank_stat.set_value("")
        self.points_stat.set_value("")
        self.correct_stat.set_value("")
        self.accuracy_stat.set_value("")

        self.feedback.setText("")

        self.clear_leaderboard()
