from PyQt6.QtWidgets import QComboBox, QCompleter
from PyQt6.QtCore import Qt


class SearchableCombobox(QComboBox):
    def __init__(self, items, parent=None):
        super().__init__(parent)
        self.items = items

        self.setEditable(True)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.setMaxVisibleItems(10)

        if self.items:
            self.addItems(self.items)

        completer = QCompleter(self.model(), self)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)

        self.setCompleter(completer)

    def set_all_items(self, items):
        self.items = items

        self.clear()
        self.addItems(self.items)
