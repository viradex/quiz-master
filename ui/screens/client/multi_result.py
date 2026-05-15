from PyQt6.QtWidgets import (
    QLabel,
    QPushButton,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QSizePolicy,
    QGraphicsDropShadowEffect,
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt

from core.screen_ids import Screens
from ui.screens.base_screen import BaseScreen
from ui.components.card import Card


class ClientMultiResultScreen(BaseScreen):
    title_text = "Quiz Master – Results"

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setup_ui()

    def setup_ui(self):
        self.result_lbl = QLabel("Correct! +1000")
        self.result_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Correct: #3DDC84
        # Incorrect: #FF5C5C
        self.result_lbl.setStyleSheet("""
            QLabel {
                font-size: 32px;
                font-weight: 600;
                color: #3DDC84;
            }
        """)

        self.your_answer = QLabel("Your answer: Harshil")
        self.your_answer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.your_answer.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #A0A0A0;
            }
        """)

        header_layout = QVBoxLayout()
        header_layout.addWidget(self.result_lbl)
        header_layout.addSpacing(5)
        header_layout.addWidget(self.your_answer)
        header_layout.addSpacing(20)

        self.question_lbl = QLabel("What is the largest planet in the solar system?")
        self.question_lbl.setWordWrap(True)
        self.question_lbl.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: 600;
            }
        """)

        self.correct_answer = QLabel("Correct answer: Harshil")
        self.correct_answer.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #A0A0A0;
            }
        """)

        left_card = Card()
        left_layout = QVBoxLayout(left_card)
        left_layout.setContentsMargins(20, 20, 20, 20)

        left_layout.addWidget(self.question_lbl)
        left_layout.addSpacing(5)
        left_layout.addWidget(self.correct_answer)
        left_layout.addStretch(1)

        right_card = Card()
        right_layout = QVBoxLayout(right_card)
        right_layout.setContentsMargins(20, 20, 20, 20)

        hbox = QHBoxLayout()
        hbox.addWidget(left_card, 3)
        hbox.addSpacing(20)
        hbox.addWidget(right_card, 2)

        vbox = QVBoxLayout()
        vbox.setContentsMargins(40, 20, 40, 20)

        vbox.addLayout(header_layout)
        vbox.addLayout(hbox, 1)

        self.setLayout(vbox)
