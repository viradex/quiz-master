"""
final_result.py

The server final results UI screen. Shows the final statistics relating to the game as a whole and
the final global leaderboard.
"""

import random

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.app.screen_ids import Screen
from models.payloads import ClientFinalResultsPayload
from ui.components.card import Card, StatCard
from ui.screens.base_screen import BaseScreen
from utils.color import darken_color
from utils.feedback_generator import feedback_generator
from utils.formatting import to_ordinal
from utils.paths import get_icons_dir


class ClientFinalResultScreen(BaseScreen):
    """
    Creates the client final results screen, inheriting BaseScreen. This screen is part of the 'client' category.

    This screen is responsible for showing statistics and the surrounding leaderboard to the player, as well
    as their position in the leaderboard.

    Attributes:
        title_text: The default text of the screen when entered. A string is used as that is what the
            title changing code requires.

    Arguments:
        parent: The parent of this screen, or None. Typically, this is the MainWindow.
    """

    title_text = "Quiz Master – Final Results"

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
        self.feedback_font = QFont()
        self.feedback_font.setPointSize(11)

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
        # Updated when entering screen
        self.ordinal_position = QLabel()
        self.ordinal_position.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ordinal_position.setStyleSheet("font-size: 42px;" "font-weight: 600;")

        self.return_btn = QPushButton("Return to Menu")
        self.return_btn.setFixedSize(140, 40)
        self.return_btn.clicked.connect(self._on_return)
        self.return_btn.setStyleSheet("font-size: 14px;")

        self.position_feedback = QLabel()
        self.position_feedback.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.position_feedback.setStyleSheet("font-size: 16px;" "color: #A0A0A0;")

    def _setup_left_widgets(self) -> None:
        """
        Internal method. Sets up all widgets related to the left side of the UI, including styling and slots,
        if needed. These widgets are not added to any global layout in this method, however.

        Returns:
            None.
        """
        # Left side contains statistics and feedback
        self.left_card = Card()

        self.stats_heading = QLabel("Your Performance")
        self.stats_heading.setStyleSheet("font-size: 24px;" "font-weight: 600;")

        self.nickname = QLabel()
        self.nickname.setStyleSheet("font-size: 16px;" "color: #6E6E6E;")

        self.rank_stat = StatCard("Rank", "", get_icons_dir() / "trophy.png")
        self.points_stat = StatCard("Points", "", get_icons_dir() / "star.png")
        self.correct_stat = StatCard("Correct", "", get_icons_dir() / "correct.png")
        self.accuracy_stat = StatCard("Accuracy", "", get_icons_dir() / "bullseye.png")

        # Enable word wrap as feedback can sometimes exceed card width
        self.feedback = QLabel()
        self.feedback.setWordWrap(True)
        self.feedback.setFont(self.feedback_font)
        self.feedback.setStyleSheet("""
            QLabel {
                background-color: #262626;
                border-radius: 10px;
                padding: 12px;
                color: #C8C8C8;
            }
        """)

    def _setup_right_widgets(self) -> None:
        """
        Internal method. Sets up all widgets related to the right side of the UI, including styling and slots,
        if needed. These widgets are not added to any global layout in this method, however.

        Returns:
            None.
        """
        # Right side contains leaderboard
        self.right_card = Card()

        self.leaderboard_heading = QLabel("Leaderboard Snapshot")
        self.leaderboard_heading.setStyleSheet("font-size: 24px;" "font-weight: 600;")

        self.leaderboard_desc = QLabel("Nearby rankings")
        self.leaderboard_desc.setStyleSheet("font-size: 14px;" "color: #6E6E6E;")

        self.leaderboard_table = QTableWidget()
        self.leaderboard_table.setFont(self.table_font)

        # Hides grid lines between rows and columns
        self.leaderboard_table.setShowGrid(False)

        # Adds zebra stripes, making every other row a slightly different color
        self.leaderboard_table.setAlternatingRowColors(True)

        self.leaderboard_table.setColumnCount(3)
        self.leaderboard_table.setHorizontalHeaderLabels(["Rank", "Nickname", "Total"])

        # Prevents users from editing the table, making it read-only
        self.leaderboard_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        # Prevents users from selecting a row or item
        self.leaderboard_table.setSelectionMode(
            QAbstractItemView.SelectionMode.NoSelection
        )

        # Prevents scrollbar from showing, as the height should adapt via _update_table_height()
        self.leaderboard_table.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
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

        # Hide vertical header and set fixed height for each item
        leaderboard_vertical_header.setVisible(False)
        leaderboard_vertical_header.setDefaultSectionSize(32)

        # Set fixed width for columns that cannot expand
        self.leaderboard_table.setColumnWidth(0, 120)
        self.leaderboard_table.setColumnWidth(2, 120)

        self.leaderboard_table.setStyleSheet("""
            QTableWidget::item {
                padding: 6px;
            }
        """)

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

        # Set 5:4 ratio in favor of left card
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
            self.ordinal_position, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter
        )
        nav_grid.addWidget(self.return_btn, 0, 2, alignment=Qt.AlignmentFlag.AlignRight)
        nav_grid.setColumnStretch(0, 1)
        nav_grid.setColumnStretch(1, 0)
        nav_grid.setColumnStretch(2, 1)

        # Top row header with description
        vbox_header = QVBoxLayout()
        vbox_header.addLayout(nav_grid)
        vbox_header.addSpacing(2)
        vbox_header.addWidget(self.position_feedback)
        vbox_header.addSpacing(20)

        return vbox_header

    def _create_left_layout(self) -> QVBoxLayout:
        """
        Internal method. Creates the left side layout, adding widgets and controlling alignment, spacing,
        and stretching.

        Returns:
            The layout to add to the main layout.
        """
        stats_grid = QGridLayout()
        stats_grid.setSpacing(10)
        stats_grid.addWidget(self.rank_stat, 0, 0)
        stats_grid.addWidget(self.points_stat, 0, 1)
        stats_grid.addWidget(self.correct_stat, 1, 0)
        stats_grid.addWidget(self.accuracy_stat, 1, 1)

        # Make layout a part of the left card
        vbox_left = QVBoxLayout(self.left_card)
        vbox_left.setContentsMargins(20, 20, 20, 20)
        vbox_left.addWidget(self.stats_heading)
        vbox_left.addSpacing(2)
        vbox_left.addWidget(self.nickname)
        vbox_left.addSpacing(15)
        vbox_left.addLayout(stats_grid)
        vbox_left.addSpacing(15)
        vbox_left.addWidget(self.feedback)
        vbox_left.addStretch(1)

        return vbox_left

    def _create_right_layout(self) -> QVBoxLayout:
        """
        Internal method. Creates the right side layout, adding widgets and controlling alignment, spacing,
        and stretching.

        Returns:
            The layout to add to the main layout.
        """
        # Make layout a part of the right card
        vbox_right = QVBoxLayout(self.right_card)
        vbox_right.setContentsMargins(20, 20, 20, 20)
        vbox_right.addWidget(self.leaderboard_heading)
        vbox_right.addSpacing(2)
        vbox_right.addWidget(self.leaderboard_desc)
        vbox_right.addSpacing(15)
        vbox_right.addWidget(self.leaderboard_table)
        vbox_right.addSpacing(20)
        vbox_right.addWidget(self.return_btn, alignment=Qt.AlignmentFlag.AlignRight)
        vbox_right.addStretch(1)

        return vbox_right

    def set_leaderboard_values(
        self, players: list[tuple[str, str, str]], own_nickname: str
    ) -> None:
        """
        Set the values to display in the leaderboard table. Adds the players and their data given in `players`
        in the order they were given in to the table, and highlights the own player's nickname bold and with
        a suffixed '(you)' at the end. The list is not sorted before being added, as it is expected to have
        been sorted beforehand.

        The table height is automatically adjusted after adding all the values to ensure it exactly fits the
        data in the table: no more, no less.

        Arguments:
            players: A list of tuples containing the rank, nickname, and total score of the player entry, in
                that order. All values are expected to be strings, despite some values, such as total score,
                making more sense as integers, due to the requirement of PyQt needing strings to input rows.
                None of the values are styled in this method, they are expected to be styled beforehand, if
                required (for example, adding a hashtag before the rank).

            own_nickname: A string representing the nickname of the current player. The matching row is
                highlighted. There is no enforcement for no matches or multiple matches which are highlighted.
                A string is used as it can be easily used for comparisons against the nickname in `players`.

        Returns:
            None.
        """
        for rank, nickname, total in players:
            # Add row to the end of the table
            row = self.leaderboard_table.rowCount()
            self.leaderboard_table.insertRow(row)

            # Suffix '(you)' if the nickname matches the own nickname
            display_nickname = (
                f"{nickname} (you)" if nickname == own_nickname else nickname
            )

            rank_item = QTableWidgetItem(rank)
            nickname_item = QTableWidgetItem(display_nickname)
            total_item = QTableWidgetItem(total)

            rank_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            nickname_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # Bold entire row if it matches the nickname
            if nickname == own_nickname:
                rank_item.setFont(self.table_bold_font)
                nickname_item.setFont(self.table_bold_font)
                total_item.setFont(self.table_bold_font)

            # Add each item to its respective column
            self.leaderboard_table.setItem(row, 0, rank_item)
            self.leaderboard_table.setItem(row, 1, nickname_item)
            self.leaderboard_table.setItem(row, 2, total_item)

        # Update table height to ensure all rows can be seen
        self._update_leaderboard_height()

    def clear_leaderboard(self) -> None:
        """
        Reset the leaderboard table by clearing and removing all the rows.

        Returns:
            None.
        """
        self.leaderboard_table.setRowCount(0)

    def _on_return(self) -> None:
        """
        Internal method. Intended to be called when pressing the Return button. Opens the main menu screen.

        Returns:
            None.
        """
        self.reset_status()
        self.go_to(Screen.COMMON_MENU)

    def _update_leaderboard_height(self) -> None:
        """
        Update leaderboard table height based on the number of rows in the table. Calculates the height of the
        header, rows, and borders, to set the fixed height as accurate as possible.

        Returns:
            None.
        """
        # Adapt all rows to fit their contents
        self.leaderboard_table.resizeRowsToContents()

        # Get height of the column header
        total = self.leaderboard_table.horizontalHeader().height()

        # Get row height of each row in the leaderboard title, and add them together
        total += sum(
            self.leaderboard_table.rowHeight(i)
            for i in range(self.leaderboard_table.rowCount())
        )

        # Get border width, and multiply by two as the border is on the top and bottom
        total += self.leaderboard_table.frameWidth() * 2

        # Change height of table to reflect new calculated height to ensure it isn't too big or small
        self.leaderboard_table.setFixedHeight(total)

    def on_enter(self, payload: ClientFinalResultsPayload) -> None:
        # Gold: #F5C542
        # Silver: #C9CED6
        # Bronze: #CD7F32
        # Purple: #8A5CFF
        if payload.rank == 1:
            theme_color = "#F5C542"
        elif payload.rank == 2:
            theme_color = "#C9CED6"
        elif payload.rank == 3:
            theme_color = "#CD7F32"
        else:
            theme_color = "#8A5CFF"

        # Used for any place below 3rd place
        message_choices = [
            "Nice effort!",
            "Well played!",
            "Good game!",
            "Thanks for playing!",
            "Great participation!",
        ]

        # Converts from decimal to number 0-100 for percentage
        accuracy = round(payload.accuracy * 100)

        # Set position heading and apply special color only if on podium
        self.ordinal_position.setText(f"{to_ordinal(payload.rank)} Place!")
        if payload.on_podium:
            self.ordinal_position.setStyleSheet(
                f"font-size: 42px; font-weight: 600; color: {theme_color};"
            )

        # Show certain message if on podium, else show random message
        if payload.on_podium:
            self.position_feedback.setText("You finished on the podium!")
        else:
            self.position_feedback.setText(random.choice(message_choices))

        # Make accent color darker for border to make it blend more into the background
        self.left_card.set_accent(darken_color(theme_color, factor=0.4))

        self.nickname.setText(f"Nickname: {payload.nickname}")

        # Setup statistics
        self.rank_stat.set_value(f"#{payload.rank}")
        self.points_stat.set_value(f"{payload.total_points}")
        self.correct_stat.set_value(
            f"{payload.total_correct} / {payload.total_questions}"
        )
        self.accuracy_stat.set_value(f"{accuracy}%")

        # Set custom feedback based on certain cases as a sentence
        self.feedback.setText(
            feedback_generator(
                payload.on_podium,
                payload.is_first,
                payload.is_last,
                payload.behind_nickname,
                payload.points_behind,
            )
        )

        # Style leaderboard values and convert them to strings rather than passing direct values
        leaderboard_players = []
        for player in payload.leaderboard:
            leaderboard_players.append(
                (
                    f"#{player['rank']}",
                    player["nickname"],
                    str(player["total"]),
                )
            )

        self.set_leaderboard_values(leaderboard_players, payload.nickname)

    def on_leave(self) -> None:
        # Reset and re-show all widgets to prevent stale data from showing if the
        # UI doesn't update fast enough on next showing.
        self.ordinal_position.setText("")
        self.ordinal_position.setStyleSheet(
            "font-size: 42px;" "font-weight: 600;" "color: white;"
        )

        self.position_feedback.setText("")

        self.left_card.reset_accent()
        self.nickname.setText("")

        self.rank_stat.set_value("")
        self.points_stat.set_value("")
        self.correct_stat.set_value("")
        self.accuracy_stat.set_value("")

        self.feedback.setText("")

        self.clear_leaderboard()
