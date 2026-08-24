"""
lobby.py

The server lobby UI screen. Allows seeing players in the lobby, managing players, selecting the quiz,
and stopping the server.
"""

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.config.constants import MAX_PLAYERS, MIN_PLAYERS_FOR_GAME
from ui.components.button import create_return_button
from ui.components.input import ClickableLabel, SearchableCombobox
from ui.components.spinner import Spinner
from ui.screens.base_screen import BaseScreen
from utils.color import get_ping_color
from utils.networking import get_ip_address


class ServerLobbyScreen(BaseScreen):
    """
    Creates the server lobby screen, inheriting BaseScreen. This screen is part of the 'server' category.

    This screen is responsible for displaying the players in the lobby, managing player actions such as
    kicking the player, getting information, selecting the quiz, starting the game, and closing the server.

    Attributes:
        title_text: The default text of the screen when entered. A string is used as that is what the
            title changing code requires.

        player_info_requested: A `pyqtSignal` that emits when the user requests information on a specific
            player. The player ID selected is provided as an argument.

        player_kicked: A `pyqtSignal` that emits when the user kicks a player. The player ID of the player
            to kick is provided as an argument.

        game_started: A `pyqtSignal` that emits when the user wishes to start the game. The quiz ID to play
            is provided as an argument.

        server_closed: A `pyqtSignal` that emits when the user wishes to close the server. No arguments are
            provided.

    Arguments:
        parent: The parent of this screen, or None. Typically, this is the MainWindow.
    """

    title_text = "Quiz Master – Lobby"

    # All player-related actions use the player ID
    player_info_requested = pyqtSignal(str)
    player_kicked = pyqtSignal(str)

    # The game_started signal has the quiz ID
    game_started = pyqtSignal(str)

    server_closed = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # The IP of the server to connect to (used currently to copy to clipboard)
        self.ip: str | None = None

        self._setup_ui()

    def _setup_ui(self) -> None:
        """
        Internal method. Sets up the screen UI for the first time. This method should only be called once,
        preferably in the initialization logic.

        Returns:
            None.
        """
        self._setup_fonts()
        self._setup_widgets()
        self._setup_layouts()

    def _setup_fonts(self) -> None:
        """
        Internal method. Sets up all `QFont` instances and their properties that the widgets will utilize. If
        a font is modified via QSS stylesheets, they are not included here.

        Returns:
            None.
        """
        self.title_font = QFont()
        self.title_font.setPointSize(24)
        self.title_font.setBold(True)

        self.loading_font = QFont()
        self.loading_font.setPointSize(12)

        self.table_font = QFont()
        self.table_font.setPointSize(12)

        self.ip_font = QFont()
        self.ip_font.setPointSize(32)

        self.combobox_font = QFont()
        self.combobox_font.setPointSize(14)

    def _setup_widgets(self) -> None:
        """
        Internal method. Sets up all widgets used by the screen, including styling and slots, if needed. These
        widgets are not added to any global layout in this method, however.

        Returns:
            None.
        """
        self._setup_left_widgets()
        self._setup_right_widgets()

    def _setup_left_widgets(self) -> None:
        """
        Internal method. Sets up all widgets related to the left side of the UI, including styling and slots,
        if needed. These widgets are not added to any global layout in this method, however.

        Returns:
            None.
        """
        self.title = QLabel("Lobby")
        self.title.setFont(self.title_font)

        # Total connected players counter
        self.total_players = QLabel(f"Players: 0 / {MAX_PLAYERS}")
        self.total_players.setStyleSheet("font-size: 16px;" "color: #A0A0A0;")

        # Loading spinner to add animation to an otherwise static screen
        self.spinner = Spinner(size=20)

        self.loading_lbl = QLabel("Waiting for players...")
        self.loading_lbl.setFont(self.loading_font)

        self.lobby_table = QTableWidget()
        self.lobby_table.setFont(self.table_font)
        self.lobby_table.setColumnCount(1)
        self.lobby_table.itemSelectionChanged.connect(self._on_selection_changed)

        # Prevent table items from being edited
        self.lobby_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        # Set icon size for ping indicators
        self.lobby_table.setIconSize(QSize(12, 12))

        lobby_horizontal_header = self.lobby_table.horizontalHeader()
        lobby_vertical_header = self.lobby_table.verticalHeader()

        # Hide both headings
        lobby_horizontal_header.setVisible(False)
        lobby_vertical_header.setVisible(False)

        # Make columns stretch to fill entire table
        lobby_horizontal_header.setSectionResizeMode(
            lobby_horizontal_header.ResizeMode.Stretch
        )
        self.lobby_table.resizeColumnsToContents()

        # Set fixed height for items
        lobby_vertical_header.setDefaultSectionSize(32)

        # Make all items have slight padding from left edge
        self.lobby_table.setStyleSheet("""
            QTableWidget::item {
                padding-left: 10px;
            }
        """)

        # Buttons for player management, enabled when a player is selected
        self.get_info_btn = QPushButton("Get Info")
        self.get_info_btn.setStyleSheet("font-size: 14px;")
        self.get_info_btn.setDisabled(True)
        self.get_info_btn.clicked.connect(self._on_get_info)

        self.kick_btn = QPushButton("Kick Player")
        self.kick_btn.setStyleSheet("font-size: 14px;")
        self.kick_btn.setDisabled(True)
        self.kick_btn.clicked.connect(self._on_kick_player)

    def _setup_right_widgets(self) -> None:
        """
        Internal method. Sets up all widgets related to the right side of the UI, including styling and slots,
        if needed. These widgets are not added to any global layout in this method, however.

        Returns:
            None.
        """
        # Use a ClickableLabel to allow the user to copy the IP address to clipboard for easier sharing
        self.ip_address = ClickableLabel()
        self.ip_address.setToolTip("Click to copy to clipboard")
        self.ip_address.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ip_address.setFont(self.ip_font)
        self.ip_address.clicked.connect(self._on_ip_copy)

        # Quiz selection widgets
        self.select_lbl = QLabel("Select quiz:")
        self.select_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.select_lbl.setFont(self.combobox_font)

        self.quiz_combo = SearchableCombobox()
        self.quiz_combo.setFont(self.combobox_font)
        self.quiz_combo.setMaximumWidth(500)

        # When user selects quiz, check if game can be started
        self.quiz_combo.currentIndexChanged.connect(self._update_start_game_state)

        # Button to start game, disabled until all conditions met
        self.start_btn = QPushButton("Start Game")
        self.start_btn.setFixedSize(220, 60)
        self.start_btn.setStyleSheet("font-size: 22px;")
        self.start_btn.setDisabled(True)
        self.start_btn.clicked.connect(self._on_start_game)

        # Displays reason why start button is disabled, if any
        self.start_status = QLabel()
        self.start_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.start_status.setStyleSheet("font-size: 14px;" "color: #A7A7A7;")

        self.leave_btn = create_return_button("Close Lobby", btn_width=100)
        self.leave_btn.clicked.connect(self.server_closed.emit)

    def _setup_layouts(self) -> None:
        """
        Internal method. Sets up all the layouts on this screen, adding widgets and controlling alignment, spacing,
        and stretching. The main layout is also applied as this screen's primary layout via `setLayout()`.

        Returns:
            None.
        """
        # Create child layouts
        left_layout = self._create_left_layout()
        right_layout = self._create_right_layout()

        # Makes left side take less space than right at 1:2 ratio
        hbox = QHBoxLayout()
        hbox.setContentsMargins(50, 40, 20, 20)
        hbox.addLayout(left_layout, stretch=1)
        hbox.addLayout(right_layout, stretch=2)

        self.setLayout(hbox)

    def _create_left_layout(self) -> QVBoxLayout:
        """
        Internal method. Creates the left side layout, adding widgets and controlling alignment, spacing,
        and stretching.

        Returns:
            The layout to add to the main layout.
        """
        # Loading container
        hbox_loading = QHBoxLayout()
        hbox_loading.addWidget(self.spinner)
        hbox_loading.addSpacing(2)
        hbox_loading.addWidget(self.loading_lbl)

        # Buttons below lobby table
        lobby_btn_hbox = QHBoxLayout()
        lobby_btn_hbox.addWidget(self.get_info_btn)
        lobby_btn_hbox.addWidget(self.kick_btn)

        vbox_left = QVBoxLayout()
        vbox_left.addWidget(self.title)
        vbox_left.addWidget(self.total_players)
        vbox_left.addSpacing(10)
        vbox_left.addLayout(hbox_loading)
        vbox_left.addSpacing(10)
        vbox_left.addWidget(self.lobby_table, stretch=1)
        vbox_left.addSpacing(2)
        vbox_left.addLayout(lobby_btn_hbox)
        vbox_left.addStretch()

        return vbox_left

    def _create_right_layout(self) -> QVBoxLayout:
        """
        Internal method. Creates the right side layout, adding widgets and controlling alignment, spacing,
        and stretching.

        Returns:
            The layout to add to the main layout.
        """
        # Make combobox centered and take up more width the more space it has
        combo_hbox = QHBoxLayout()
        combo_hbox.addStretch(1)
        combo_hbox.addWidget(self.quiz_combo, stretch=3)
        combo_hbox.addStretch(1)

        vbox_right = QVBoxLayout()
        vbox_right.addWidget(self.ip_address)
        vbox_right.addStretch(3)
        vbox_right.addWidget(self.select_lbl)
        vbox_right.addSpacing(10)
        vbox_right.addLayout(combo_hbox)
        vbox_right.addSpacing(20)
        vbox_right.addWidget(self.start_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        vbox_right.addSpacing(2)
        vbox_right.addWidget(self.start_status)
        vbox_right.addStretch(5)
        vbox_right.addWidget(self.leave_btn, alignment=Qt.AlignmentFlag.AlignRight)

        return vbox_right

    def add_player_lobby(self, player_id: str, nickname: str) -> None:
        """
        Adds a player to the lobby table on the UI. A player ID is attached to the nickname for sending signals
        and identifying the player more safely than a nickname. Only the nickname is visible on the UI; the
        player ID is hidden from the UI, but stored internally and linked to the nickname.

        The player count is also updated, and the loading spinner is hidden if the number of players is the same
        as the maximum amount of players the server can support handling.

        Arguments:
            player_id: A string representing a unique player ID for the given player. Used to identify the player
                when sending requests, for example, kicking the player. A string is used as it is more versatile
                for IDs than an integer and allows more combinations in a shorter number of characters.

            nickname: A string representing the player's nickname. This value is shown on the UI in the lobby table,
                but is not used to identify the player internally, it is purely for user convenience. A string
                is used as the nickname typically contains letters and characters, which a string naturally holds.

        Returns:
            None.
        """
        self._add_player(player_id, nickname)
        self._update_player_count()
        self._update_spinner_visibility()

    def remove_player_lobby(self, player_id: str) -> None:
        """
        Removes a player from the lobby table on the UI. The player ID is used for identifying the player
        from the lobby table, internally, rather than the nickname. If the player ID does not exist, nothing
        happens.

        The player count is also updated, and the loading spinner is shown if the number of players has since
        decreased from the maximum amount of players the server can support handling.

        Arguments:
            player_id: A string representing a unique player ID for the player, to remove them from the
                table. A string is used as it is more versatile for IDs than an integer and allows more
                combinations in a shorter number of characters.

        Returns:
            None.
        """
        self._remove_player(player_id)
        self._update_player_count()
        self._update_spinner_visibility()

    def update_rtt_color(self, player_id: str, rtt: float) -> None:
        """
        Updates the round-trip time color of the specified player ID in the lobby table. The color is set
        as the item's icon in the lobby table next to the player's nickname, representing in a broad sense the
        round-trip time of the player. If the player ID does not exist in the table, no colors are updated.

        Arguments:
            player_id: A string representing a unique player ID for the player, to update their round-trip time
                color. A string is used as it is more versatile for IDs than an integer and allows more
                combinations in a shorter number of characters.

            rtt: A float representing the round-trip time, in milliseconds, of the player. This value is used
                to determine the color shown. A float is used for easier usage as the round-trip time is
                calculated in fractions of a millisecond, which a float represents well.

        Returns:
            None.
        """
        # Get player, and if they do not exist, exit prematurely
        player = self._get_player_item(player_id)
        if player is None:
            return

        # QIcon does not accept a Path object, hence convert to a string before passing in
        player.setIcon(QIcon(str(get_ping_color(rtt))))

    def reset_lobby(self) -> None:
        """
        Reset the lobby table by clearing and removing all the rows. Also, resets the player count and clears
        all the values in the quiz dropdown, allowing a reset for the screen.

        Returns:
            None.
        """
        self.lobby_table.setRowCount(0)
        self._update_player_count()

        # Clear quizzes in dropdown
        self.quiz_combo.clear()

    def set_quizzes(self, quizzes: dict[str, str]) -> None:
        """
        Set the quizzes that can be selected in the quiz selection dropdown menu. This does not remove existing
        data from the quiz dropdown menu, so this method is only intended to be run generally when entering the
        screen. The quizzes entered are also not sorted in this method, and they are expected to have been
        sorted beforehand, however needed (for example, having the custom quizzes appear before the default
        quizzes).

        The quizzes dictionary should contain the quiz ID as the identifier and the quiz title as the display
        value. The quiz ID is used internally to identify a quiz that has been selected, and the title is purely
        for the UI.

        Arguments:
            quizzes: A dictionary containing the quiz IDs and quiz title to add to the dropdown, in the order
                provided. Information about the dictionary values is provided above. A dictionary is used as
                it provides an easy way to link multiple related values together and identify them easily.

        Returns:
            None.
        """
        # Add each value to dropdown with hidden ID
        for quiz_id, quiz_title in quizzes.items():
            self.quiz_combo.addItem(quiz_title, quiz_id)

        # Leave no quiz selected at first
        self.quiz_combo.setCurrentIndex(-1)

    def _update_spinner_visibility(self) -> None:
        """
        Internal method. Updates the visibility of the spinner and its loading text depending on if the server
        can accept any more players. This determination is based entirely around the number of rows in the lobby
        table, and thus can be inaccurate if the table and the actual number of players have somehow gone out
        of sync, though this should never happen in normal usage.

        When the number of players is equal to or exceeds the maximum number of players allowed, the loading
        spinner is hidden. Otherwise, it is shown.

        Returns:
            None.
        """
        if self.lobby_table.rowCount() >= MAX_PLAYERS:
            self.spinner.hide()
            self.loading_lbl.hide()
        else:
            self.spinner.show()
            self.loading_lbl.show()

    def _update_player_count(self) -> None:
        """
        Internal method. Updates the player counter to reflect the number of rows in the lobby table, out of
        the maximum number of players as defined in the constant. The number of players in the lobby is based
        entirely around the number of rows in the lobby table, and thus can be inaccurate if the table and the
        actual number of players have somehow gone out of sync, though this should never happen in normal usage.

        Returns:
            None.
        """
        self.total_players.setText(
            f"Players: {self.lobby_table.rowCount()} / {MAX_PLAYERS}"
        )

    def _update_start_game_state(self) -> None:
        """
        Internal method. Updates the Start Game button state to be enabled if all checks pass, else disabled. If
        the button is disabled, a small subtext is shown describing the condition that must be met in order for
        the button to be enabled.

        The button is disabled if:
        - No quiz has been selected.
        - There are enough players to start the game.

        These checks are only done purely based on information from the UI, and thus can be inaccurate. Due to
        this, the user requesting the game to be started should not be trusted, and stricter validation should
        be performed before the game starts to ensure values have not been tampered with.

        Returns:
            None.
        """
        # No quiz selected yet
        if self.quiz_combo.currentIndex() == -1:
            self.start_btn.setEnabled(False)
            self.start_status.setText("(select a quiz from the list)")

        # Not enough players to start the game
        elif self.lobby_table.rowCount() < MIN_PLAYERS_FOR_GAME:
            self.start_btn.setEnabled(False)
            self.start_status.setText(
                f"(at least {MIN_PLAYERS_FOR_GAME} {"player is" if MIN_PLAYERS_FOR_GAME == 1 else "players are"} required)"
            )

        # All checks passed
        else:
            self.start_btn.setEnabled(True)
            self.start_status.setText("")

    def _on_selection_changed(self) -> None:
        """
        Internal method. Intended to be called when a player is selected or deselected from the lobby table.

        This method changes the state of the player management buttons to be enabled if a player has been
        selected, or disabled if a player has been deselected or not selected at all.

        Returns:
            None.
        """
        # If player is not selected, disable player buttons
        if self._get_selected_player_item() is None:
            self.get_info_btn.setEnabled(False)
            self.kick_btn.setEnabled(False)
        else:
            self.get_info_btn.setEnabled(True)
            self.kick_btn.setEnabled(True)

    def _on_get_info(self) -> None:
        """
        Internal method. Intended to be called when the Get Info button is clicked for a player.

        The button should only be enabled if a player was selected. If a player was not selected and this method
        was somehow called, it fails with an error modal box. Otherwise, it displays more advanced player
        information.

        Returns:
            None.
        """
        selected_item = self._get_selected_player_item()

        # Should not happen, but here as a precaution
        if selected_item is None:
            self.show_error("No Player Selected", "Please select a player.")
            return

        # Get hidden player ID
        player_id = selected_item.data(Qt.ItemDataRole.UserRole)
        self.player_info_requested.emit(player_id)

    def _on_kick_player(self) -> None:
        """
        Internal method. Intended to be called when the Kick button is clicked for a player.

        The button should only be enabled if a player was selected. If a player was not selected and this method
        was somehow called, it fails with an error modal box. Otherwise, it confirms to kick the player before
        kicking them from the server and removing them from the UI.

        Returns:
            None.
        """
        selected_item = self._get_selected_player_item()

        # Should not happen, but here as a precaution
        if selected_item is None:
            self.show_error("No Player Selected", "Please select a player.")
            return

        # Get hidden player ID and nickname for dialog
        player_id = selected_item.data(Qt.ItemDataRole.UserRole)
        nickname = selected_item.text()

        confirm = self.show_question(
            "Confirm Kick", f"Are you sure you want to kick the player {nickname}?"
        )

        if confirm:
            self.player_kicked.emit(player_id)

    def _on_start_game(self) -> None:
        """
        Internal method. Intended to be called when the Start Game button is clicked.

        The button should only be enabled if all checks passed for starting a game. However, this method does
        not check if all checks passed UI-side again, as it is expected for the logic to ensure the quiz can
        be successfully started. The quiz ID is provided.

        Returns:
            None.
        """
        # Provide quiz ID from dropdown
        self.game_started.emit(self.quiz_combo.currentData())

    def _on_ip_copy(self) -> None:
        """
        Internal method. Copies the server IP address to the user's clipboard. If there is no server IP, for
        example, if the program is unable to determine it, no item is copied to the user's clipboard.

        Returns:
            None.
        """
        # Adds item to clipboard if IP is set
        if self.ip:
            QApplication.clipboard().setText(self.ip)
            self.set_status("Copied IP to clipboard", 3000)

    def _get_selected_player_item(self) -> QTableWidgetItem | None:
        """
        Internal method. Gets the player item from the lobby table that the user selected, or None if the user
        has not selected anything.

        Returns:
            A `QTableWidgetItem` of the item the user selected from the lobby table, or None if nothing
            was selected by the user.
        """
        selected_items = self.lobby_table.selectedItems()
        return selected_items[0] if selected_items else None

    def _get_player_item(self, player_id: str) -> QTableWidgetItem | None:
        """
        Internal method. Gets the player item from the lobby table that matches the provided player ID, or None
        if the player ID does not match any values in the lobby table.

        Arguments:
            player_id: A string representing a unique player ID for the player, to find the matching value in
                the lobby table to return. A string is used as it is the data type used to store player IDs
                internally in the table as well, allowing for an easier comparison check.

        Returns:
            A `QTableWidgetItem` of the item that matches the player ID provided, or None if no matches were
            found.
        """
        for row in range(self.lobby_table.rowCount()):
            # Cycle through all rows and get item from first and only column, column 0
            item = self.lobby_table.item(row, 0)

            # If item is valid and hidden player ID matches
            if item and item.data(Qt.ItemDataRole.UserRole) == player_id:
                return item

        # No matches found
        return None

    def _add_player(self, player_id: str, nickname: str) -> None:
        """
        Internal method. Adds a player to the end of the lobby table on the UI. A hidden player ID is attached
        to the nickname for sending signals and identifying the player more safely than a nickname. Only the
        nickname is visible on the UI; the player ID is hidden from the UI, but stored internally and linked
        to the nickname. The gray round-trip time color is displayed at the start.

        Arguments:
            player_id: A string representing a unique player ID for the given player. Used to identify the player
                when sending requests, for example, kicking the player. A string is used as it is more versatile
                for IDs than an integer and allows more combinations in a shorter number of characters.

            nickname: A string representing the player's nickname. This value is shown on the UI in the lobby table,
                but is not used to identify the player internally, it is purely for user convenience. A string
                is used as the nickname typically contains letters and characters, which a string naturally holds.

        Returns:
            None.
        """
        # Insert new row at end of table
        row = self.lobby_table.rowCount()
        self.lobby_table.insertRow(row)

        item = QTableWidgetItem(nickname)

        # Set neutral ping icon at start
        item.setIcon(QIcon(str(get_ping_color())))

        # Sets alignment to right-aligned and centered vertically on item
        item.setTextAlignment(
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
        )

        # Store hidden player ID
        item.setData(Qt.ItemDataRole.UserRole, player_id)

        # Add the item to the last row, in the only column (column 0)
        self.lobby_table.setItem(row, 0, item)
        self._update_start_game_state()

    def _remove_player(self, player_id: str) -> bool:
        """
        Internal method. Removes a player from the lobby table on the UI. The player ID is used for identifying
        the player from the lobby table, internally, rather than the nickname.

        Arguments:
            player_id: A string representing a unique player ID for the player, to remove them from the
                table. A string is used as it is more versatile for IDs than an integer and allows more
                combinations in a shorter number of characters.

        Returns:
            A boolean informing whether or not the removal was successful. If the player ID was found in the
            lobby table and successfully removed, True is returned. If the player ID could not be found, False
            is returned instead.
        """
        # Get player QTableWidgetItem, returning False if it could not be found
        item = self._get_player_item(player_id)
        if item is None:
            return False

        # Remove row from table and return True, success
        self.lobby_table.removeRow(item.row())
        self._update_start_game_state()
        return True

    def on_enter(self, payload: None = None) -> None:
        # Start spinner animation and get current device IP
        self.spinner.start()
        self.ip = get_ip_address()

        if self.ip:
            self.ip_address.setText(f"Server IP: {self.ip}")
        else:
            # On some systems, the DNS lookup fails
            self.ip_address.setText("Server IP: Unable to determine")

    def on_leave(self) -> None:
        # Stop spinner to reduce CPU usage and reset lobby to prevent stale data on next visit
        self.spinner.stop()
        self.reset_lobby()
