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

from ui.screens.base_screen import BaseScreen
from ui.components.input import SearchableCombobox
from ui.components.spinner import Spinner

from ui.components.button import create_return_button
from ui.components.dialogs import confirm_warning
from utils.networking import get_ip_address
from core.config.constants import MAX_PLAYERS, MIN_PLAYERS_FOR_GAME


class ServerLobbyScreen(BaseScreen):
    title_text = "Quiz Master – Lobby"

    player_info_requested = pyqtSignal(str)
    player_kicked = pyqtSignal(str)
    game_started = pyqtSignal(str)

    server_closed = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setup_ui()

    def setup_ui(self) -> None:
        ## FONTS SETUP ##
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)

        loading_font = QFont()
        loading_font.setPointSize(12)

        table_font = QFont()
        table_font.setPointSize(12)

        ip_font = QFont()
        ip_font.setPointSize(32)

        combobox_font = QFont()
        combobox_font.setPointSize(14)

        ## WIDGETS SETUP ##
        # Left side
        title = QLabel("Lobby")
        title.setFont(title_font)

        self.total_players = QLabel(f"Players: 0 / {MAX_PLAYERS}")
        self.total_players.setStyleSheet("font-size: 16px;" "color: #A0A0A0;")

        self.spinner = Spinner(size=20, color=QColor(255, 255, 255), interval_ms=20)

        loading_lbl = QLabel("Waiting for players...")
        loading_lbl.setFont(loading_font)

        # Hbox layout for loading above (not in layouts section for easier readability)
        hbox_loading = QHBoxLayout()
        hbox_loading.addWidget(self.spinner)
        hbox_loading.addSpacing(2)
        hbox_loading.addWidget(loading_lbl)

        self.lobby_table = QTableWidget()
        self.lobby_table.setFont(table_font)
        self.lobby_table.setColumnCount(1)
        self.lobby_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.lobby_table.resizeColumnsToContents()
        self.lobby_table.itemSelectionChanged.connect(self.on_selection_changed)

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
        self.get_info_btn.setStyleSheet("font-size: 14px;")
        self.get_info_btn.setDisabled(True)
        self.get_info_btn.clicked.connect(self.on_get_info)

        self.kick_btn = QPushButton("Kick Player")
        self.kick_btn.setStyleSheet("font-size: 14px;")
        self.kick_btn.setDisabled(True)
        self.kick_btn.clicked.connect(self.on_kick_player)

        # Hbox layout for buttons above (not in layouts section for easier readability)
        lobby_btn_hbox = QHBoxLayout()
        lobby_btn_hbox.addWidget(self.get_info_btn)
        lobby_btn_hbox.addWidget(self.kick_btn)

        # Right side
        self.ip_address = QLabel("Server IP: Unable to determine")
        self.ip_address.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ip_address.setFont(ip_font)

        select_lbl = QLabel("Select quiz:")
        select_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        select_lbl.setFont(combobox_font)

        self.quiz_combo = SearchableCombobox()
        self.quiz_combo.setFont(combobox_font)
        self.quiz_combo.setMaximumWidth(500)
        self.quiz_combo.currentIndexChanged.connect(self.check_start_game_state)

        self.start_btn = QPushButton("Start Game")
        self.start_btn.setFixedSize(220, 60)
        self.start_btn.setStyleSheet("font-size: 22px;")
        self.start_btn.setDisabled(True)
        self.start_btn.clicked.connect(self.on_start_game)

        self.start_status = QLabel()
        self.start_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.start_status.setStyleSheet("font-size: 14px;" "color: #A7A7A7;")

        leave_btn = create_return_button("Close Lobby", btn_width=100)
        leave_btn.clicked.connect(self.close_lobby)

        ## LAYOUTS SETUP ##
        vbox_left = QVBoxLayout()
        vbox_left.addWidget(title)
        vbox_left.addWidget(self.total_players)
        vbox_left.addSpacing(10)
        vbox_left.addLayout(hbox_loading)
        vbox_left.addSpacing(10)
        vbox_left.addWidget(self.lobby_table, stretch=1)
        vbox_left.addSpacing(2)
        vbox_left.addLayout(lobby_btn_hbox)
        vbox_left.addStretch()

        combo_hbox = QHBoxLayout()
        combo_hbox.addStretch(1)
        combo_hbox.addWidget(self.quiz_combo, stretch=3)
        combo_hbox.addStretch(1)

        vbox_right = QVBoxLayout()
        vbox_right.addWidget(self.ip_address)
        vbox_right.addStretch(3)
        vbox_right.addWidget(select_lbl)
        vbox_right.addSpacing(10)
        vbox_right.addLayout(combo_hbox)
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

    def on_selection_changed(self) -> None:
        # If player is selected, enable player buttons
        if self._get_selected_player_item() is not None:
            self.get_info_btn.setDisabled(False)
            self.kick_btn.setDisabled(False)
        else:
            self.get_info_btn.setDisabled(True)
            self.kick_btn.setDisabled(True)

    def set_player_count(self) -> None:
        """Set player counter to reflect the players in the lobby table."""
        self.total_players.setText(
            f"Players: {self.lobby_table.rowCount()} / {MAX_PLAYERS}"
        )

    def add_player_lobby(self, player_id: str, nickname: str) -> None:
        """Adds a player to the lobby table and increases the player counter."""
        self._add_player(player_id, nickname)
        self.set_player_count()

    def remove_player_lobby(self, player_id: str) -> None:
        """Removes a player from the lobby table and decreases the player counter."""
        self._remove_player(player_id)
        self.set_player_count()

    def reset_lobby(self) -> None:
        """Resets the player counter to `0`, and removes all values from the lobby table."""
        self.lobby_table.setRowCount(0)
        self.set_player_count()
        self.quiz_combo.clear()

    def close_lobby(self) -> None:
        """Displays a warning modal box before closing the server."""
        confirm = confirm_warning(
            self,
            "Confirm Closing",
            "Are you sure you want to close the server and return to menu? All players in the server will be disconnected.",
        )

        if confirm:
            self.server_closed.emit()

    def set_quizzes(self, quizzes: dict[str, str]) -> None:
        """Set the quizzes that can be selected from the dropdown."""
        # TODO add some sort of differentiation for quizzes with the same name
        for quiz_id, quiz_title in quizzes.items():
            self.quiz_combo.addItem(quiz_title, quiz_id)

        # Leave no quiz selected at first
        self.quiz_combo.setCurrentIndex(-1)

    def check_start_game_state(self) -> None:
        """Loosely checks if the game can be started, and if the checks are successful, enables the Start button."""
        if self.quiz_combo.currentIndex() == -1:
            self.start_btn.setDisabled(True)
            self.start_status.setText("(select a quiz from the list)")
        elif self.lobby_table.rowCount() < MIN_PLAYERS_FOR_GAME:
            self.start_btn.setDisabled(True)
            self.start_status.setText(
                f"(at least {MIN_PLAYERS_FOR_GAME} {"player is" if MIN_PLAYERS_FOR_GAME == 1 else "players are"} required)"
            )
        else:
            self.start_btn.setDisabled(False)
            self.start_status.setText("")

    def on_get_info(self) -> None:
        """Get player info for the selected player."""
        selected_item = self._get_selected_player_item()

        # Should not happen, but here as a precaution
        if selected_item is None:
            self.show_warning("No Player Selected", "Please select a player.")
            return

        player_id = selected_item.data(Qt.ItemDataRole.UserRole)
        self.player_info_requested.emit(player_id)

    def on_kick_player(self) -> None:
        """Kick the selected player."""
        selected_item = self._get_selected_player_item()

        # Should not happen, but here as a precaution
        if selected_item is None:
            self.show_warning("No Player Selected", "Please select a player.")
            return

        player_id = selected_item.data(Qt.ItemDataRole.UserRole)
        nickname = selected_item.text()

        confirm = self.show_question(
            "Confirm Kick",
            f"Are you sure you want to kick the player {nickname}?",
            default="no",
        )

        if confirm:
            self.player_kicked.emit(player_id)

    def on_start_game(self) -> None:
        self.game_started.emit(self.quiz_combo.currentData())

    def _get_selected_player_item(self) -> QTableWidgetItem | None:
        """Get the selected player item from the lobby table."""
        selected_items = self.lobby_table.selectedItems()
        return selected_items[0] if selected_items else None

    def _add_player(self, player_id: str, nickname: str) -> None:
        """Add a player to the lobby table."""
        row = self.lobby_table.rowCount()
        self.lobby_table.insertRow(row)

        item = QTableWidgetItem(nickname)
        item.setTextAlignment(
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
        )

        # Store hidden player ID
        item.setData(Qt.ItemDataRole.UserRole, player_id)

        self.lobby_table.setItem(row, 0, item)
        self.check_start_game_state()

    def _remove_player(self, player_id: str) -> bool:
        """Remove a player from the lobby table based on player ID."""
        for row in range(self.lobby_table.rowCount()):
            item = self.lobby_table.item(row, 0)

            if item.data(Qt.ItemDataRole.UserRole) == player_id:
                self.lobby_table.removeRow(row)
                self.check_start_game_state()
                return True

        return False

    def on_enter(self, payload=None) -> None:
        self.spinner.start()

        ip = get_ip_address()
        if ip:
            self.ip_address.setText(f"Server IP: {ip}")
        else:
            self.ip_address.setText("Server IP: Unable to determine")

    def on_leave(self) -> None:
        self.spinner.stop()
        self.reset_lobby()
