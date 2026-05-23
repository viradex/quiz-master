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
from PyQt6.QtGui import QFont

from core.screen_ids import Screens
from ui.screens.base_screen import BaseScreen
from ui.components.card import Card, make_stat_card


class ClientFinalResultScreen(BaseScreen):
    title_text = "Quiz Master – Final Results"

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setup_ui()

    def setup_ui(self):
        self.ordinal_position = QLabel("3rd Place!")
        self.ordinal_position.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Gold: #F5C542
        # Silver: #C9CED6
        # Bronze: #CD7F32
        self.ordinal_position.setStyleSheet(
            "font-size: 42px;" "font-weight: 600;" "color: #CD7F32;"
        )

        self.position_feedback = QLabel("Podium finish!")
        self.position_feedback.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.position_feedback.setStyleSheet("font-size: 16px;" "color: #A0A0A0;")

        header_layout = QVBoxLayout()
        header_layout.addWidget(self.ordinal_position)
        header_layout.addSpacing(2)
        header_layout.addWidget(self.position_feedback)
        header_layout.addSpacing(20)

        stats_heading = QLabel("Your Performance")
        stats_heading.setStyleSheet("font-size: 24px;" "font-weight: 600;")

        self.nickname = QLabel("Viradex • Podium finish")
        self.nickname.setStyleSheet("font-size: 16px;" "color: #6E6E6E;")

        # TODO use actual icons
        base_dir = Path(__file__).resolve().parent.parent.parent
        icons_path = base_dir / "assets" / "icons"

        place_stat = make_stat_card("Place", "#3", icons_path / "trophy.png")
        points_stat = make_stat_card("Points", "1824", icons_path / "star.png")
        correct_stat = make_stat_card("Correct", "1 / 2", icons_path / "correct.png")
        accuracy_stat = make_stat_card("Accuracy", "50%", icons_path / "bullseye.png")

        stats_grid = QGridLayout()
        stats_grid.setSpacing(10)

        stats_grid.addWidget(place_stat, 0, 0)
        stats_grid.addWidget(points_stat, 0, 1)
        stats_grid.addWidget(correct_stat, 1, 0)
        stats_grid.addWidget(accuracy_stat, 1, 1)

        feedback_font = QFont()
        feedback_font.setPointSize(11)

        self.feedback = QLabel(
            "You finished on the podium and were 835 points behind ItsJakePlayz21!"
        )
        self.feedback.setWordWrap(True)
        self.feedback.setFont(feedback_font)
        self.feedback.setStyleSheet("""
            background-color: #262626;
            border-radius: 10px;
            padding: 12px;
            color: #C8C8C8;
        """)

        left_card = Card(
            accent="#CD7F32",
            blur_radius=35,
        )
        left_layout = QVBoxLayout(left_card)
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
        leaderboard_desc.setStyleSheet("font-size: 12px;" "color: #6E6E6E;")

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

        self.leaderboard_table.setColumnWidth(0, 70)
        self.leaderboard_table.setColumnWidth(2, 70)

        # TODO round table corners
        self.leaderboard_table.setStyleSheet("""
            QTableWidget {
                background-color: #252525;
                border: none;
                border-radius: 12px;
            }

            QHeaderView::section {
                background-color: #2F2F2F;
                border: none;
                padding: 6px;
                font-weight: 600;
            }

            QTableWidget::item {
                padding: 6px;
            }
        """)

        # TODO only for prototype
        data = [
            ("#2", "ItsJakePlayz21", "1835"),
            ("#3", "Viradex (you)", "1000"),
            ("#4", "TrexGamerGirl", "972"),
        ]

        for place, name, total in data:
            row = self.leaderboard_table.rowCount()
            self.leaderboard_table.insertRow(row)

            place_item = QTableWidgetItem(place)
            name_item = QTableWidgetItem(name)
            total_item = QTableWidgetItem(total)

            place_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            if name.endswith("(you)"):
                place_item.setFont(table_bold_font)
                name_item.setFont(table_bold_font)
                total_item.setFont(table_bold_font)

            self.leaderboard_table.setItem(row, 0, place_item)
            self.leaderboard_table.setItem(row, 1, name_item)
            self.leaderboard_table.setItem(row, 2, total_item)

        self._update_table_height()

        self.return_btn = QPushButton("Return to Menu")
        self.return_btn.setFixedSize(140, 40)
        self.return_btn.clicked.connect(lambda: self.go_to(Screens.COMMON_MENU))
        self.return_btn.setStyleSheet("font-size: 14px;")

        right_card = Card()
        right_layout = QVBoxLayout(right_card)
        right_layout.setContentsMargins(20, 20, 20, 20)

        right_layout.addWidget(leaderboard_heading)
        right_layout.addSpacing(2)
        right_layout.addWidget(leaderboard_desc)
        right_layout.addSpacing(15)
        right_layout.addWidget(self.leaderboard_table)
        right_layout.addSpacing(20)
        right_layout.addWidget(self.return_btn, alignment=Qt.AlignmentFlag.AlignRight)
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

    def _update_table_height(self):
        header_height = self.leaderboard_table.horizontalHeader().height()
        row_height = self.leaderboard_table.rowHeight(0)
        self.leaderboard_table.setFixedHeight(header_height + (row_height * 3) + 2)
