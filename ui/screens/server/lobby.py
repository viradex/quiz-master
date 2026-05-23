from PyQt6.QtWidgets import (
    QLabel,
    QPushButton,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QHBoxLayout,
    QAbstractItemView,
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from core.screen_ids import Screens
from ui.screens.base_screen import BaseScreen
from ui.components.button import LeaveButton


class ServerLobbyScreen(BaseScreen):
    title_text = "Quiz Master – Lobby"

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setup_ui()

    def setup_ui(self):
        ### LEFT SIDE ###
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)

        title = QLabel("Lobby")
        title.setFont(title_font)

        self.total_players = QLabel("Players: 5 / 16")
        self.total_players.setStyleSheet("font-size: 16px;" "color: #A0A0A0;")

        table_font = QFont()
        table_font.setPointSize(12)

        self.lobby_table = QTableWidget()
        self.lobby_table.setFont(table_font)
        self.lobby_table.setColumnCount(1)
        self.lobby_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.lobby_table.resizeColumnsToContents()

        self.lobby_table.verticalHeader().setVisible(False)
        self.lobby_table.verticalHeader().setDefaultSectionSize(32)
        self.lobby_table.horizontalHeader().setVisible(False)
        self.lobby_table.horizontalHeader().setSectionResizeMode(
            self.lobby_table.horizontalHeader().ResizeMode.Stretch
        )
        self.lobby_table.setStyleSheet("""
            QTableWidget::item {
                padding-left: 10px;
            }
        """)

        self.get_info_btn = QPushButton("Get Info")
        self.get_info_btn.clicked.connect(self.on_get_info)
        self.get_info_btn.setStyleSheet("font-size: 14px;")

        self.kick_btn = QPushButton("Kick Player")
        self.kick_btn.clicked.connect(self.on_kick_player)
        self.kick_btn.setStyleSheet("font-size: 14px;")

        player_btn_hbox = QHBoxLayout()
        player_btn_hbox.addWidget(self.get_info_btn)
        player_btn_hbox.addWidget(self.kick_btn)

        # TODO only for prototype
        data = [
            "Viradex",
            "Peptalker101",
            "TrexGamerGirl",
            "Scyrist",
            "ItsJakePlayz21",
        ]

        for value in data:
            row = self.lobby_table.rowCount()
            self.lobby_table.insertRow(row)

            item = QTableWidgetItem(value)
            item.setTextAlignment(
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
            )

            self.lobby_table.setItem(row, 0, item)

        vbox_left = QVBoxLayout()
        vbox_left.addWidget(title)
        vbox_left.addWidget(self.total_players)
        vbox_left.addSpacing(10)
        vbox_left.addWidget(self.lobby_table, stretch=1)
        vbox_left.addSpacing(2)
        vbox_left.addLayout(player_btn_hbox)
        vbox_left.addStretch()

        ### RIGHT SIDE ###
        ip_font = QFont()
        ip_font.setPointSize(28)

        self.ip_address = QLabel("IP: 192.168.0.2")
        self.ip_address.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ip_address.setFont(ip_font)

        leave_btn = LeaveButton("Close Lobby", btn_width=100)
        leave_btn.confirm_leave.connect(lambda: self.go_to(Screens.COMMON_MENU))

        vbox_right = QVBoxLayout()

        vbox_right.addWidget(self.ip_address)
        vbox_right.addStretch(1)
        vbox_right.addStretch(5)
        vbox_right.addWidget(leave_btn, alignment=Qt.AlignmentFlag.AlignRight)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(100, 50, 20, 20)
        hbox.addLayout(vbox_left, stretch=1)
        hbox.addLayout(vbox_right, stretch=2)

        self.setLayout(hbox)

    def get_selected_player(self):
        selected_items = self.lobby_table.selectedItems()
        if selected_items:
            item = selected_items[0]
            return item.text()
        else:
            return None

    def on_get_info(self):
        # TODO dummy function, should call logic
        selected_player = self.get_selected_player()
        if selected_player is None:
            QMessageBox.warning(self, "No Player Selected", "Please select a player")
            return

        QMessageBox.information(
            self,
            "Player Info",
            f"Player name: {selected_player}\n\nIP address: 192.168.1.50\nPort: 54321\nHostname: ARNAV-PC",
        )

    def on_kick_player(self):
        # TODO dummy function, should call logic
        selected_player = self.get_selected_player()
        if selected_player is None:
            QMessageBox.warning(self, "No Player Selected", "Please select a player")
            return

        confirm = QMessageBox.question(
            self,
            "Confirm Kick",
            f"Are you sure you want to kick the player {selected_player}?",
            defaultButton=QMessageBox.StandardButton.No,
        )

        if confirm == QMessageBox.StandardButton.No:
            return

        for row in range(self.lobby_table.rowCount()):
            item = self.lobby_table.item(row, 0)
            if item and item.text() == selected_player:
                self.lobby_table.removeRow(row)
                break
