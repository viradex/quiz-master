"""
answer_button_grid.py

The answer button grid component. Used to display a grid of answer buttons for various situations,
such as to display the correct answer or to allow the answer to select an answer.
"""

from dataclasses import dataclass

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QGridLayout, QSizePolicy, QWidget

from core.app.enums import AnswerButtonGridMode
from ui.components.button import WordWrapButton
from utils.color import darken_color

# Define the button colors used, as well as the colors to use during different states
BUTTON_COLORS: dict[str, dict[str, str]] = {
    "red": {"normal": "#C94F4F", "hover": "#D45B5B", "click": "#A94444"},
    "blue": {"normal": "#4A78C2", "hover": "#5A86CC", "click": "#3D66A8"},
    "yellow": {"normal": "#B89B2E", "hover": "#C5A83A", "click": "#9E8424"},
    "green": {"normal": "#3E9B68", "hover": "#4AA977", "click": "#347F56"},
}


@dataclass
class _AnswerButtonData:
    """
    Internal class. Represents the data stored in a single answer button.

    Arguments:
        button: The `WordWrapButton` that this class represents.

        glow: The `QGraphicsDropShadowEffect` to use when wanting to set a glow to the button.

        bg: The regular background color of the button, as a hex code. A string is used as it easily
            represents hex codes.

        hover: The hovered background color of the button, as a hex code. A string is used as it easily
            represents hex codes.

        click: The clicked background color of the button, as a hex code. A string is used as it easily
            represents hex codes.

        text: The regular text color of the button, as a hex code. A string is used as it easily represents
            hex codes.
    """

    button: WordWrapButton
    glow: QGraphicsDropShadowEffect

    bg: str
    hover: str
    click: str
    text: str

    def get_all(
        self,
    ) -> tuple[WordWrapButton, QGraphicsDropShadowEffect, str, str, str, str]:
        """
        Get all data stored in the class as a tuple, for easier unpacking and less code when trying to access
        all the attributes of the class.

        The return value is a tuple with values in the following order. The details of what these attributes
        contain is discussed in more detail in the class docstring.
        - button (`WordWrapButton`)
        - glow (`QGraphicsDropShadowEffect`)
        - bg (`str`)
        - hover (`str`)
        - click (`str`)
        - text (`str`)

        Returns:
            A tuple containing all the data stored in this class, in the order described above. A tuple is
            returned as it allows for easier unpacking.
        """
        return self.button, self.glow, self.bg, self.hover, self.click, self.text


# NOTE Due to weird rendering issues, when wanting to remove the glow by setting
# it to 0, you must set it to 0.1 instead:
#
#   glow.setBlurRadius(0.1)
#
# This applies to the whole class!
class AnswerButtonGrid(QWidget):
    """
    Creates the answer button grid, inheriting `QWidget`.

    Used to show a bunch of answer buttons in a grid, in different modes depending on the context the component
    is used in. For example, in a results screen, the button grid will show the answer.

    Attributes:
        answer_select: A `pyqtSignal` that emits when a button is selected and the component is in live mode.
            The answer button zero-based index selected is provided as an integer argument.

    Arguments:
        mode: The AnswerButtonGridMode that the component should be in. The mode should not be changed after
            creation. A specialized Enum is used to prevent typos with using strings, and allow more
            self-documenting code.

        parent: The parent of this screen, or None.
    """

    # Zero-based index representing the answer button selected
    # e.g. Yellow button, or answer button C, gives 2
    answer_select = pyqtSignal(int)

    def __init__(
        self, mode: AnswerButtonGridMode, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.mode = mode

        # Initialize empty answer text and answer buttons
        self.answers: list[str] = []
        self.answer_buttons: list[_AnswerButtonData] = []

        # Only for results mode
        self.correct_index: int | None = None
        self.selected_index: int | None = None

        self._setup_grid()
        self._setup_buttons()

    def set_answers(self, answers: list[str]) -> None:
        """
        Set the answer text for the buttons, and re-displays the buttons. Only 2-4 answers are expected.
        The number of answers provided directly influences the number of answer buttons displayed on the UI.

        Arguments:
            answers: A list of answer button text to display to the user. The length must be between 2-4 answers.
                A list is used as it is an ordered collection of related data values, which suits its use case
                here.

        Returns:
            None.

        Raises:
            ValueError: If the number of answers provided does not satisfy the range of 2-4 answers, inclusive.
        """
        if not 2 <= len(answers) <= 4:
            raise ValueError(f"Expected between 2-4 answers, received {len(answers)}")

        self.answers = answers
        self._setup_buttons()

    def set_result(self, correct_index: int, selected_index: int | None = None) -> None:
        """
        Set the correct and selected answer for the button grid. The selected answer can be hidden by setting it
        or leaving it as None. This method can only be run if the mode is set to result mode, and should only
        be called after `set_answers()`.

        Arguments:
            correct_index: The correct answer button to highlight. The index is zero-based, and must be within
                a valid range of 0 to the number of answers. An integer is used as it can easily be used to
                recognize the answer button at a point.

            selected_index: The selected answer button to highlight. The index is zero-based, and must be within
                a valid range of 0 to the number of answers. The value can also be None, in which case it will
                be set to the same value as the correct index. This is useful for a server-side results display,
                for example. An integer is used as it can easily be used to recognize the answer button at a point.
                Default is None.

        Returns:
            None.

        Raises:
            RuntimeError: If the mode is not set to result.

            ValueError: If either the correct index and/or the selected index is not in the valid range of 0 to
                the number of answers provided beforehand minus one.
        """
        if self.mode is not AnswerButtonGridMode.RESULT:
            raise RuntimeError(
                f"The mode must be {AnswerButtonGridMode.RESULT} to run set_result()"
            )

        num_answers = len(self.answers)

        # Assuming there are 4 answers for this code example:
        # If the correct index is not between 0-3, and the selected index is
        # not None AND it is not between 0-3, raise exception.
        if not (0 <= correct_index < num_answers) or (
            selected_index is not None and not (0 <= selected_index < num_answers)
        ):
            raise ValueError(
                f"Index out of range, must be between 0-{num_answers - 1}, but received {correct_index} and {selected_index}"
            )

        self.correct_index = correct_index

        # Set selected index to correct index if not set to only highlight correct answer
        self.selected_index = (
            selected_index if selected_index is not None else correct_index
        )

        self._setup_result_buttons()

    def reset_buttons(self) -> None:
        """
        Reset button styling and enables all visible buttons. Does not add or remove any buttons from the grid.

        Returns:
            None.
        """
        for data in self.answer_buttons:
            btn, glow, bg, hover, click, text = data.get_all()

            # Re-enable and reset styling and glow
            btn.setEnabled(True)
            btn.setStyleSheet(self._style_button(bg, hover, click, text))
            glow.setBlurRadius(0.1)

    def _setup_grid(self) -> None:
        """
        Internal method. Sets up the main button grid and its stretch configuration, then sets it as the main
        layout of this component via `setLayout()`.
        """
        self.button_grid = QGridLayout()
        self.button_grid.setColumnStretch(0, 1)
        self.button_grid.setColumnStretch(1, 1)
        self.button_grid.setRowStretch(0, 1)
        self.button_grid.setRowStretch(1, 1)

        self.setLayout(self.button_grid)

    def _setup_buttons(self) -> None:
        """
        Internal method. Sets up all the buttons by building and then placing them in the grid, depending on
        the amount of answers available. The answers property should be filled before running this.

        Returns:
            None.
        """
        buttons = self._build_buttons()
        self._place_buttons(buttons)

    def _setup_result_buttons(self) -> None:
        """
        Internal method. Sets up the buttons to be styled as result buttons. This method should only be run
        once the selected index and correct index are set.

        The correct index button is styled with a large glow and a tick, while the selected answer (which is
        not set if it is the same as the correct index) has a cross and slightly darker color. All other buttons
        are darker.

        Returns:
            None.
        """
        for i, data in enumerate(self.answer_buttons):
            # Get all data about this button
            btn, glow, bg, _hover, _click, text = data.get_all()

            # Disable button for results
            btn.setEnabled(False)
            original_text = self.answers[i]

            # Correct button
            if i == self.correct_index:
                btn.setText(f"✔ {original_text}")
                glow.setBlurRadius(20)
                btn.setStyleSheet(self._style_button(bg, bg, bg, text))
                continue

            # Incorrect button, if not correct
            if i == self.selected_index:
                btn.setText(f"✖ {original_text}")
                darker = darken_color(bg, factor=0.2)
                btn.setStyleSheet(self._style_button(darker, darker, darker, text))
                continue

            # Other buttons
            btn.setText(original_text)
            darker = darken_color(bg, factor=0.4)
            btn.setStyleSheet(self._style_button(darker, darker, darker, text))

    def _build_buttons(self) -> list[_AnswerButtonData]:
        """
        Internal method. Create the individual buttons with respective styling, and return them as a list of
        button data. Also sets `self.answer_buttons` to contain these buttons in order. Only creates the number
        of buttons as there are answers.

        Returns:
            A list containing all of the buttons as answer button data, ordered in the order that they were inserted.
            A list is used as it is an ordered collection and groups the similar data together.
        """
        self.answer_buttons.clear()
        color_names = ["red", "blue", "yellow", "green"]

        # Cycle through all answers and exit early if answers have run out
        for answer, color_name in zip(self.answers, color_names):
            # If server mode, buttons are disabled, so make all states the same 'normal' state
            if self.mode is AnswerButtonGridMode.SERVER:
                btn = self._create_answer_button(
                    answer,
                    BUTTON_COLORS[color_name]["normal"],
                    BUTTON_COLORS[color_name]["normal"],
                    BUTTON_COLORS[color_name]["normal"],
                )
            else:
                btn = self._create_answer_button(
                    answer,
                    BUTTON_COLORS[color_name]["normal"],
                    BUTTON_COLORS[color_name]["hover"],
                    BUTTON_COLORS[color_name]["click"],
                )

            self.answer_buttons.append(btn)

        return self.answer_buttons

    def _place_buttons(self, buttons: list[_AnswerButtonData]) -> None:
        """
        Internal method. Adds the buttons provided into the grid layout, differently depending on the amount of
        buttons provided. Clears the layout before adding the buttons.

        If there are two buttons, the buttons are placed side-by-side. If there are three buttons, the first two
        buttons are placed normally at the top, but the third button stretches to fill the final horizontal section.
        If there are four buttons, they are placed in a normal 2x2 grid.

        Arguments:
            buttons: A list of buttons to add to the layout, in order. A list is used as it groups similar values
                and orders them in insertion order.

        Returns:
            None.
        """
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

    def _create_answer_button(
        self, text: str, bg: str, hover_bg: str, click_bg: str
    ) -> _AnswerButtonData:
        """
        Internal method. Creates a single answer button with its data and styling applied, and attaches a clicked
        signal to it. This method does not add it to any layout, however.

        Arguments:
            text: The text to display on the button. A string is used as it works well for any text.

            bg: The normal background of the button, as a hex code. A string is used as it represents hex
                codes well.

            hover_bg: The hover background of the button, as a hex code. A string is used as it represents hex
                codes well.

            click_bg: The clicked background of the button, as a hex code. A string is used as it represents
                hex codes well.

        Returns:
            The button, as well as the glow and extra metadata, as a button data class.
        """
        button = WordWrapButton(text)
        button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # If button clickable, show respective cursor
        if self.mode is AnswerButtonGridMode.LIVE:
            button.setCursor(Qt.CursorShape.PointingHandCursor)

        # Create button with no glow and attach it to the button
        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(0.1)
        glow.setOffset(0, 0)
        glow.setColor(QColor(bg))
        button.setGraphicsEffect(glow)

        # Put button in wrapper class stored with its metadata
        data = _AnswerButtonData(
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

        # Connect signals
        button.clicked.connect(lambda _, b=button: self._on_answer_clicked(b))
        return data

    def _style_button(self, bg: str, hover: str, click: str, text: str) -> str:
        """
        Internal method. Give a QSS stylesheet string containing styling data for the button, depending on
        the arguments passed and the current mode that this component was created using.

        Arguments:
            bg: The normal background of the button, as a hex code. A string is used as it represents hex
                codes well.

            hover_bg: The hover background of the button, as a hex code. A string is used as it represents hex
                codes well.

            click_bg: The clicked background of the button, as a hex code. A string is used as it represents
                hex codes well.

            text: The color of the text to display on the button, as a hex code. A string is used as it represents
                hex codes well.

        Returns:
            The QSS as a string. A string is used as it can represent the QSS well and also works well with
            f-strings.
        """
        # Changes sizes depending on the mode
        font_size = 20 if self.mode is AnswerButtonGridMode.RESULT else 22
        margin = 3 if self.mode is AnswerButtonGridMode.RESULT else 6

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

    def _on_answer_clicked(self, selected: WordWrapButton) -> None:
        """
        Internal method. Intended to be run when an answer button is clicked. Emits a signal that a button was
        clicked with the button's respective zero-based index. Also styles the clicked button and the remaining
        buttons to reflect the state and disables all buttons.

        Attributes:
            selected: The `WordWrapButton` that was clicked by the user. A `WordWrapButton` is used as it can be used
                to identify the exact button location in `self.answer_buttons`.

        Returns:
            None.

        Raises:
            RuntimeError: If the selected button was not found.
        """
        # Buttons can only be clicked in live mode
        if self.mode is not AnswerButtonGridMode.LIVE:
            return

        # Find the index of the button if it matches
        index = next(
            (
                i
                for i, data in enumerate(self.answer_buttons)
                if data.button is selected
            ),
            None,
        )

        # Should never happen under regular operation, as all buttons are created beforehand
        if index is None:
            raise RuntimeError("Selected button not found")

        self.answer_select.emit(index)

        # Disable all buttons once submitted
        for data in self.answer_buttons:
            btn, glow, bg, hover, click, text = data.get_all()

            # Disable all buttons and reset glow
            btn.setEnabled(False)
            glow.setBlurRadius(0.1)

            # Highlight selected button
            if btn is selected:
                btn.setStyleSheet(self._style_button(bg, hover, click, text))
                glow.setBlurRadius(50)
            else:
                dim = darken_color(bg, factor=0.2)
                btn.setStyleSheet(self._style_button(dim, dim, dim, "white"))

    def _clear_layout(self) -> None:
        """
        Removes all the buttons in the grid layout.

        Returns:
            None.
        """
        while self.button_grid.count():
            # Take the next item and delete it
            item = self.button_grid.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
