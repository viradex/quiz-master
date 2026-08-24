import random

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
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
from models.payloads import ServerFinalResultsPayload
from ui.components.card import Card, StatCard
from ui.screens.base_screen import BaseScreen
from utils.color import darken_color
from utils.paths import get_icons_dir


class ServerFinalResultScreen(BaseScreen):
    """
    Creates the server final results screen, inheriting BaseScreen. This screen is part of the 'server' category.

    This screen is responsible for showing final global statistics and the final global leaderboard.

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
        self.table_font = QFont()
        self.table_font.setPointSize(12)

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
        self.heading = QLabel("Final Results")
        self.heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.heading.setStyleSheet("font-size: 36px;" "font-weight: 600;")

        self.return_btn = QPushButton("Return to Menu")
        self.return_btn.setFixedSize(140, 40)
        self.return_btn.setStyleSheet("font-size: 14px;")
        self.return_btn.clicked.connect(self._on_return)

        # Updated when entering screen
        self.winner = QLabel()
        self.winner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.winner.setStyleSheet("font-size: 20px;" "color: #F5C542;")

    def _setup_left_widgets(self) -> None:
        """
        Internal method. Sets up all widgets related to the left side of the UI, including styling and slots,
        if needed. These widgets are not added to any global layout in this method, however.

        Returns:
            None.
        """
        # Left side contains leaderboard
        # Make accent color darker for border to make it blend more into the background
        self.left_card = Card(accent=darken_color("#8A5CFF", factor=0.4))

        self.leaderboard_heading = QLabel("Leaderboard")
        self.leaderboard_heading.setStyleSheet("font-size: 24px;" "font-weight: 600;")

        self.leaderboard_desc = QLabel("Final standings")
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

    def _setup_right_widgets(self) -> None:
        """
        Internal method. Sets up all widgets related to the right side of the UI, including styling and slots,
        if needed. These widgets are not added to any global layout in this method, however.

        Returns:
            None.
        """
        # Right side contains statistics
        self.right_card = Card()

        self.stats_heading = QLabel("Game Stats")
        self.stats_heading.setStyleSheet("font-size: 24px;" "font-weight: 600;")

        self.stats_desc = QLabel("Overall game stats")
        self.stats_desc.setStyleSheet("font-size: 14px;" "color: #6E6E6E;")

        # Make each stat a card that will be added to a grid, no values yet
        self.winner_stat = StatCard("Winner", "", get_icons_dir() / "trophy.png")
        self.highest_points_stat = StatCard(
            "Highest Points", "", get_icons_dir() / "star.png"
        )
        self.fastest_answer_stat = StatCard(
            "Fastest Answer", "", get_icons_dir() / "lightning.png"
        )
        self.average_accuracy_stat = StatCard(
            "Average Accuracy", "", get_icons_dir() / "bullseye.png"
        )
        self.players_stat = StatCard("Total Players", "", get_icons_dir() / "users.png")
        self.questions_stat = StatCard(
            "Total Questions", "", get_icons_dir() / "question.png"
        )

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

        # Set 5:4 ratio in favor of left card
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
        nav_grid.addWidget(self.heading, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        nav_grid.addWidget(self.return_btn, 0, 2, alignment=Qt.AlignmentFlag.AlignRight)
        nav_grid.setColumnStretch(0, 1)
        nav_grid.setColumnStretch(1, 0)
        nav_grid.setColumnStretch(2, 1)

        # Top row header with description
        vbox_header = QVBoxLayout()
        vbox_header.addLayout(nav_grid)
        vbox_header.addSpacing(2)
        vbox_header.addWidget(self.winner)
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
        vbox_left.addWidget(self.leaderboard_heading)
        vbox_left.addSpacing(2)
        vbox_left.addWidget(self.leaderboard_desc)
        vbox_left.addSpacing(15)
        vbox_left.addWidget(self.leaderboard_table, stretch=1)

        return vbox_left

    def _create_right_layout(self) -> QVBoxLayout:
        """
        Internal method. Creates the right side layout, adding widgets and controlling alignment, spacing,
        and stretching.

        Returns:
            The layout to add to the main layout.
        """
        # Grid containing each stat card
        stats_grid = QGridLayout()
        stats_grid.setSpacing(10)
        stats_grid.addWidget(self.winner_stat, 0, 0)
        stats_grid.addWidget(self.highest_points_stat, 0, 1)
        stats_grid.addWidget(self.fastest_answer_stat, 1, 0)
        stats_grid.addWidget(self.average_accuracy_stat, 1, 1)
        stats_grid.addWidget(self.players_stat, 2, 0)
        stats_grid.addWidget(self.questions_stat, 2, 1)

        # Make layout a part of the right card
        vbox_right = QVBoxLayout(self.right_card)
        vbox_right.setContentsMargins(20, 20, 20, 20)
        vbox_right.addWidget(self.stats_heading)
        vbox_right.addSpacing(2)
        vbox_right.addWidget(self.stats_desc)
        vbox_right.addSpacing(15)
        vbox_right.addLayout(stats_grid)
        vbox_right.addStretch(1)

        return vbox_right

    def set_leaderboard_values(self, players: list[tuple[str, str, str]]) -> None:
        """
        Set the values to display in the leaderboard table. Adds the players and their data given in `players`
        in the order they were given in to the table, and highlights the podium with specialized colors and
        bolding. The list is not sorted before being added, as it is expected to have been sorted beforehand.

        Arguments:
            players: A list of tuples containing the rank, nickname, and total score of the player entry, in
                that order. All values are expected to be strings, despite some values, such as total score,
                making more sense as integers, due to the requirement of PyQt needing strings to input rows.
                None of the values are styled in this method, they are expected to be styled beforehand, if
                required (for example, adding a hashtag before the rank).

        Returns:
            None.
        """
        for index, (rank, nickname, total) in enumerate(players):
            # Add row to the end of the table
            row = self.leaderboard_table.rowCount()
            self.leaderboard_table.insertRow(row)

            rank_item = QTableWidgetItem(rank)
            nickname_item = QTableWidgetItem(nickname)
            total_item = QTableWidgetItem(total)

            # Color according to podium colors. Make all other ranks slightly
            # grayer rather than pure white to ensure it does not draw attention
            # away from podium colors.
            if index == 0:
                color = QColor("#F5C542")
            elif index == 1:
                color = QColor("#C9CED6")
            elif index == 2:
                color = QColor("#CD7F32")
            else:
                color = QColor("#D6D1C7")

            # Set text color for all items
            rank_item.setForeground(color)
            nickname_item.setForeground(color)
            total_item.setForeground(color)

            # Bold rank rows if they are on the podium
            if index <= 2:
                for item in (rank_item, nickname_item, total_item):
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)

            rank_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            nickname_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # Add each item to its respective column
            self.leaderboard_table.setItem(row, 0, rank_item)
            self.leaderboard_table.setItem(row, 1, nickname_item)
            self.leaderboard_table.setItem(row, 2, total_item)

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

    def on_enter(self, payload: ServerFinalResultsPayload) -> None:
        # Converts from decimal to number 0-100 for percentage
        average_accuracy = round(payload.average_accuracy * 100)

        # Used for 1st place person message
        message_choices = [
            "{player} takes 1st place!",
            "{player} claims the top spot!",
            "{player} secures the victory!",
            "{player} takes the crown!",
            "{player} tops the leaderboard!",
        ]

        # Randomly choose text and replace placeholder player nickname with actual nickname
        winner_text = random.choice(message_choices).format(player=payload.winner)
        self.winner.setText(winner_text)

        # Statistic cards require a string
        self.winner_stat.set_value(payload.winner)
        self.highest_points_stat.set_value(str(payload.highest_points))

        # If the quiz was ended without any submissions, fastest_answer is None
        if payload.fastest_answer is not None:
            self.fastest_answer_stat.set_value(f"{payload.fastest_answer:.2f}s")
        else:
            self.fastest_answer_stat.set_value("-")

        self.average_accuracy_stat.set_value(f"{average_accuracy}%")
        self.players_stat.set_value(str(payload.total_players))
        self.questions_stat.set_value(str(payload.total_questions))

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

        self.set_leaderboard_values(leaderboard_players)

    def on_leave(self) -> None:
        # Reset and re-show all widgets to prevent stale data from showing if the
        # UI doesn't update fast enough on next showing.
        self.winner.setText("")

        self.clear_leaderboard()

        self.winner_stat.set_value("")
        self.highest_points_stat.set_value("")
        self.fastest_answer_stat.set_value("")
        self.average_accuracy_stat.set_value("")
        self.players_stat.set_value("")
        self.questions_stat.set_value("")
