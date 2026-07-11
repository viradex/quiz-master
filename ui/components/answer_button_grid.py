from dataclasses import dataclass
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


@dataclass
class AnswerButtonData:
    """Represents the data stored in a single answer button."""

    button: QPushButton
    glow: QGraphicsDropShadowEffect

    bg: str
    hover: str
    click: str
    text: str

    def get_all(
        self,
    ) -> tuple[QPushButton, QGraphicsDropShadowEffect, str, str, str, str]:
        return self.button, self.glow, self.bg, self.hover, self.click, self.text


class AnswerButtonGrid(QWidget):
    """Class to manage showing an answer button grid, for multiple views."""

    answer_select = pyqtSignal(int)

    def __init__(self, mode: str, parent: QWidget | None = None) -> None:
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
        self.answer_buttons: list[AnswerButtonData] = []

        self.correct_index: int | None = None
        self.selected_index: int | None = None

        self.button_colors: dict[str, dict[str, str]] = {
            "red": {"normal": "#C94F4F", "hover": "#D45B5B", "click": "#A94444"},
            "blue": {"normal": "#4A78C2", "hover": "#5A86CC", "click": "#3D66A8"},
            "yellow": {"normal": "#B89B2E", "hover": "#C5A83A", "click": "#9E8424"},
            "green": {"normal": "#3E9B68", "hover": "#4AA977", "click": "#347F56"},
        }

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

    def set_result(self, correct_index: int, selected_index: int) -> None:
        """Set correct and selected answer for button grid. Can only be run if the mode is `"result"`."""
        if self.mode != "result":
            raise ValueError("mode must be 'result' to run set_result()")

        self.correct_index = correct_index
        self.selected_index = selected_index

        for i, data in enumerate(self.answer_buttons):
            btn, glow, bg, hover, click, text = data.get_all()

            btn.setEnabled(False)
            original_text = self.answers[i]

            # Correct button
            if i == correct_index:
                btn.setText(f"✔ {original_text}")
                glow.setBlurRadius(20)
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
            darker = darken_color(bg, factor=0.6)
            btn.setStyleSheet(self._style_button(darker, darker, darker, text))

    def reset_buttons(self) -> None:
        """Reset button styling and enable all buttons."""
        for data in self.answer_buttons:
            btn, glow, bg, hover, click, text = data.get_all()

            btn.setEnabled(True)
            btn.setStyleSheet(self._style_button(bg, hover, click, text))
            glow.setBlurRadius(0.1)

    def on_answer_clicked(self, selected: QPushButton) -> None:
        """Emits a signal for the button that was clicked, when a button is clicked."""
        if self.mode != "live":
            return

        index = next(
            i for i, data in enumerate(self.answer_buttons) if data.button is selected
        )
        self.answer_select.emit(index)

        # Disable all buttons once submitted
        for data in self.answer_buttons:
            btn, glow, bg, hover, click, text = data.get_all()

            btn.setEnabled(False)
            glow.setBlurRadius(0.1)

            # Highlight selected button
            if btn is selected:
                btn.setStyleSheet(self._style_button(bg, hover, click, text))
                glow.setBlurRadius(50)
            else:
                dim = darken_color(bg, 0.8)
                btn.setStyleSheet(self._style_button(dim, dim, dim, "white"))

    def _build_buttons(self) -> list[AnswerButtonData]:
        """Create all buttons and return them as a list."""
        self.answer_buttons.clear()
        color_names = ["red", "blue", "yellow", "green"]

        for i, answer in enumerate(self.answers):
            color_name = color_names[i]

            # If server mode, buttons are unclickable, so make
            # all states the same 'normal' state
            if self.mode == "server":
                btn = self._create_answer_button(
                    answer,
                    self.button_colors[color_name]["normal"],
                    self.button_colors[color_name]["normal"],
                    self.button_colors[color_name]["normal"],
                )
            else:
                btn = self._create_answer_button(
                    answer,
                    self.button_colors[color_name]["normal"],
                    self.button_colors[color_name]["hover"],
                    self.button_colors[color_name]["click"],
                )

            self.answer_buttons.append(btn)

        return self.answer_buttons

    def _place_buttons(self, buttons: list[AnswerButtonData]) -> None:
        """Place buttons in a certain order and layout depending on the count."""
        self._clear_layout()
        count = len(buttons)

        if count == 2:
            self.button_grid.addWidget(buttons[0].button, 0, 0, 2, 1)  # red
            self.button_grid.addWidget(buttons[1].button, 0, 1, 2, 1)  # blue
        elif count == 3:
            self.button_grid.addWidget(buttons[0].button, 0, 0)  # red
            self.button_grid.addWidget(buttons[1].button, 0, 1)  # blue
            self.button_grid.addWidget(buttons[2].button, 1, 0, 1, 2)  # yellow
        elif count == 4:
            self.button_grid.addWidget(buttons[0].button, 0, 0)  # red
            self.button_grid.addWidget(buttons[1].button, 0, 1)  # blue
            self.button_grid.addWidget(buttons[2].button, 1, 0)  # yellow
            self.button_grid.addWidget(buttons[3].button, 1, 1)  # green

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
    ) -> AnswerButtonData:
        """Create a single answer button with styling."""
        button = QPushButton(text)
        button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # If button clickable, show respective cursor to denote clickability
        if self.mode == "live":
            button.setCursor(Qt.CursorShape.PointingHandCursor)

        # NOTE Due to weird rendering issues, when setting the glow to 0 you must set it to 0.1:
        # glow.setBlurRadius(0.1) - this applies to the whole class!
        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(0.1)
        glow.setOffset(0, 0)
        glow.setColor(QColor(bg))
        button.setGraphicsEffect(glow)

        data = AnswerButtonData(
            button=button,
            glow=glow,
            bg=bg,
            hover=hover_bg,
            click=click_bg,
            text="white",
        )

        button.setStyleSheet(
            self._style_button(data.bg, data.hover, data.click, data.text)
        )

        button.clicked.connect(lambda _, b=button: self.on_answer_clicked(b))
        return data

    def _clear_layout(self) -> None:
        """Reset the layout in the button grid."""
        while self.button_grid.count():
            item = self.button_grid.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
