from PyQt6.QtWidgets import QComboBox, QCompleter
from PyQt6.QtCore import Qt


class SearchableCombobox(QComboBox):
    """Searchable dropdown menu."""

    def __init__(self, items: list[str], parent=None) -> None:
        super().__init__(parent)
        self.items = items

        self.setup_component()

    def setup_component(self) -> None:
        self.setEditable(True)

        # Ensures the item does not get added as a new selectable item
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.setMaxVisibleItems(10)

        if self.items:
            self.addItems(self.items)

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
