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
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt, pyqtSignal

from core.app.screen_ids import Screens
from ui.screens.base_screen import BaseScreen
from ui.components.button import LeaveButton
from ui.components.combobox import SearchableCombobox
from ui.components.spinner import Spinner

from utils.networking import get_ip_address
from ui.components.dialogs import confirm_warning
from core.config.constants import MAX_PLAYERS


class ServerLobbyScreen(BaseScreen):
    title_text = "Quiz Master – Lobby"

    get_player_info = pyqtSignal(str)
    kick_player = pyqtSignal(str)

    close_server = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.players = 0

        self.setup_ui()

    def setup_ui(self):
        ### LEFT SIDE ###
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)

        title = QLabel("Lobby")
        title.setFont(title_font)

        self.total_players = QLabel(f"Players: {self.players} / {MAX_PLAYERS}")
        self.total_players.setStyleSheet("font-size: 16px;" "color: #A0A0A0;")

        self.spinner = Spinner(
            self, size=20, color=QColor(255, 255, 255), interval_ms=20
        )

        loading_font = QFont()
        loading_font.setPointSize(12)

        loading_lbl = QLabel("Waiting for players...")
        loading_lbl.setFont(loading_font)

        hbox_loading = QHBoxLayout()
        hbox_loading.addWidget(self.spinner)
        hbox_loading.addSpacing(2)
        hbox_loading.addWidget(loading_lbl)

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

        vbox_left = QVBoxLayout()
        vbox_left.addWidget(title)
        vbox_left.addWidget(self.total_players)
        vbox_left.addSpacing(10)
        vbox_left.addLayout(hbox_loading)
        vbox_left.addSpacing(10)
        vbox_left.addWidget(self.lobby_table, stretch=1)
        vbox_left.addSpacing(2)
        vbox_left.addLayout(player_btn_hbox)
        vbox_left.addStretch()

        ### RIGHT SIDE ###
        ip_font = QFont()
        ip_font.setPointSize(32)

        self.ip_address = QLabel(f"Server IP: {get_ip_address()}")
        self.ip_address.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ip_address.setFont(ip_font)

        combobox_font = QFont()
        combobox_font.setPointSize(14)

        select_lbl = QLabel("Select quiz:")
        select_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        select_lbl.setFont(combobox_font)

        # TODO for prototype only
        quizzes = [
            "Maths Quiz",
            "Science Quiz",
            "General Knowledge Quiz",
            "History Quiz",
            "Geography Quiz",
            "Sports Quiz",
            "Music Quiz",
            "Movie Trivia Quiz",
            "Technology Quiz",
            "Literature Quiz",
        ]
        quizzes.sort()

        self.quiz_combo = SearchableCombobox(quizzes)
        self.quiz_combo.setFont(combobox_font)
        self.quiz_combo.setCurrentIndex(-1)
        self.quiz_combo.setFixedWidth(400)

        self.start_btn = QPushButton("Start Game")
        self.start_btn.setFixedSize(220, 60)
        self.start_btn.setStyleSheet("font-size: 22px;")
        self.start_btn.setDisabled(True)
        self.start_btn.clicked.connect(lambda: self.go_to(Screens.COMMON_COUNTDOWN))

        self.start_status = QLabel("(not implemented)")
        self.start_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.start_status.setStyleSheet("font-size: 14px;" "color: #A7A7A7;")

        leave_btn = LeaveButton("Close Lobby", btn_width=100, do_confirm=False)
        leave_btn.clicked.connect(self.close_lobby)

        vbox_right = QVBoxLayout()

        vbox_right.addWidget(self.ip_address)
        vbox_right.addStretch(3)
        vbox_right.addWidget(select_lbl)
        vbox_right.addSpacing(10)
        vbox_right.addWidget(self.quiz_combo, alignment=Qt.AlignmentFlag.AlignCenter)
        vbox_right.addStretch(1)
        vbox_right.addWidget(self.start_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        vbox_right.addSpacing(2)
        vbox_right.addWidget(self.start_status)
        vbox_right.addStretch(5)
        vbox_right.addWidget(leave_btn, alignment=Qt.AlignmentFlag.AlignRight)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(50, 40, 20, 20)
        hbox.addLayout(vbox_left, stretch=1)
        hbox.addLayout(vbox_right, stretch=2)

        self.setLayout(hbox)

    def _get_selected_player(self):
        selected_items = self.lobby_table.selectedItems()
        if selected_items:
            item = selected_items[0]
            return item.text()
        else:
            return None

    def _add_player(self, player):
        row = self.lobby_table.rowCount()
        self.lobby_table.insertRow(row)

        item = QTableWidgetItem(player)
        item.setTextAlignment(
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
        )

        self.lobby_table.setItem(row, 0, item)

    def _remove_player(self, player):
        for row in range(self.lobby_table.rowCount()):
            item = self.lobby_table.item(row, 0)
            if item and item.text() == player:
                self.lobby_table.removeRow(row)
                return True

        return False

    def on_get_info(self):
        # TODO dummy function, should call logic
        selected_player = self._get_selected_player()
        if selected_player is None:
            QMessageBox.warning(self, "No Player Selected", "Please select a player.")
            return

        self.get_player_info.emit(selected_player)

    def on_kick_player(self):
        # TODO dummy function, should call logic
        selected_player = self._get_selected_player()
        if selected_player is None:
            QMessageBox.warning(self, "No Player Selected", "Please select a player.")
            return

        confirm = QMessageBox.question(
            self,
            "Confirm Kick",
            f"Are you sure you want to kick the player {selected_player}?",
            defaultButton=QMessageBox.StandardButton.No,
        )

        if confirm == QMessageBox.StandardButton.No:
            return

        self.kick_player.emit(selected_player)

    def update_player_count(self, amount):
        self.players += amount
        self.total_players.setText(f"Players: {self.players} / {MAX_PLAYERS}")

    def add_player_lobby(self, player):
        self.update_player_count(1)
        self._add_player(player)

    def remove_player_lobby(self, player):
        self.update_player_count(-1)
        self._remove_player(player)

    def reset_lobby(self):
        self.players = 0

        self.total_players.setText(f"Players: {self.players} / {MAX_PLAYERS}")
        self.lobby_table.setRowCount(0)

    def show_player_info(self, nickname, ip, port, hostname):
        QMessageBox.information(
            self,
            "Player Info",
            f"Player name: {nickname}\n\nIP address: {ip}\nPort: {port}\nHostname: {hostname}",
        )

    def close_lobby(self):
        confirm = confirm_warning(
            self,
            "Confirm Closing",
            "Are you sure you want to close the server and return to menu? All players in the server will be disconnected.",
        )

        if confirm:
            self.close_server.emit()

    def on_enter(self, payload=None):
        self.spinner.start()

    def on_leave(self):
        self.spinner.stop()
        self.reset_lobby()
