import random
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
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from core.app.screen_ids import Screens
from ui.screens.base_screen import BaseScreen
from ui.components.card import Card, StatCard
from models.payloads import ClientFinalResultsPayload

from utils.color import darken_color
from utils.formatting import to_ordinal
from utils.feedback_generator import feedback_generator


class ClientFinalResultScreen(BaseScreen):
    title_text = "Quiz Master – Final Results"

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.icons_path = self.base_dir / "assets" / "icons"

        self.setup_ui()

    def setup_ui(self) -> None:
        ## FONTS SETUP ##
        feedback_font = QFont()
        feedback_font.setPointSize(11)

        table_font = QFont()
        table_font.setPointSize(12)

        self.table_bold_font = QFont()
        self.table_bold_font.setPointSize(12)
        self.table_bold_font.setBold(True)

        ## WIDGETS SETUP ##
        # Header
        self.ordinal_position = QLabel()
        self.ordinal_position.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ordinal_position.setStyleSheet("font-size: 42px;" "font-weight: 600;")

        self.position_feedback = QLabel()
        self.position_feedback.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.position_feedback.setStyleSheet("font-size: 16px;" "color: #A0A0A0;")

        # Left side
        self.left_card = Card()

        stats_heading = QLabel("Your Performance")
        stats_heading.setStyleSheet("font-size: 24px;" "font-weight: 600;")

        self.nickname = QLabel()
        self.nickname.setStyleSheet("font-size: 16px;" "color: #6E6E6E;")

        self.rank_stat = StatCard("Rank", "", self.icons_path / "trophy.png")
        self.points_stat = StatCard("Points", "", self.icons_path / "star.png")
        self.correct_stat = StatCard("Correct", "", self.icons_path / "correct.png")
        self.accuracy_stat = StatCard("Accuracy", "", self.icons_path / "bullseye.png")

        self.feedback = QLabel()
        self.feedback.setWordWrap(True)
        self.feedback.setFont(feedback_font)
        self.feedback.setStyleSheet("""
            background-color: #262626;
            border-radius: 10px;
            padding: 12px;
            color: #C8C8C8;
        """)

        # Right side
        right_card = Card()

        leaderboard_heading = QLabel("Leaderboard Snapshot")
        leaderboard_heading.setStyleSheet("font-size: 24px;" "font-weight: 600;")

        leaderboard_desc = QLabel("Nearby rankings")
        leaderboard_desc.setStyleSheet("font-size: 14px;" "color: #6E6E6E;")

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

        ## LAYOUTS SETUP ##
        vbox_header = QVBoxLayout()
        vbox_header.addWidget(self.ordinal_position)
        vbox_header.addSpacing(2)
        vbox_header.addWidget(self.position_feedback)
        vbox_header.addSpacing(20)

        stats_grid = QGridLayout()
        stats_grid.setSpacing(10)
        stats_grid.addWidget(self.rank_stat, 0, 0)
        stats_grid.addWidget(self.points_stat, 0, 1)
        stats_grid.addWidget(self.correct_stat, 1, 0)
        stats_grid.addWidget(self.accuracy_stat, 1, 1)

        vbox_left = QVBoxLayout(self.left_card)
        vbox_left.setContentsMargins(20, 20, 20, 20)
        vbox_left.addWidget(stats_heading)
        vbox_left.addSpacing(2)
        vbox_left.addWidget(self.nickname)
        vbox_left.addSpacing(15)
        vbox_left.addLayout(stats_grid)
        vbox_left.addSpacing(15)
        vbox_left.addWidget(self.feedback)
        vbox_left.addStretch(1)

        vbox_right = QVBoxLayout(right_card)
        vbox_right.setContentsMargins(20, 20, 20, 20)
        vbox_right.addWidget(leaderboard_heading)
        vbox_right.addSpacing(2)
        vbox_right.addWidget(leaderboard_desc)
        vbox_right.addSpacing(15)
        vbox_right.addWidget(self.leaderboard_table)
        vbox_right.addSpacing(20)
        vbox_right.addWidget(return_btn, alignment=Qt.AlignmentFlag.AlignRight)
        vbox_right.addStretch(1)

        hbox = QHBoxLayout()
        hbox.addWidget(self.left_card, 5)
        hbox.addSpacing(20)
        hbox.addWidget(right_card, 4)

        vbox = QVBoxLayout()
        vbox.setContentsMargins(40, 20, 40, 20)
        vbox.addLayout(vbox_header)
        vbox.addLayout(hbox, 1)

        self.setLayout(vbox)

    def show_leaderboard_values(
        self, players: list[tuple[str, str, str]], own_nickname: str
    ) -> None:
        """Show the entries in the leaderboard table, and mark the own nickname to stand out."""
        for rank, name, total in players:
            # If the name matches the nickname
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

            # Bold row if it matches the nickname
            if is_you:
                rank_item.setFont(self.table_bold_font)
                name_item.setFont(self.table_bold_font)
                total_item.setFont(self.table_bold_font)

            self.leaderboard_table.setItem(row, 0, rank_item)
            self.leaderboard_table.setItem(row, 1, name_item)
            self.leaderboard_table.setItem(row, 2, total_item)

        self._update_table_height()

    def clear_leaderboard(self) -> None:
        """Remove all rows in the leaderboard table."""
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

        # Converts from decimal to number 0-100
        accuracy = round(payload.accuracy * 100)

        self.ordinal_position.setText(f"{to_ordinal(payload.rank)} Place!")
        if payload.on_podium:
            self.ordinal_position.setStyleSheet(
                f"font-size: 42px; font-weight: 600; color: {theme_color};"
            )

        # Show certain message if on podium, else show random message
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

        # Set custom feedback based on certain cases as a sentence
        self.feedback.setText(
            feedback_generator(
                payload.on_podium,
                payload.is_first,
                payload.is_last,
                payload.behind_nickname,
                payload.points_behind,
            )
        )

        # Show players in leaderboard
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

    def _update_table_height(self) -> None:
        """Update table height based on the number of rows in the leaderboard table."""
        self.leaderboard_table.resizeRowsToContents()

        total = self.leaderboard_table.horizontalHeader().height()
        total += sum(
            self.leaderboard_table.rowHeight(i)
            for i in range(self.leaderboard_table.rowCount())
        )
        total += self.leaderboard_table.frameWidth() * 2

        self.leaderboard_table.setFixedHeight(total)
