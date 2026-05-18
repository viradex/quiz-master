from PyQt6.QtWidgets import QLabel, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from core.screen_ids import Screens
from ui.screens.base_screen import BaseScreen
from ui.components.card import Card
from ui.components.button import LeaveButton
from ui.utils.color import darken_color


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
            "font-size: 38px;" "font-weight: 600;" "color: #CD7F32;"
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
        stats_heading.setWordWrap(True)
        stats_heading.setStyleSheet("font-size: 24px;" "font-weight: 600;")

        self.nickname = QLabel("Viradex • Podium finish")
        self.nickname.setStyleSheet("font-size: 16px;" "color: #6E6E6E;")

        accuracy_stat = self._make_stat_card("Accuracy", "50%")
        correct_stat = self._make_stat_card("Correct", "1 / 2")
        points_stat = self._make_stat_card("Points", "1824")
        place_stat = self._make_stat_card("Place", "#3")

        stats_grid = QGridLayout()
        stats_grid.setSpacing(10)

        stats_grid.addWidget(accuracy_stat, 0, 0)
        stats_grid.addWidget(correct_stat, 0, 1)
        stats_grid.addWidget(points_stat, 1, 0)
        stats_grid.addWidget(place_stat, 1, 1)

        self.feedback = QLabel(
            "Great effort! You finished on the podium and were only 16 points behind 2nd place."
        )
        self.feedback.setWordWrap(True)
        self.feedback.setStyleSheet("font-size: 14px;" "color: #E6D3B0;")

        left_card = Card()
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

        right_card = Card()
        right_layout = QVBoxLayout(right_card)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.addStretch(1)

        hbox = QHBoxLayout()
        hbox.addWidget(left_card, 3)
        hbox.addSpacing(20)
        hbox.addWidget(right_card, 2)

        vbox = QVBoxLayout()
        vbox.setContentsMargins(40, 20, 40, 20)

        vbox.addLayout(header_layout)
        vbox.addLayout(hbox, 1)

        self.setLayout(vbox)

    def _make_stat_card(self, title, value):
        container = QWidget()
        container.setStyleSheet("background-color: #272727;" "border-radius: 10px;")

        layout = QVBoxLayout(container)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(2)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size: 14px;" "color: #8A8A8A;")

        value_lbl = QLabel(value)
        value_lbl.setStyleSheet("font-size: 24px;" "font-weight: 600;")

        layout.addWidget(title_lbl)
        layout.addSpacing(5)
        layout.addWidget(value_lbl)

        return container
