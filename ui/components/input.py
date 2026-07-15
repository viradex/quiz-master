from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFocusEvent, QKeyEvent, QMouseEvent, QWheelEvent
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QComboBox,
    QSpinBox,
    QGridLayout,
    QCompleter,
)


class ClickableLabel(QLabel):
    """Create a clickable QLabel, which emits a 'clicked' signal when pressed."""

    clicked = pyqtSignal()

    def __init__(self, text: str = "", parent=None) -> None:
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Called automatically by PyQt when the widget is clicked."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

        super().mousePressEvent(event)


class FocusLineEdit(QLineEdit):
    """Create a QLineEdit, which emits a 'focused' signal when its focus state is toggled (True if focus given, else False)."""

    focused = pyqtSignal(bool)

    def focusInEvent(self, event: QFocusEvent) -> None:
        """Called automatically by PyQt when the widget is focused."""
        self.focused.emit(True)
        super().focusInEvent(event)

    def focusOutEvent(self, event: QFocusEvent) -> None:
        """Called automatically by PyQt when the widget is unfocused."""
        self.focused.emit(False)
        super().focusOutEvent(event)


class CharacterCountInput(QWidget):
    """
    Create an input box with a character counter at the top-right corner, showing a live counter
    of characters entered out of maximum characters. If the characters entered exceeds the maximum characters,
    the label turns red, but the user is still allowed to continue typing. This does not enforce the number of characters
    through validation; this must be done separately.
    """

    def __init__(self, max_length: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.max_length = max_length

        self.setup_component()

    def setup_component(self) -> None:
        self.line_edit = FocusLineEdit()
        self.line_edit.focused.connect(self._on_focus_changed)

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

        # Put both widgets on same cell in grid to overlap
        grid = QGridLayout(self)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(0)
        grid.addWidget(self.line_edit, 0, 0)
        grid.addWidget(
            self.counter,
            0,
            0,
            alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight,
        )

        self.line_edit.textChanged.connect(self._update_count)
        self._update_count(self.line_edit.text())

    def _update_count(self, text: str) -> None:
        """Update the counter at the top-right corner with the total characters in the input field
        out of the maximum characters allowed. Turns red if it exceeds the limit."""
        length = len(text.strip())

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
        """Shows the counter label if the input is focused or the character count exceeds the max, else hides it."""
        if focused or len(self.line_edit.text().strip()) > self.max_length:
            self.counter.show()
        else:
            self.counter.hide()


class SearchableCombobox(QComboBox):
    """Searchable dropdown menu."""

    def __init__(
        self, items: list[str] | None = None, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.items = list(items) if items is not None else []

        self.setup_component()

    def setup_component(self) -> None:
        self.setEditable(True)

        # Ensures the item does not get added as a new selectable item
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.setMaxVisibleItems(10)

        if self.items:
            self.addItems(self.items)
            self.setCurrentIndex(-1)  # Select no value when starting

        # QCompleter for search functionality
        completer = QCompleter(self.model(), self)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)

        self.setCompleter(completer)

    def set_items(self, items: list[str]) -> None:
        """Set a new set of items for the dropdown."""
        self.items = items

        self.clear()
        self.addItems(self.items)

        # Deselect everything
        self.setCurrentIndex(-1)


class ReversedSpinBox(QSpinBox):
    """
    Reverses the effects of normally using the keyboard keys or mouse scroll wheel to change the
    value of a spin box. Pressing down, or scrolling down, increases the value, and vice versa for upwards.
    """

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Called automatically by PyQt when a keyboard key is pressed."""
        # Pressing up goes down instead and vice versa
        if event.key() == Qt.Key.Key_Up:
            self.setValue(min(self.value() - 1, self.maximum()))
            event.accept()
        elif event.key() == Qt.Key.Key_Down:
            self.setValue(min(self.value() + 1, self.maximum()))
            event.accept()
        else:
            super().keyPressEvent(event)

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Called automatically by PyQt when the mouse scroll wheel is used."""
        # Scrolling up acts as if it scrolls down and vice versa
        if event.angleDelta().y() > 0:
            self.setValue(max(self.minimum(), self.value() - 1))
        elif event.angleDelta().y() < 0:
            self.setValue(min(self.maximum(), self.value() + 1))

        event.accept()
