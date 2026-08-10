"""
lobby.py

The client lobby UI screen. Allows seeing other players in the lobby, and leaving the server if
needed.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.config.constants import RTT_WARNING_THRESHOLD_MS
from ui.components.button import create_return_button
from ui.components.dialog import confirm_warning
from ui.components.spinner import Spinner
from ui.screens.base_screen import BaseScreen
from utils.formatting import format_ping


class ClientLobbyScreen(BaseScreen):
    """
    Creates the client lobby screen, inheriting BaseScreen. This screen is part of the 'client' category.

    This screen is responsible for displaying the players in the lobby with the current user, and allowing
    the user to leave the server.

    Attributes:
        title_text: The default text of the screen when entered. A string is used as that is what the
            title changing code requires.

        left_server: A `pyqtSignal` that emits when the user wishes to leave the server. No arguments are
            provided.

    Arguments:
        parent: The parent of this screen, or None. Typically, this is the MainWindow.
    """

    title_text = "Quiz Master – Lobby"

    left_server = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

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

        self.table_font = QFont()
        self.table_font.setPointSize(12)

        self.ping_font = QFont()
        self.ping_font.setPointSize(10)

        self.waiting_font = QFont()
        self.waiting_font.setPointSize(18)

    def _setup_widgets(self) -> None:
        """
        Internal method. Sets up all widgets used by the screen, including styling and slots, if needed. These
        widgets are not added to any global layout in this method, however.

        Returns:
            None.
        """
        # Left side
        self.title = QLabel("Lobby")
        self.title.setFont(self.title_font)

        self.lobby_table = QTableWidget()
        self.lobby_table.setFont(self.table_font)
        self.lobby_table.setColumnCount(1)

        # Prevents table contents from being edited or selected
        self.lobby_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.lobby_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)

        lobby_horizontal_header = self.lobby_table.horizontalHeader()
        lobby_vertical_header = self.lobby_table.verticalHeader()

        # Remove both headers from the table
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

        self.ping_time = QLabel()
        self.ping_time.setFont(self.ping_font)

        # Right side
        # Static waiting text
        self.waiting_lbl = QLabel("Waiting for the host to start the game...")
        self.waiting_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.waiting_lbl.setFont(self.waiting_font)

        self.spinner = Spinner(size=60, interval_ms=30, color="#64B4FF")

        self.status_lbl = QLabel("Connected to server. Game will begin shortly.")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_lbl.setStyleSheet("font-size: 14px;" "color: #A7A7A7;")

        self.leave_btn = create_return_button("Leave Lobby", btn_width=100)
        self.leave_btn.clicked.connect(self._on_leave_lobby)

    def _setup_layouts(self) -> None:
        """
        Internal method. Sets up all the layouts on this screen, adding widgets and controlling alignment, spacing,
        and stretching. The main layout is also applied as this screen's primary layout via `setLayout()`.

        Returns:
            None.
        """
        vbox_left = QVBoxLayout()
        vbox_left.addWidget(self.title)
        vbox_left.addSpacing(10)
        vbox_left.addWidget(self.lobby_table, stretch=1)
        vbox_left.addStretch()
        vbox_left.addSpacing(20)
        vbox_left.addWidget(self.ping_time)

        # Make contents appear more at the top than the bottom
        vbox_right = QVBoxLayout()
        vbox_right.addStretch(1)
        vbox_right.addWidget(self.waiting_lbl)
        vbox_right.addSpacing(30)
        vbox_right.addWidget(self.spinner, alignment=Qt.AlignmentFlag.AlignCenter)
        vbox_right.addSpacing(10)
        vbox_right.addWidget(self.status_lbl)
        vbox_right.addStretch(5)
        vbox_right.addWidget(self.leave_btn, alignment=Qt.AlignmentFlag.AlignRight)

        # Make the right side take up 2/3rds of the window width
        hbox = QHBoxLayout()
        hbox.setContentsMargins(100, 50, 20, 20)
        hbox.addLayout(vbox_left, stretch=1)
        hbox.addLayout(vbox_right, stretch=2)

        self.setLayout(hbox)

    def add_player_lobby(self, nickname: str, is_self: bool = False) -> None:
        """
        Adds a player to the end of the lobby table on the UI.

        If `is_self`, the item has the text '(you)' suffixed to the player's nickname. The player's nickname
        is also bolded. In normal usage, it is expected that the item with `is_self=True` would be added
        at the beginning of the table. However, this is not enforced.

        Arguments:
            nickname: A string representing the nickname of the player to add to the table. A string is used
                as the nickname of the player added is naturally a word or collection of words which a string
                represents well.

            is_self: A boolean determining if the player being added is the own player or not. If it is, they
                are styled as described above, but do not have any other unique interactions.

        Returns:
            None.
        """
        # Inserts row at end of table
        row = self.lobby_table.rowCount()
        self.lobby_table.insertRow(row)

        # Adds '(you)' suffix if is_self
        nickname = f"{nickname} (you)" if is_self else nickname

        # Sets alignment to right-aligned and centered vertically on item
        item = QTableWidgetItem(nickname)
        item.setTextAlignment(
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
        )

        # Adds special formatting to the row if the player is themselves
        if is_self:
            font = item.font()
            font.setBold(True)
            item.setFont(font)

        # Add the item to the last row, in the only column (column 0)
        self.lobby_table.setItem(row, 0, item)

    def remove_player_lobby(self, nickname: str) -> bool:
        """
        Removes a player from the lobby table on the UI, by display nickname.

        The method searches through all the player nicknames currently in the table, and if a match is found,
        it removes its row. The match is case-sensitive.

        Arguments:
            nickname: A string representing the nickname of the player to remove from the table. A string is
                used as the nickname of the player is naturally a word or collection of words which a string
                represents well.

        Returns:
            A boolean determining whether a player was successfully removed or not. True if removed, else False
            if no player was removed. A boolean is used as it can easily convey a binary success value.
        """
        for row in range(self.lobby_table.rowCount()):
            # Get the player item in the only column (column 0)
            item = self.lobby_table.item(row, 0)

            # If item is not None and matches, removes player row
            if item and item.text() == nickname:
                self.lobby_table.removeRow(row)
                return True

        # No matching player nickname found
        return False

    def clear_lobby(self) -> None:
        """
        Reset the lobby table by clearing and removing all the rows.

        Returns:
            None.
        """
        self.lobby_table.setRowCount(0)

    def update_rtt(self, rtt: float | None = None) -> None:
        """
        Update the round-trip time on the UI.

        If the `rtt` provided is None, the label resets its style and assumes the loading text. Otherwise, the
        round-trip time is formatted accordingly. If the round-trip time exceeds the warning threshold, it is
        colored red. Otherwise, it is colored white.

        Arguments:
            rtt: The round-trip time in milliseconds to display on the client, or None. A float is used as it can
                accurately display sub-millisecond measurements and is what the calculations provide. A value of
                None can be used to reset the label. Default is None.

        Returns:
            None.
        """
        # If no RTT was provided, assume a label reset or waiting status
        if rtt is None:
            self.ping_time.setText("Ping: Calculating...")
            self.ping_time.setStyleSheet("color: white;")
            return

        self.ping_time.setText(f"Ping: {format_ping(rtt)}")

        # If RTT isn't too high, color normally, else, show warning color
        if rtt < RTT_WARNING_THRESHOLD_MS:
            self.ping_time.setStyleSheet("color: white;")
        else:
            self.ping_time.setStyleSheet("color: #D16969;")

    def _on_leave_lobby(self) -> None:
        """
        Internal method. Intended to be run when the user clicks the Leave button. Displays a warning confirmation
        dialog to ensure the user wishes to leave the server, then disconnects from the server.

        Returns:
            None.
        """
        confirm = confirm_warning(
            self,
            "Confirm Leaving",
            "Are you sure you want to disconnect and return to menu?",
        )

        if confirm:
            self.left_server.emit()

    def on_enter(self, payload: None = None) -> None:
        # Reset RTT and start spinner
        self.update_rtt()
        self.spinner.start()

    def on_leave(self) -> None:
        # Stop spinner to reduce CPU usage, and reset values and lobby table
        self.spinner.stop()
        self.clear_lobby()

        self.ping_time.setStyleSheet("color: white;")
        self.update_rtt()
