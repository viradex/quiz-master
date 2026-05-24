from PyQt6.QtWidgets import (
    QPushButton,
    QWidget,
    QGridLayout,
    QSizePolicy,
    QGraphicsDropShadowEffect,
)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt, pyqtSignal

from ui.utils.color import darken_color


# TODO code is all-over-the-place, and it's obvious that it
# was changed as the code progressively got complex rather than
# improving core design of the class, maybe improve it later?
# like adding a ButtonStyle dataclass, for instance
class AnswerButtonGrid(QWidget):
    BUTTON_COLORS = {
        "red": {"normal": "#C94F4F", "hover": "#D45B5B", "click": "#A94444"},
        "blue": {"normal": "#4A78C2", "hover": "#5A86CC", "click": "#3D66A8"},
        "yellow": {"normal": "#B89B2E", "hover": "#C5A83A", "click": "#9E8424"},
        "green": {"normal": "#3E9B68", "hover": "#4AA977", "click": "#347F56"},
    }

    answer_select = pyqtSignal(int)

    def __init__(self, answers, mode, parent=None):
        super().__init__(parent)
        self.answers = answers
        self.mode = mode

        self.correct_index = None
        self.selected_index = None

        if not 2 <= len(self.answers) <= 4:
            raise ValueError(
                f"Expected between 2-4 answers, received {len(self.answers)}"
            )

        self.setup_grid()
        self.setup_buttons()

    def setup_grid(self):
        self.button_grid = QGridLayout()
        self.button_grid.setColumnStretch(0, 1)
        self.button_grid.setColumnStretch(1, 1)
        self.button_grid.setRowStretch(0, 1)
        self.button_grid.setRowStretch(1, 1)

        self.setLayout(self.button_grid)

    def setup_buttons(self):
        buttons = self._build_buttons()
        self._place_buttons(buttons)

    def _build_buttons(self):
        self.answer_buttons = []
        color_names = ["red", "blue", "yellow", "green"]

        for i, answer in enumerate(self.answers):
            color_name = color_names[i]

            if self.mode == "server":
                btn = self._create_answer_button(
                    answer,
                    self.BUTTON_COLORS[color_name]["normal"],
                    self.BUTTON_COLORS[color_name]["normal"],
                    self.BUTTON_COLORS[color_name]["normal"],
                )
            else:
                btn = self._create_answer_button(
                    answer,
                    self.BUTTON_COLORS[color_name]["normal"],
                    self.BUTTON_COLORS[color_name]["hover"],
                    self.BUTTON_COLORS[color_name]["click"],
                )

            self.answer_buttons.append(btn)

        return self.answer_buttons

    def _place_buttons(self, buttons):
        count = len(buttons)

        if count == 2:
            self.button_grid.addWidget(buttons[0], 0, 0, 2, 1)  # red
            self.button_grid.addWidget(buttons[1], 0, 1, 2, 1)  # blue
        elif count == 3:
            self.button_grid.addWidget(buttons[0], 0, 0)  # red
            self.button_grid.addWidget(buttons[1], 0, 1)  # blue
            self.button_grid.addWidget(buttons[2], 1, 0, 1, 2)  # yellow
        elif count == 4:
            self.button_grid.addWidget(buttons[0], 0, 0)  # red
            self.button_grid.addWidget(buttons[1], 0, 1)  # blue
            self.button_grid.addWidget(buttons[2], 1, 0)  # yellow
            self.button_grid.addWidget(buttons[3], 1, 1)  # green

    def set_result(self, correct_index, selected_index):
        self.correct_index = correct_index
        self.selected_index = selected_index

        for i, btn in enumerate(self.answer_buttons):
            bg, hover, click, text = btn._base

            btn.setEnabled(False)
            original_text = self.answers[i]

            if i == correct_index:
                btn.setText(f"✔ {original_text}")
                btn._glow.setBlurRadius(20)
                btn.setStyleSheet(self._style_button(bg, hover, click, text))
                continue

            if i == selected_index:
                btn.setText(f"✖ {original_text}")
                darker = darken_color(bg, 0.8)
                btn.setStyleSheet(self._style_button(darker, darker, darker, text))
                continue

            btn.setText(original_text)
            darker = darken_color(bg, 0.6)
            btn.setStyleSheet(self._style_button(darker, darker, darker, text))

    def reset_buttons(self):
        for btn in self.answer_buttons:
            bg, hover, click, text = btn._base

            btn.setEnabled(True)
            btn.setStyleSheet(self._style_button(bg, hover, click, text))
            btn._glow.setBlurRadius(0)

    def _style_button(self, bg, hover, click, text):
        font_size = 20 if self.mode == "result" else 22
        margin = 3 if self.mode == "result" else 6

        return f"""
            QPushButton {{
                background-color: {bg};
                color: {text};
                border: none;
                border-radius: 14px;
                padding: 18px;
                margin: {margin}px;
                font-size: {font_size}px;
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

        if self.mode == "live":
            button.setCursor(Qt.CursorShape.PointingHandCursor)

        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(0.1)  # to fix bug with buttons sometimes not rendering
        glow.setOffset(0, 0)
        glow.setColor(QColor(bg))
        button.setGraphicsEffect(glow)

        button._base = (bg, hover_bg, click_bg, "white")
        button._glow = glow

        button.setStyleSheet(self._style_button(*button._base))
        button.clicked.connect(lambda _, b=button: self.on_answer_clicked(b))

        return button

    def on_answer_clicked(self, selected):
        if self.mode != "live":
            return

        index = self.answer_buttons.index(selected)
        self.answer_select.emit(index)

        for btn in self.answer_buttons:
            btn.setEnabled(False)
            btn._glow.setBlurRadius(0)

            bg, hover, click, text = btn._base

            if btn is selected:
                # TODO fix cutoff of glow effect
                btn.setStyleSheet(self._style_button(bg, hover, click, text))
                btn._glow.setBlurRadius(50)
            else:
                dim = darken_color(bg, 0.8)
                btn.setStyleSheet(self._style_button(dim, dim, dim, "white"))
