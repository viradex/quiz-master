from PyQt6.QtWidgets import (
    QPushButton,
    QWidget,
    QGridLayout,
    QSizePolicy,
    QGraphicsDropShadowEffect,
)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt, pyqtSignal

from utils.color import darken_color


# TODO code is all-over-the-place, and it's obvious that it
# was changed as the code progressively got complex rather than
# improving core design of the class, maybe improve it later?
# like adding a ButtonStyle dataclass, for instance
class AnswerButtonGrid(QWidget):
    """Class to manage showing an answer button grid, for multiple views."""

    BUTTON_COLORS: dict[str, dict[str, str]] = {
        "red": {"normal": "#C94F4F", "hover": "#D45B5B", "click": "#A94444"},
        "blue": {"normal": "#4A78C2", "hover": "#5A86CC", "click": "#3D66A8"},
        "yellow": {"normal": "#B89B2E", "hover": "#C5A83A", "click": "#9E8424"},
        "green": {"normal": "#3E9B68", "hover": "#4AA977", "click": "#347F56"},
    }

    answer_select = pyqtSignal(int)

    def __init__(self, mode: str, parent=None) -> None:
        """
        The `mode` determines the type of answer button grid.

        Possible values are:
        - `"live"` - Player can answer
        - `"server"` - Display only
        - `"result"` - Show correct/incorrect answers
        """

        super().__init__(parent)
        self.mode: str = mode

        self.answers: list[str] = []
        self.correct_index: int | None = None
        self.selected_index: int | None = None

        self.setup_grid()
        self.setup_buttons()

    def set_answers(self, answers: list[str]) -> None:
        """Set answers for buttons, and re-displays the buttons. Only 2-4 answers accepted."""
        if not 2 <= len(answers) <= 4:
            raise ValueError(f"Expected between 2-4 answers, received {len(answers)}")

        self.answers = answers
        self.setup_buttons()

    def setup_grid(self) -> None:
        self.button_grid = QGridLayout()
        self.button_grid.setColumnStretch(0, 1)
        self.button_grid.setColumnStretch(1, 1)
        self.button_grid.setRowStretch(0, 1)
        self.button_grid.setRowStretch(1, 1)

        self.setLayout(self.button_grid)

    def setup_buttons(self) -> None:
        buttons = self._build_buttons()
        self._place_buttons(buttons)

    def _build_buttons(self) -> list[QPushButton]:
        self.answer_buttons = []
        color_names = ["red", "blue", "yellow", "green"]

        for i, answer in enumerate(self.answers):
            color_name = color_names[i]

            # If server mode, buttons are unclickable, so make
            # all states the same 'normal' state
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

    def _place_buttons(self, buttons: list[QPushButton]) -> None:
        """Place buttons in a certain order and layout depending on the count."""
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

    def set_result(self, correct_index: int, selected_index: int) -> None:
        """Set correct and selected answer for button grid. Can only be run if the mode is `"result"`."""
        if self.mode != "result":
            raise ValueError("mode must be 'result' to run set_result()")

        self.correct_index = correct_index
        self.selected_index = selected_index

        for i, btn in enumerate(self.answer_buttons):
            bg, hover, click, text = btn._base

            btn.setEnabled(False)
            original_text = self.answers[i]

            # Correct button
            if i == correct_index:
                btn.setText(f"✔ {original_text}")
                btn._glow.setBlurRadius(20)
                btn.setStyleSheet(self._style_button(bg, hover, click, text))
                continue

            # Incorrect button, if not correct
            if i == selected_index:
                btn.setText(f"✖ {original_text}")
                darker = darken_color(bg, 0.8)
                btn.setStyleSheet(self._style_button(darker, darker, darker, text))
                continue

            # Other buttons
            btn.setText(original_text)
            darker = darken_color(bg, 0.6)
            btn.setStyleSheet(self._style_button(darker, darker, darker, text))

    def reset_buttons(self) -> None:
        """Reset button styling and enable all buttons."""
        for btn in self.answer_buttons:
            bg, hover, click, text = btn._base

            btn.setEnabled(True)
            btn.setStyleSheet(self._style_button(bg, hover, click, text))
            btn._glow.setBlurRadius(0)

    def _style_button(self, bg: str, hover: str, click: str, text: str) -> str:
        """Style an individual answer button, and return the QSS for it."""
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

    def _create_answer_button(
        self, text: str, bg: str, hover_bg: str, click_bg: str
    ) -> QPushButton:
        """Create a single answer button with styling."""
        button = QPushButton(text)
        button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # If button clickable, show respective cursor to denote clickability
        if self.mode == "live":
            button.setCursor(Qt.CursorShape.PointingHandCursor)

        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(0.1)  # to fix bug with buttons sometimes not rendering
        glow.setOffset(0, 0)
        glow.setColor(QColor(bg))
        button.setGraphicsEffect(glow)

        # TODO this is a bit of a smell :/
        button._base = (bg, hover_bg, click_bg, "white")
        button._glow = glow

        button.setStyleSheet(self._style_button(*button._base))
        button.clicked.connect(lambda _, b=button: self.on_answer_clicked(b))

        return button

    def on_answer_clicked(self, selected: QPushButton) -> None:
        """Emits a signal for the button that was clicked, when a button is clicked."""
        if self.mode != "live":
            return

        index = self.answer_buttons.index(selected)
        self.answer_select.emit(index)

        # Disable all buttons once submitted
        for btn in self.answer_buttons:
            btn.setEnabled(False)
            btn._glow.setBlurRadius(0)

            bg, hover, click, text = btn._base

            # Highlight selected button
            if btn is selected:
                # TODO fix cutoff of glow effect
                btn.setStyleSheet(self._style_button(bg, hover, click, text))
                btn._glow.setBlurRadius(50)
            else:
                dim = darken_color(bg, 0.8)
                btn.setStyleSheet(self._style_button(dim, dim, dim, "white"))
