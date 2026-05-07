from PyQt6.QtWidgets import (
    QLabel,
    QPushButton,
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
from ui.components.question_timer import QuestionTimer
from ui.components.dialogs import confirm_warning
from ui.utils.color import darken_color


class ClientMultiQuestionScreen(BaseScreen):
    title_text = "Quiz Master – Question 1 / 2"

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setup_ui()

    def setup_ui(self):
        question_num_font = QFont()
        question_num_font.setPointSize(12)

        self.question_num = QLabel("Question 1 / 2")
        self.question_num.setFont(question_num_font)

        question_font = QFont()
        question_font.setPointSize(26)
        question_font.setBold(True)

        self.question_lbl = QLabel("What is the largest planet in the solar system?")
        self.question_lbl.setWordWrap(True)
        self.question_lbl.setFont(question_font)

        colors = {
            "red": {"normal": "#C94F4F", "hover": "#D45B5B", "click": "#A94444"},
            "blue": {"normal": "#4A78C2", "hover": "#5A86CC", "click": "#3D66A8"},
            "yellow": {"normal": "#B89B2E", "hover": "#C5A83A", "click": "#9E8424"},
            "green": {"normal": "#3E9B68", "hover": "#4AA977", "click": "#347F56"},
        }

        button_grid = QGridLayout()
        button_grid.setColumnStretch(0, 1)
        button_grid.setColumnStretch(1, 1)
        button_grid.setRowStretch(0, 1)
        button_grid.setRowStretch(1, 1)

        self.answer_buttons = []

        # TODO only for prototype
        index = 0
        answers = ["Jupiter", "Saturn", "Uranus", "Neptune"]

        for row in range(2):
            for column in range(2):
                color_name = list(colors.keys())[index]

                btn = self._create_answer_button(
                    answers[index],
                    colors[color_name]["normal"],
                    colors[color_name]["hover"],
                    colors[color_name]["click"],
                )
                self.answer_buttons.append(btn)
                button_grid.addWidget(btn, row, column)

                index += 1

        vbox_left = QVBoxLayout()
        vbox_left.addSpacing(20)
        vbox_left.addWidget(self.question_num)
        vbox_left.addSpacing(10)
        vbox_left.addWidget(self.question_lbl)
        vbox_left.addSpacing(20)
        vbox_left.addLayout(button_grid, 1)
        vbox_left.addSpacing(20)

        leave_btn = QPushButton("Leave")
        leave_btn.setFixedWidth(60)
        leave_btn.clicked.connect(self.return_to_menu)
        leave_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #bbb;
                border: 1px solid #444;
                border-radius: 8px;
                padding: 6px;
                font-size: 12px;
            }

            QPushButton:hover {
                background-color: #333;
                color: white;
            }

            QPushButton:pressed {
                background-color: #222;
            }
        """)

        self.question_timer = QuestionTimer(total_ms=20000, parent=self)
        # TODO use this for calling func when timer ends
        # self.question_timer.timeup.connect()

        right_vbox = QVBoxLayout()
        right_vbox.addWidget(leave_btn, 0, alignment=Qt.AlignmentFlag.AlignRight)
        right_vbox.addStretch()
        right_vbox.addWidget(
            self.question_timer, 1, alignment=Qt.AlignmentFlag.AlignRight
        )

        hbox = QHBoxLayout()
        hbox.setContentsMargins(50, 20, 20, 20)
        hbox.addLayout(vbox_left, 1)
        hbox.addSpacing(40)
        hbox.addLayout(right_vbox)

        self.setLayout(hbox)

    def _style_button(self, bg, hover, click, text):
        return f"""
            QPushButton {{
                background-color: {bg};
                color: {text};
                border: none;
                border-radius: 14px;
                padding: 18px;
                margin: 6px;
                font-size: 22px;
                font-weight: 600;
            }}

            QPushButton:hover {{
                background-color: {hover};
            }}

            QPushButton:pressed {{
                background-color: {click};
            }}
        """

    def _create_answer_button(self, text, bg, hover_bg, click_bg):
        button = QPushButton(text)
        button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        button.setCursor(Qt.CursorShape.PointingHandCursor)

        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(0)
        glow.setOffset(0, 0)
        glow.setColor(QColor(bg))
        button.setGraphicsEffect(glow)

        button._base = (bg, hover_bg, click_bg, "white")
        button._glow = glow

        button.setStyleSheet(self._style_button(*button._base))
        button.clicked.connect(lambda _, b=button: self.on_answer_clicked(b))

        return button

    def on_answer_clicked(self, selected):
        self.question_timer.lock()

        for btn in self.answer_buttons:
            btn.setEnabled(False)
            btn._glow.setBlurRadius(0)

            bg, hover, click, text = btn._base

            if btn is selected:
                btn.setStyleSheet(self._style_button(bg, hover, click, text))
                btn._glow.setBlurRadius(80)
            else:
                dim = darken_color(bg, 0.8)
                btn.setStyleSheet(self._style_button(dim, dim, dim, "white"))

    def reset_buttons(self):
        for btn in self.answer_buttons:
            bg, hover, click, text = btn._base

            btn.setEnabled(True)
            btn.setStyleSheet(self._style_button(bg, hover, click, text))
            btn._glow.setBlurRadius(0)

    def return_to_menu(self):
        confirm = confirm_warning(
            self,
            "Confirm Returning",
            "Are you sure you want to leave the game and return to menu?",
        )
        if confirm:
            self.go_to(Screens.COMMON_MENU)

    def on_enter(self):
        self.question_timer.on_enter()

    def on_leave(self):
        self.question_timer.on_leave()
        self.reset_buttons()
