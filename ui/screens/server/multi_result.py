"""
multi_result.py

The server multi-question results UI screen. Allows viewing the global results and correct answer,
as well as the leaderboard.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QStackedLayout,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.app.enums import AnswerButtonGridMode
from models.payloads import ServerResultsPayload
from ui.components.answer_bar_chart import AnswerBarChart
from ui.components.answer_button_grid import AnswerButtonGrid
from ui.components.button import create_return_button
from ui.components.card import Card
from ui.components.dialog import confirm_warning
from ui.screens.base_screen import BaseScreen
from utils.color import darken_color


class ServerMultiResultScreen(BaseScreen):
    """
    Creates the server multi-question results screen, inheriting BaseScreen. This screen is part of the
    'server' category.

    This screen is responsible for allowing the host to view the number of submissions for each answer,
    the correct answer, and current leaderboard.

    Attributes:
        title_text: The default text of the screen when entered. A string is used as that is what the
            title changing code requires.

        next_question_requested: A `pyqtSignal` that emits when the user wishes to move onto the next
            question. No arguments are provided.

        end_game_requested: A `pyqtSignal` that emits when the user wishes to end the game prematurely.
            No arguments are provided.

        player_info_requested: A `pyqtSignal` that emits when the user requests information on a specific
            player. The player ID selected is provided as an argument.

        player_kicked: A `pyqtSignal` that emits when the user kicks a player. The player ID of the player
            to kick is provided as an argument.

    Arguments:
        parent: The parent of this screen, or None. Typically, this is the MainWindow.
    """

    title_text = "Quiz Master – Results"

    next_question_requested = pyqtSignal()
    end_game_requested = pyqtSignal()

    # All player-related actions use the player ID
    player_info_requested = pyqtSignal(str)
    player_kicked = pyqtSignal(str)

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
        self.table_font = QFont()
        self.table_font.setPointSize(12)

        self.table_bold_font = QFont()
        self.table_bold_font.setPointSize(12)
        self.table_bold_font.setBold(True)

    def _setup_widgets(self) -> None:
        """
        Internal method. Sets up all widgets used by the screen, including styling and slots, if needed. These
        widgets are not added to any global layout in this method, however.

        Returns:
            None.
        """
        self._setup_header_widgets()
        self._setup_left_widgets()
        self._setup_right_widgets()

    def _setup_header_widgets(self) -> None:
        """
        Internal method. Sets up all widgets related to the header, including styling and slots, if needed.
        These widgets are not added to any global layout in this method, however.

        Returns:
            None.
        """
        self.heading = QLabel("Question Results")
        self.heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.heading.setStyleSheet("font-size: 36px;" "font-weight: 600;")

        self.end_game_btn = create_return_button("End Game", btn_width=80)
        self.end_game_btn.clicked.connect(self._on_end_game)

        self.next_btn = QPushButton("Next Question")
        self.next_btn.setFixedSize(140, 40)
        self.next_btn.clicked.connect(self.next_question_requested.emit)
        self.next_btn.setStyleSheet("font-size: 14px;")

        # Updated when entering screen
        self.accuracy = QLabel()
        self.accuracy.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.accuracy.setStyleSheet("font-size: 16px;" "color: #A0A0A0;")

    def _setup_left_widgets(self) -> None:
        """
        Internal method. Sets up all widgets related to the left side of the UI, including styling and slots,
        if needed. These widgets are not added to any global layout in this method, however.

        Returns:
            None.
        """
        # Left side contains statistics and feedback
        self.left_card = Card()

        # Set word wrap to ensure question does not extend beyond view and overflow
        self.question_lbl = QLabel()
        self.question_lbl.setWordWrap(True)
        self.question_lbl.setStyleSheet("font-size: 24px;" "font-weight: 600;")

        self.correct_answer = QLabel()
        self.correct_answer.setStyleSheet("font-size: 16px;" "color: #A0A0A0;")

        # Shows frequency of answers
        self.answer_bar_chart = AnswerBarChart()

        # Shows correct answer
        self.answer_button_grid = AnswerButtonGrid(AnswerButtonGridMode.RESULT)
        self.answer_button_grid.setMaximumHeight(500)

    def _setup_right_widgets(self) -> None:
        """
        Internal method. Sets up all widgets related to the right side of the UI, including styling and slots,
        if needed. These widgets are not added to any global layout in this method, however.

        Returns:
            None.
        """
        # Right side contains leaderboard
        self.right_card = Card()

        self.leaderboard_heading = QLabel("Leaderboard")
        self.leaderboard_heading.setStyleSheet("font-size: 24px;" "font-weight: 600;")

        self.leaderboard_table = QTableWidget()
        self.leaderboard_table.setFont(self.table_font)
        self.leaderboard_table.itemSelectionChanged.connect(self._on_selection_changed)

        # Hides grid lines between rows and columns
        self.leaderboard_table.setShowGrid(False)

        # Adds zebra stripes, making every other row a slightly different color
        self.leaderboard_table.setAlternatingRowColors(True)

        self.leaderboard_table.setColumnCount(4)
        self.leaderboard_table.setHorizontalHeaderLabels(
            ["Rank", "Nickname", "Gained", "Total"]
        )

        # Makes selecting a single item select the entire row
        self.leaderboard_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        # Prevents selecting multiple rows
        self.leaderboard_table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        # Prevents users from editing the table, making it read-only
        self.leaderboard_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        leaderboard_horizontal_header = self.leaderboard_table.horizontalHeader()
        leaderboard_vertical_header = self.leaderboard_table.verticalHeader()

        # Makes only nickname column able to expand, rest are fixed width
        leaderboard_horizontal_header.setSectionResizeMode(
            0, QHeaderView.ResizeMode.Fixed
        )
        leaderboard_horizontal_header.setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        leaderboard_horizontal_header.setSectionResizeMode(
            2, QHeaderView.ResizeMode.Fixed
        )
        leaderboard_horizontal_header.setSectionResizeMode(
            3, QHeaderView.ResizeMode.Fixed
        )

        # Hide vertical header and set fixed height for each item
        leaderboard_vertical_header.setVisible(False)
        leaderboard_vertical_header.setDefaultSectionSize(32)

        # Set fixed width for columns that cannot expand
        self.leaderboard_table.setColumnWidth(0, 80)
        self.leaderboard_table.setColumnWidth(2, 80)
        self.leaderboard_table.setColumnWidth(3, 80)

        self.leaderboard_table.setStyleSheet("""
            QTableWidget::item {
                padding: 6px;
            }
        """)

        # Leaderboard overlay for when the leaderboard should be hidden (typically for final question)
        self.leaderboard_blur = QLabel("Leaderboard hidden until final results!")
        self.leaderboard_blur.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.leaderboard_blur.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 255, 255, 0.08);
                border-radius: 12px;
                color: #A0A0A0;
                font-size: 18px;
                font-weight: 600;
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

    def _setup_layouts(self) -> None:
        """
        Internal method. Sets up all the layouts on this screen, adding widgets and controlling alignment, spacing,
        and stretching. The main layout is also applied as this screen's primary layout via `setLayout()`.

        Returns:
            None.
        """
        # Create child layouts
        header_layout = self._create_header_layout()

        # These are already made a child of the cards, which are added to self
        self._create_left_layout()
        self._create_right_layout()

        hbox = QHBoxLayout()
        hbox.addWidget(self.left_card, stretch=5)
        hbox.addSpacing(20)
        hbox.addWidget(self.right_card, stretch=4)

        vbox = QVBoxLayout()
        vbox.setContentsMargins(20, 20, 20, 20)
        vbox.addLayout(header_layout)
        vbox.addLayout(hbox, stretch=1)

        self.setLayout(vbox)

    def _create_header_layout(self) -> QVBoxLayout:
        """
        Internal method. Creates the header layout, adding widgets and controlling alignment, spacing,
        and stretching.

        Returns:
            The layout to add to the main layout.
        """
        # Create header using grid layout to ensure buttons and heading are aligned evenly
        nav_grid = QGridLayout()
        nav_grid.addWidget(
            self.end_game_btn, 0, 0, alignment=Qt.AlignmentFlag.AlignLeft
        )
        nav_grid.addWidget(self.heading, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        nav_grid.addWidget(self.next_btn, 0, 2, alignment=Qt.AlignmentFlag.AlignRight)
        nav_grid.setColumnStretch(0, 1)
        nav_grid.setColumnStretch(1, 0)
        nav_grid.setColumnStretch(2, 1)

        # Top row header with description
        vbox_header = QVBoxLayout()
        vbox_header.addLayout(nav_grid)
        vbox_header.addSpacing(2)
        vbox_header.addWidget(self.accuracy)
        vbox_header.addSpacing(20)

        return vbox_header

    def _create_left_layout(self) -> QVBoxLayout:
        """
        Internal method. Creates the left side layout, adding widgets and controlling alignment, spacing,
        and stretching.

        Returns:
            The layout to add to the main layout.
        """
        # Make layout a part of the left card
        vbox_left = QVBoxLayout(self.left_card)
        vbox_left.setContentsMargins(20, 20, 20, 20)
        vbox_left.addWidget(self.question_lbl)
        vbox_left.addSpacing(2)
        vbox_left.addWidget(self.correct_answer)
        vbox_left.addWidget(self.answer_bar_chart, stretch=1)
        vbox_left.addSpacing(15)
        vbox_left.addWidget(self.answer_button_grid, stretch=1)

        return vbox_left

    def _create_right_layout(self) -> QVBoxLayout:
        """
        Internal method. Creates the right side layout, adding widgets and controlling alignment, spacing,
        and stretching.

        Returns:
            The layout to add to the main layout.
        """
        # Allow switching between hiding and showing leaderboard
        self.leaderboard_stack = QStackedLayout()
        self.leaderboard_stack.addWidget(self.leaderboard_table)
        self.leaderboard_stack.addWidget(self.leaderboard_blur)

        player_btn_hbox = QHBoxLayout()
        player_btn_hbox.addWidget(self.get_info_btn)
        player_btn_hbox.addWidget(self.kick_btn)

        # Make layout a part of the right card
        vbox_right = QVBoxLayout(self.right_card)
        vbox_right.setContentsMargins(20, 20, 20, 20)
        vbox_right.addWidget(self.leaderboard_heading)
        vbox_right.addSpacing(15)
        vbox_right.addLayout(self.leaderboard_stack, stretch=1)
        vbox_right.addSpacing(2)
        vbox_right.addLayout(player_btn_hbox)

        return vbox_right

    def set_leaderboard_visible(self, visible: bool) -> None:
        """
        Set the visibility of the leaderboard. If not visible, applies an overlay on the leaderboard. Otherwise,
        shows the actual leaderboard on the UI.

        Arguments:
            visible: A boolean specifying whether or not the leaderboard itself should be visible. If True, shows
                the leaderboard, otherwise, applies an overlay. A boolean is used for this as it is good for
                a two-way decision of visible or not.

        Returns:
            None.
        """
        widget = self.leaderboard_table if visible else self.leaderboard_blur
        self.leaderboard_stack.setCurrentWidget(widget)

    def set_leaderboard_values(
        self, players: list[tuple[str, str, str, str, str]]
    ) -> None:
        """
        Set the values to display in the leaderboard table. Adds the players and their data given in `players`
        in the order they were given in to the table, and color ranks accordingly to the podium. The list is
        not sorted before being added, as it is expected to have been sorted beforehand. The player ID is
        hidden and attached to the nickname item (at column index 1) for player actions that need an identifier.

        Arguments:
            players: A list of tuples containing the player ID, rank, nickname, gained score, and total score
                of the player entry, in that order. All values are expected to be strings, despite some values,
                such as total score, making more sense as integers, due to the requirement of PyQt needing
                strings to input rows. None of the values are styled in this method, they are expected to be
                styled beforehand, if required (for example, adding a hashtag before the rank, or a plus to the
                gained points).

        Returns:
            None.
        """
        for index, (player_id, rank, nickname, gained, total) in enumerate(players):
            # Add row to the end of the table
            row = self.leaderboard_table.rowCount()
            self.leaderboard_table.insertRow(row)

            rank_item = QTableWidgetItem(rank)
            nickname_item = QTableWidgetItem(nickname)
            gained_item = QTableWidgetItem(gained)
            total_item = QTableWidgetItem(total)

            # Store hidden player ID attached to the nickname, as that relates
            # the most to the player's identity.
            nickname_item.setData(Qt.ItemDataRole.UserRole, player_id)

            color = self._rank_color(index)

            # Set text color for all items
            rank_item.setForeground(color)
            nickname_item.setForeground(color)
            gained_item.setForeground(color)
            total_item.setForeground(color)

            rank_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            nickname_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            gained_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # Add each item to its respective column
            self.leaderboard_table.setItem(row, 0, rank_item)
            self.leaderboard_table.setItem(row, 1, nickname_item)
            self.leaderboard_table.setItem(row, 2, gained_item)
            self.leaderboard_table.setItem(row, 3, total_item)

    def clear_leaderboard(self) -> None:
        """
        Reset the leaderboard table by clearing and removing all the rows.

        Returns:
            None.
        """
        self.leaderboard_table.setRowCount(0)

    def remove_player(self, player_id: str) -> bool:
        """
        Removes a player from the leaderboard table on the UI. The player ID is used for identifying the player
        from the leaderboard table, internally, rather than the nickname. The ranks of other players are updated
        when the player is removed.

        Arguments:
            player_id: A string representing a unique player ID for the player, to remove them from the
                table. A string is used as it is more versatile for IDs than an integer and allows more
                combinations in a shorter number of characters.

        Returns:
            A boolean informing whether or not the removal was successful. If the player ID was found in the
            leaderboard table and successfully removed, True is returned. If the player ID could not be found,
            False is returned instead.
        """
        for row in range(self.leaderboard_table.rowCount()):
            # Cycle through all rows and get item from the column that stores the
            # player ID, column 1 (aka nickname column).
            item = self.leaderboard_table.item(row, 1)

            # If item is valid and hidden player ID matches, remove and update ranks
            if item and item.data(Qt.ItemDataRole.UserRole) == player_id:
                self.leaderboard_table.removeRow(row)
                self._refresh_ranks()

                return True

        # No matches found
        return False

    def _on_selection_changed(self) -> None:
        """
        Internal method. Intended to be called when a player is selected or deselected from the leaderboard table.

        This method changes the state of the player management buttons to be enabled if a player has been
        selected, or disabled if a player has been deselected or not selected at all.

        Returns:
            None.
        """
        # If player is not selected, disable player buttons
        if self._get_selected_nickname_item() is None:
            self.get_info_btn.setEnabled(False)
            self.kick_btn.setEnabled(False)
        else:
            self.get_info_btn.setEnabled(True)
            self.kick_btn.setEnabled(True)

    def _on_end_game(self) -> None:
        """
        Internal method. Intended to be run when the host clicks the End Game button. Displays a warning confirmation
        dialog to ensure the host wishes to end the game prematurely, then goes directly to the final results.

        Returns:
            None.
        """
        confirm = confirm_warning(
            self,
            "Confirm Ending Quiz",
            "Are you sure you want to skip all questions? The next questions won't be shown and the game will go directly to final results.",
        )

        if confirm:
            self.end_game_requested.emit()

    def _on_get_info(self) -> None:
        """
        Internal method. Intended to be called when the Get Info button is clicked for a player.

        The button should only be enabled if a player was selected. If a player was not selected and this method
        was somehow called, it fails with an error modal box. Otherwise, it displays more advanced player
        information.

        Returns:
            None.
        """
        selected_item = self._get_selected_nickname_item()

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
        selected_item = self._get_selected_nickname_item()

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

    def _get_selected_nickname_item(self) -> QTableWidgetItem | None:
        """
        Internal method. Gets the player's nickname item from the leaderboard table that the user selected, or
        None if the user has not selected anything.

        Returns:
            A `QTableWidgetItem` of the nickname item the user selected from the leaderboard table, or None
            if nothing was selected by the user.
        """
        row = self.leaderboard_table.currentRow()

        # Nothing is selected
        if row == -1:
            return None

        # Return item at nickname column, column 1
        return self.leaderboard_table.item(row, 1)

    def _refresh_ranks(self) -> None:
        """
        Refresh the rank counts and podium colors, if the leaderboard table was updated. For example, if a
        player was removed from the table. The color scheme is the same used when setting the players in the
        leaderboard.

        Returns:
            None.
        """
        for row in range(self.leaderboard_table.rowCount()):
            color = self._rank_color(row)

            # Update rank text for the first column, which contains the rank
            rank_item = self.leaderboard_table.item(row, 0)
            if rank_item:
                rank_item.setText(f"#{row + 1}")

            # Update all cells in the row to reflect color text changes
            for column in range(self.leaderboard_table.columnCount()):
                item = self.leaderboard_table.item(row, column)
                if item:
                    item.setForeground(color)

    def _rank_color(self, index: int) -> QColor:
        """
        Get the color of the rank at the given index as a `QColor`, to match podium colors. The index provided
        should be zero-indexed, not starting from one.

        Arguments:
            index: The index of the player to give the color for. The index is expected to be zero-indexed, not
                starting from one. An integer is used as it easily gives a count for the index.

        Returns:
            The color of the row to match podium colors, as a `QColor`, which can be directly applied without
            converting it afterwards. A `QColor` is returned rather than a string for easier compatibility with
            PyQt methods.
        """
        # Color according to podium colors. Make all other ranks slightly
        # grayer rather than pure white to ensure it does not draw attention
        # away from podium colors.
        if index == 0:
            return QColor("#F5C542")
        if index == 1:
            return QColor("#C9CED6")
        if index == 2:
            return QColor("#CD7F32")
        else:
            return QColor("#D6D1C7")

    def on_enter(self, payload: ServerResultsPayload) -> None:
        # Converts from decimal to number 0-100 for percentage
        accuracy = round(payload.accuracy * 100)

        # Correct: #3DDC84
        # Incorrect: #FF5C5C
        # Change theme color depending on global accuracy
        theme_color = "#3DDC84" if accuracy >= 50 else "#FF5C5C"

        self.heading.setStyleSheet(
            f"font-size: 36px; font-weight: 600; color: {theme_color};"
        )
        self.accuracy.setText(
            f"Question {payload.question_num} / {payload.total_questions} • {accuracy}% answered correctly"
        )

        correct_answer = payload.answer_options[payload.correct_answer]

        # Make accent color darker for border to make it blend more into the background
        self.left_card.set_accent(darken_color(theme_color, factor=0.4))

        # Set question and correct answer
        self.question_lbl.setText(payload.question_text)
        self.correct_answer.setText(f"Correct answer: {correct_answer}")

        # Set frequency data for each answer
        self.answer_bar_chart.set_values(
            payload.answer_frequency, payload.correct_answer
        )

        # Set answers in button grid
        self.answer_button_grid.set_answers(payload.answer_options)
        self.answer_button_grid.set_result(payload.correct_answer)

        # Show players in leaderboard, if it isn't the last question, else, show overlay
        if payload.leaderboard is not None:
            # Style leaderboard values and convert them to strings rather than passing direct values
            leaderboard_players = []
            for player in payload.leaderboard:
                leaderboard_players.append(
                    (
                        player["player_id"],
                        f"#{player['rank']}",
                        player["nickname"],
                        f"+{player['gained']}",
                        str(player["total"]),
                    )
                )

            self.set_leaderboard_values(leaderboard_players)
        else:
            self.set_leaderboard_visible(False)

            self.get_info_btn.hide()
            self.kick_btn.hide()

        # If the question is the last question, change button text and disable
        # End Game button, as the game is technically already over and the Next
        # and End Game buttons do the same thing in this scenario.
        if payload.question_num == payload.total_questions:
            self.next_btn.setText("Final Results")
            self.end_game_btn.setDisabled(True)

    def on_leave(self) -> None:
        # Reset and re-show all widgets to prevent stale data from showing if the
        # UI doesn't update fast enough on next showing.
        self.heading.setStyleSheet("font-size: 36px;" "font-weight: 600;")
        self.accuracy.setText("")

        self.left_card.reset_accent()
        self.question_lbl.setText("")
        self.correct_answer.setText("")

        self.answer_button_grid.reset_buttons()

        self.set_leaderboard_visible(True)
        self.clear_leaderboard()

        self.get_info_btn.show()
        self.kick_btn.show()

        self.next_btn.setText("Next Question")
        self.end_game_btn.setDisabled(False)
