from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QComboBox,
    QSpinBox,
    QCompleter,
    QGridLayout,
)
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtCore import Qt, pyqtSignal


class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def __init__(self, text: str = "", parent=None) -> None:
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

        super().mousePressEvent(event)


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

        self.setCurrentIndex(-1)


class ReversedSpinBox(QSpinBox):
    def keyPressEvent(self, event):
        # Pressing up goes down instead and vice versa
        if event.key() == Qt.Key.Key_Up:
            self.setValue(min(self.value() - 1, self.maximum()))
            event.accept()
        elif event.key() == Qt.Key.Key_Down:
            self.setValue(min(self.value() + 1, self.maximum()))
            event.accept()
        else:
            super().keyPressEvent(event)

    def wheelEvent(self, event):
        # Scrolling up acts as if it scrolls down and vice versa
        if event.angleDelta().y() > 0:
            self.setValue(max(self.minimum(), self.value() - 1))
        elif event.angleDelta().y() < 0:
            self.setValue(min(self.maximum(), self.value() + 1))

        event.accept()
