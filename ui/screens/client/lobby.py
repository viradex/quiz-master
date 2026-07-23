from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QLabel,
    QAbstractItemView,
    QTableWidget,
    QTableWidgetItem,
    QHBoxLayout,
    QVBoxLayout,
)

from ui.components.spinner import Spinner
from ui.screens.base_screen import BaseScreen

from ui.components.button import create_return_button
from ui.components.dialogs import confirm_warning
from utils.formatting import format_ping


class ClientLobbyScreen(BaseScreen):
    title_text = "Quiz Master – Lobby"

    left_server = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setup_ui()

    def setup_ui(self) -> None:
        ## FONTS SETUP ##
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)

        table_font = QFont()
        table_font.setPointSize(12)

        ping_font = QFont()
        ping_font.setPointSize(10)

        waiting_font = QFont()
        waiting_font.setPointSize(18)

        ## WIDGETS SETUP ##
        # Left side
        title = QLabel("Lobby")
        title.setFont(title_font)

        self.lobby_table = QTableWidget()
        self.lobby_table.setFont(table_font)
        self.lobby_table.setColumnCount(1)
        self.lobby_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.lobby_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
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

        self.ping_time = QLabel("Ping: Calculating...")
        self.ping_time.setFont(ping_font)

        # Right side
        waiting_lbl = QLabel("Waiting for the host to start the game...")
        waiting_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        waiting_lbl.setFont(waiting_font)

        self.spinner = Spinner(size=60)

        status_lbl = QLabel("Connected to server. Game will begin shortly.")
        status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_lbl.setStyleSheet("font-size: 14px;" "color: #A7A7A7;")

        leave_btn = create_return_button("Leave Lobby", btn_width=100)
        leave_btn.clicked.connect(self.leave_lobby)

        ## LAYOUTS SETUP ##
        vbox_left = QVBoxLayout()
        vbox_left.addWidget(title)

        vbox_left.addSpacing(10)
        vbox_left.addWidget(self.lobby_table, stretch=1)
        vbox_left.addStretch()
        vbox_left.addSpacing(20)
        vbox_left.addWidget(self.ping_time)

        vbox_right = QVBoxLayout()
        vbox_right.addStretch(1)
        vbox_right.addWidget(waiting_lbl)
        vbox_right.addSpacing(30)
        vbox_right.addWidget(self.spinner, alignment=Qt.AlignmentFlag.AlignCenter)
        vbox_right.addSpacing(10)
        vbox_right.addWidget(status_lbl)
        vbox_right.addStretch(5)
        vbox_right.addWidget(leave_btn, alignment=Qt.AlignmentFlag.AlignRight)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(100, 50, 20, 20)
        hbox.addLayout(vbox_left, stretch=1)
        hbox.addLayout(vbox_right, stretch=2)

        self.setLayout(hbox)

    def add_player_lobby(self, player: str, is_you: bool = False) -> None:
        """
        Adds a player to the lobby table. If `is_you` is True, makes the player bolded
        and with '(you)' suffixed. If the player is themselves, they should be added first.
        """
        row = self.lobby_table.rowCount()
        self.lobby_table.insertRow(row)

        # Adds (you) suffix if is_you
        player = f"{player} (you)" if is_you else player

        item = QTableWidgetItem(player)
        item.setTextAlignment(
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
        )

        # Adds special formatting to the row if the player is themselves
        if is_you:
            font = item.font()
            font.setBold(True)
            item.setFont(font)

        self.lobby_table.setItem(row, 0, item)

    def remove_player_lobby(self, player: str) -> bool:
        """Removes a specific player from the lobby table"""
        for row in range(self.lobby_table.rowCount()):
            item = self.lobby_table.item(row, 0)

            if item and item.text() == player:
                self.lobby_table.removeRow(row)
                return True

        return False

    def reset_lobby(self) -> None:
        """Reset lobby table to remove all rows."""
        self.lobby_table.setRowCount(0)

    def update_ping(self, rtt: float | None) -> None:
        """Update the ping time on the UI."""
        if rtt is None:
            self.ping_time.setText("Ping: Calculating...")
            return

        self.ping_time.setText(f"Ping: {format_ping(rtt)}")

        if rtt < 150:
            self.ping_time.setStyleSheet("color: white;")
        else:
            self.ping_time.setStyleSheet("color: #D16969;")

    def leave_lobby(self) -> None:
        """Displays a warning modal box before leaving the server."""
        confirm = confirm_warning(
            self,
            "Confirm Leaving",
            "Are you sure you want to disconnect and return to menu?",
        )

        if confirm:
            self.left_server.emit()

    def on_enter(self, payload=None) -> None:
        self.spinner.start()

    def on_leave(self) -> None:
        self.spinner.stop()
        self.reset_lobby()

        self.ping_time.setStyleSheet("color: white;")
        self.ping_time.setText("Ping: Calculating...")
