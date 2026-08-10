"""
input.py

Contains widgets that are slightly customized versions of pre-made Qt input-based widgets.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFocusEvent, QKeyEvent, QMouseEvent, QWheelEvent
from PyQt6.QtWidgets import (
    QComboBox,
    QCompleter,
    QGridLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QWidget,
)


class ClickableLabel(QLabel):
    """
    Creates a regular clickable `QLabel` that emits a 'clicked' event signal when left-clicked like a
    button. Inherits `QLabel`.

    Attributes:
        clicked: A `pyqtSignal` that emits when the label is left-clicked with the mouse. No arguments are
            provided.

    Arguments:
        text: The text to display on the label, or None to set no text. Defaults to None.

        parent: The parent to make this label a child of, or None to set no parent. Defaults to None.
    """

    clicked = pyqtSignal()

    def __init__(self, text: str | None = None, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)

        # Sets cursor to hand to signify to user that it can be clicked
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Called automatically by PyQt when the widget is clicked by the mouse. Checks if the left mouse button
        was clicked, and if so, emits the signal.

        Arguments:
            event: An argument passed automatically by PyQt upon this method being run, to detect the type of
                mouse button pressed.

        Returns:
            None.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

        super().mousePressEvent(event)


class FocusLineEdit(QLineEdit):
    """
    Creates a regular `QLineEdit` that emits a 'focused' event signal when the widget gets or loses focus.
    Inherits `QLineEdit`.

    Attributes:
        focused: A `pyqtSignal` that emits when the input gets or loses focus. An argument is provided that
            determines whether the input lost or got focus (True if focus was received, False if focus was
            lost). A boolean is used as it works well for these binary states.

    Arguments:
        text: The text to display on the label, or None to set no text. Defaults to None.

        parent: The parent to make this label a child of, or None to set no parent. Defaults to None.
    """

    focused = pyqtSignal(bool)

    def focusInEvent(self, event: QFocusEvent) -> None:
        """
        Called automatically by PyQt when the widget receives focus. Emits the 'focused' signal with True.

        Arguments:
            event: An argument passed automatically by PyQt upon this method being run.

        Returns:
            None.
        """
        self.focused.emit(True)
        super().focusInEvent(event)

    def focusOutEvent(self, event: QFocusEvent) -> None:
        """
        Called automatically by PyQt when the widget loses focus. Emits the 'focused' signal with False.

        Arguments:
            event: An argument passed automatically by PyQt upon this method being run.

        Returns:
            None.
        """
        self.focused.emit(False)
        super().focusOutEvent(event)


class CharacterCountLineEdit(QWidget):
    """
    Creates an input box with a character counter at the top-right corner, showing a live counter
    of characters entered out of the maximum characters permitted. If the characters entered exceeds
    the maximum characters, the label turns red, but the user is still allowed to continue typing.
    This does not enforce the number of characters through validation; that must be done separately.

    As this widget inherits `QWidget` instead of `QLineEdit`, when wanting to edit the properties of the
    line edit used internally in this widget, you must use the `line_edit` property. For example:

        character_count.line_edit.setPlaceholderText("Placeholder!")

    Arguments:
        max_length: The maximum number of characters permitted in the input widget. As stated above, this
            simply changes the character count label; it does not restrict the number of characters. An
            integer is used as it is a whole number that represents the number of characters well.

        parent: The parent to make this widget a child of, or None to set no parent. Defaults to None.
    """

    def __init__(self, max_length: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.max_length: int = max_length

        self._setup_component()

    def _setup_component(self) -> None:
        """
        Internal method. Sets up the component UI, such as widgets and layouts. This method should only be
        called once, preferably in the initialization logic.

        Returns:
            None.
        """
        # This attribute is intended to be called outside the class to change
        # attributes relating to the line edit, such as placeholder text.
        self.line_edit = FocusLineEdit()
        self.line_edit.focused.connect(self._on_focus_changed)
        self.line_edit.textChanged.connect(self._update_count)

        # Counter label that overlaps the line edit, hidden by default
        self.counter = QLabel()
        self.counter.hide()
        self.counter.setProperty("state", "normal")
        self.counter.setStyleSheet("""
            QLabel[state="normal"] {
                color: #A0A0A0;
                font-size: 12px;
                padding-right: 4px;
                padding-top: 2px;
                background: transparent;
            }

            QLabel[state="error"] {
                color: #C75A5A;
                font-size: 12px;
                padding-right: 4px;
                padding-top: 2px;
                background: transparent;
            }
        """)

        self._update_count(self.line_edit.text())

        # Put both widgets on same cell in grid to overlap, with the counter
        # overlapping the line edit at the top-right corner.
        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(0)
        grid.addWidget(self.line_edit, 0, 0)
        grid.addWidget(
            self.counter,
            0,
            0,
            alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight,
        )

        self.setLayout(grid)

    def _update_count(self, text: str) -> None:
        """
        Internal method. Update the counter at the top-right corner with the total characters in the input field
        out of the maximum characters allowed. Turns red if it exceeds the limit. Strips the text before counting
        its length.

        Arguments:
            text: A string with the new text in the input field, to calculate the characters of. A string is used
                as it can be used to easily store several characters.

        Returns:
            None.
        """
        length = len(text.strip())

        # Set label text and update styles depending on if it exceeds the max length or not
        self.counter.setText(f"{length}/{self.max_length}")
        self.counter.setProperty(
            "state",
            "error" if length > self.max_length else "normal",
        )

        # Update styles
        self.counter.style().unpolish(self.counter)
        self.counter.style().polish(self.counter)
        self.counter.update()

    def _on_focus_changed(self, focused: bool) -> None:
        """
        Internal method. Shows the counter label if the input is focused or the character count exceeds the
        maximum limit (even if it is unfocused), else hides it.

        Arguments:
            focused: Whether or not the input field is focused or not. A boolean is used as this is a binary value,
                where it can only be True or False.

        Returns:
            None.
        """
        if focused or len(self.line_edit.text().strip()) > self.max_length:
            self.counter.show()
        else:
            self.counter.hide()


class SearchableCombobox(QComboBox):
    """
    Creates a searchable drop-down menu, inheriting `QComboBox`. The searching functionality is case-insensitive
    and checks if it contains the search query. The search is based off of the list of items provided, not the items
    in the dropdown.

    Arguments:
        items: The list of items to base the search off of. A list is used as it groups similar values together in an
            iterable object.

        parent: The parent to make this combobox a child of, or None to set no parent. Defaults to None.
    """

    def __init__(
        self, items: list[str] | None = None, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.items: list[str] = items if items is not None else []

        self._setup_component()

    def _setup_component(self) -> None:
        """
        Internal method. Sets up the component UI, such as widgets. This method should only be called once,
        preferably in the initialization logic.

        Returns:
            None.
        """
        # Allows combobox to be edited to allow search to work
        self.setEditable(True)

        # Ensures any custom typed item does not get added as a new selectable item
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.setMaxVisibleItems(10)

        if self.items:
            self.addItems(self.items)

            # Select no value when starting
            self.setCurrentIndex(-1)

        # QCompleter for search functionality, case-insensitive and contains match search
        completer = QCompleter(self.model(), self)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)

        self.setCompleter(completer)

    def set_items(self, items: list[str]) -> None:
        """
        Replace the existing list of items for the search functionality with a new list, and deselects any
        item selected.

        Arguments:
            items: The list of items to base the search off of, and to add to the dropdown selection.
                A list is used as it groups similar values together in an iterable object.

        Returns:
            None.
        """
        self.items = items

        # Refreshes items in the dropdown itself
        self.clear()
        self.addItems(self.items)

        # Deselect any existing selected item
        self.setCurrentIndex(-1)


class ReversedSpinBox(QSpinBox):
    """
    Creates a reversed version of a `QSpinBox`, which reverses the effect of the keyboard arrow keys and the
    mouse scroll wheel. For example, pressing the up arrow decreases the value, and the down arrow increases
    the value. Also, scrolling the mouse wheel up decreases the value, and scrolling it down increases the value.

    The arguments for this class are the same as a regular `QSpinBox`, as this class inherits `QSpinBox`.
    """

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """
        Called automatically by PyQt when a keyboard key is pressed while the widget is focused. If the up arrow
        key is pressed, decreases the value by 1. If the down arrow key is pressed, increases the value by 1. All
        other keys are delegated to the spinbox's default handling for the key.

        Arguments:
            event: An argument passed automatically by PyQt upon this method being run, to detect the type of
                keyboard key pressed.

        Returns:
            None.
        """
        if event.key() == Qt.Key.Key_Up:
            # Decreases current value, ensuring it does not go below the set minimum
            self.setValue(max(self.minimum(), self.value() - 1))
        elif event.key() == Qt.Key.Key_Down:
            # Increases current value, ensuring it does not go above the set maximum
            self.setValue(min(self.maximum(), self.value() + 1))
        else:
            # Other keys are delegated to their default handling by QSpinBox
            super().keyPressEvent(event)

    def wheelEvent(self, event: QWheelEvent) -> None:
        """
        Called automatically by PyQt when the mouse wheel is scrolled while the cursor is hovered over the widget.
        If the mouse wheel is scrolled up, it decreases the value by 1. Otherwise, if it is scrolled down, it
        increases the value by 1.

        Arguments:
            event: An argument passed automatically by PyQt upon this method being run, to detect the direction
                that the mouse wheel was scrolled in.

        Returns:
            None.
        """
        if event.angleDelta().y() > 0:
            # Decreases current value, ensuring it does not go below the set minimum
            self.setValue(max(self.minimum(), self.value() - 1))
        elif event.angleDelta().y() < 0:
            # Increases current value, ensuring it does not go above the set maximum
            self.setValue(min(self.maximum(), self.value() + 1))

        # Informs Qt that the event has been handled, preventing more code from
        # running and potentially reversing the effects of this code above.
        event.accept()
