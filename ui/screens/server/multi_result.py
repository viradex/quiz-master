from PyQt6.QtWidgets import (
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QMessageBox,
    QStackedLayout,
    QAbstractItemView,
    QHeaderView,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from ui.screens.base_screen import BaseScreen
from ui.components.answer_bar_chart import AnswerBarChart
from ui.components.answer_button_grid import AnswerButtonGrid
from ui.components.card import Card
from models.payloads import ServerResultsPayload

from ui.components.dialogs import confirm_warning
from ui.components.button import create_return_button
from utils.color import darken_color


class ServerMultiResultScreen(BaseScreen):
    title_text = "Quiz Master – Results"

    next_question_requested = pyqtSignal()
    end_game_requested = pyqtSignal()

    player_info_requested = pyqtSignal(str)
    player_kicked = pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setup_ui()

    def setup_ui(self) -> None:
        ## FONTS SETUP ##
        table_font = QFont()
        table_font.setPointSize(12)

        table_bold_font = QFont()
        table_bold_font.setPointSize(12)
        table_bold_font.setBold(True)

        ## WIDGETS SETUP ##
        # Header
        self.heading = QLabel("Question Results")
        self.heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.heading.setStyleSheet("font-size: 36px;" "font-weight: 600;")

        self.end_game_btn = create_return_button("End Game", btn_width=80)
        self.end_game_btn.clicked.connect(self.on_end_game)

        self.next_btn = QPushButton("Next Question")
        self.next_btn.setFixedSize(140, 40)
        self.next_btn.clicked.connect(self.on_next_question)
        self.next_btn.setStyleSheet("font-size: 14px;")

        self.accuracy = QLabel()
        self.accuracy.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.accuracy.setStyleSheet("font-size: 16px;" "color: #A0A0A0;")

        # Left side
        self.left_card = Card()

        self.question_lbl = QLabel()
        self.question_lbl.setWordWrap(True)
        self.question_lbl.setStyleSheet("font-size: 24px;" "font-weight: 600;")

        self.correct_answer = QLabel()
        self.correct_answer.setStyleSheet("font-size: 16px;" "color: #A0A0A0;")

        self.answer_bar_chart = AnswerBarChart()

        self.answer_button_grid = AnswerButtonGrid("result")
        self.answer_button_grid.setMaximumHeight(500)

        # Right side
        right_card = Card()

        leaderboard_heading = QLabel("Leaderboard")
        leaderboard_heading.setStyleSheet("font-size: 24px;" "font-weight: 600;")

        self.leaderboard_table = QTableWidget()
        self.leaderboard_table.setFont(table_font)
        self.leaderboard_table.setShowGrid(False)
        self.leaderboard_table.setAlternatingRowColors(True)
        self.leaderboard_table.setColumnCount(4)
        self.leaderboard_table.setHorizontalHeaderLabels(
            ["Rank", "Nickname", "Gained", "Total"]
        )
        self.leaderboard_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.leaderboard_table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.leaderboard_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.leaderboard_table.itemSelectionChanged.connect(self.on_selection_changed)

        self.leaderboard_table.verticalHeader().setVisible(False)
        self.leaderboard_table.verticalHeader().setDefaultSectionSize(32)

        header = self.leaderboard_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)

        self.leaderboard_table.setColumnWidth(0, 80)
        self.leaderboard_table.setColumnWidth(2, 80)
        self.leaderboard_table.setColumnWidth(3, 80)
        self.leaderboard_table.setStyleSheet("""
            QTableWidget::item {
                padding: 6px;
            }
        """)

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

        self.leaderboard_stack = QStackedLayout()
        self.leaderboard_stack.addWidget(self.leaderboard_table)
        self.leaderboard_stack.addWidget(self.leaderboard_blur)

        self.get_info_btn = QPushButton("Get Info")
        self.get_info_btn.setStyleSheet("font-size: 14px;")
        self.get_info_btn.setDisabled(True)
        self.get_info_btn.clicked.connect(self.on_get_info)

        self.kick_btn = QPushButton("Kick Player")
        self.kick_btn.setStyleSheet("font-size: 14px;")
        self.kick_btn.setDisabled(True)
        self.kick_btn.clicked.connect(self.on_kick_player)

        # Hbox layout for buttons above (not in layouts section for easier readability)
        player_btn_hbox = QHBoxLayout()
        player_btn_hbox.addWidget(self.get_info_btn)
        player_btn_hbox.addWidget(self.kick_btn)

        ## LAYOUTS SETUP ##
        nav_grid = QGridLayout()
        nav_grid.addWidget(
            self.end_game_btn, 0, 0, alignment=Qt.AlignmentFlag.AlignLeft
        )
        nav_grid.addWidget(self.heading, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        nav_grid.addWidget(self.next_btn, 0, 2, alignment=Qt.AlignmentFlag.AlignRight)
        nav_grid.setColumnStretch(0, 1)
        nav_grid.setColumnStretch(1, 0)
        nav_grid.setColumnStretch(2, 1)

        vbox_header = QVBoxLayout()
        vbox_header.addLayout(nav_grid)
        vbox_header.addSpacing(2)
        vbox_header.addWidget(self.accuracy)
        vbox_header.addSpacing(20)

        vbox_left = QVBoxLayout(self.left_card)
        vbox_left.setContentsMargins(20, 20, 20, 20)
        vbox_left.addWidget(self.question_lbl)
        vbox_left.addSpacing(2)
        vbox_left.addWidget(self.correct_answer)
        vbox_left.addWidget(self.answer_bar_chart, stretch=1)
        vbox_left.addSpacing(15)
        vbox_left.addWidget(self.answer_button_grid, stretch=1)

        vbox_right = QVBoxLayout(right_card)
        vbox_right.setContentsMargins(20, 20, 20, 20)
        vbox_right.addWidget(leaderboard_heading)
        vbox_right.addSpacing(15)
        vbox_right.addLayout(self.leaderboard_stack, stretch=1)
        vbox_right.addSpacing(2)
        vbox_right.addLayout(player_btn_hbox)

        hbox = QHBoxLayout()
        hbox.addWidget(self.left_card, 5)
        hbox.addSpacing(20)
        hbox.addWidget(right_card, 4)

        vbox = QVBoxLayout()
        vbox.setContentsMargins(20, 20, 20, 20)
        vbox.addLayout(vbox_header)
        vbox.addLayout(hbox, 1)

        self.setLayout(vbox)

    def set_leaderboard_hidden(self, hidden: bool) -> None:
        """Whether to show the leaderboard table or the leaderboard blur overlay to hide the table."""
        if hidden:
            self.leaderboard_stack.setCurrentWidget(self.leaderboard_blur)
        else:
            self.leaderboard_stack.setCurrentWidget(self.leaderboard_table)

    def show_leaderboard_values(
        self, players: list[tuple[str, str, str, str, str]]
    ) -> None:
        """
        Show the entries in the leaderboard table, and color ranks accordingly to the podium.
        The players list should contain tuples with this info in the following order: `(player_id, rank, name, gained, total)`.
        """
        for index, (player_id, rank, name, gained, total) in enumerate(players):
            row = self.leaderboard_table.rowCount()
            self.leaderboard_table.insertRow(row)

            rank_item = QTableWidgetItem(rank)
            name_item = QTableWidgetItem(name)
            gained_item = QTableWidgetItem(gained)
            total_item = QTableWidgetItem(total)

            # Store hidden player ID
            name_item.setData(Qt.ItemDataRole.UserRole, player_id)

            # Color according to podium
            if index == 0:
                color = QColor("#F5C542")
            elif index == 1:
                color = QColor("#C9CED6")
            elif index == 2:
                color = QColor("#CD7F32")
            else:
                color = QColor("#D6D1C7")

            rank_item.setForeground(color)
            name_item.setForeground(color)
            gained_item.setForeground(color)
            total_item.setForeground(color)

            rank_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            gained_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.leaderboard_table.setItem(row, 0, rank_item)
            self.leaderboard_table.setItem(row, 1, name_item)
            self.leaderboard_table.setItem(row, 2, gained_item)
            self.leaderboard_table.setItem(row, 3, total_item)

    def clear_leaderboard(self) -> None:
        """Remove all rows in the leaderboard table."""
        self.leaderboard_table.setRowCount(0)

    def remove_player(self, player_id: str) -> bool:
        """Remove a player from the leaderboard."""
        for row in range(self.leaderboard_table.rowCount()):
            item = self.leaderboard_table.item(row, 1)

            if item.data(Qt.ItemDataRole.UserRole) == player_id:
                self.leaderboard_table.removeRow(row)
                return True

        return False

    def on_selection_changed(self) -> None:
        # If player is selected, enable player buttons
        if self._get_selected_player_item() is not None:
            self.get_info_btn.setDisabled(False)
            self.kick_btn.setDisabled(False)
        else:
            self.get_info_btn.setDisabled(True)
            self.kick_btn.setDisabled(True)

    def on_next_question(self) -> None:
        self.next_question_requested.emit()

    def on_end_game(self) -> None:
        """Displays a warning modal box before closing the server."""
        confirm = confirm_warning(
            self,
            "Confirm Ending Quiz",
            "Are you sure you want to skip all questions? The next questions won't be shown and the game will go directly to final results.",
        )

        if confirm:
            self.end_game_requested.emit()

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

    def _get_selected_player_item(self) -> QTableWidgetItem | None:
        """Get the selected player item from the leaderboard table."""
        row = self.leaderboard_table.currentRow()

        # Nothing is selected
        if row == -1:
            return None

        return self.leaderboard_table.item(row, 1)

    def _update_ranks(self):
        """Refresh ranks when a player is removed from the leaderboard."""
        for row in range(self.leaderboard_table.rowCount()):
            rank_item = self.leaderboard_table.item(row, 0)
            if rank_item:
                rank_item.setText(f"#{row + 1}")

    def on_enter(self, payload: ServerResultsPayload) -> None:
        # Correct: #3DDC84
        # Incorrect: #FF5C5C

        # Convert accuracy to percentage, and change theme color depending on global accuracy
        accuracy = round(payload.accuracy * 100)
        theme_color = "#3DDC84" if accuracy >= 50 else "#FF5C5C"

        self.heading.setStyleSheet(
            f"font-size: 36px; font-weight: 600; color: {theme_color};"
        )
        self.accuracy.setText(
            f"Question {payload.question_num} / {payload.total_questions} • {accuracy}% answered correctly"
        )

        correct_answer = payload.answer_options[payload.correct_answer]

        self.left_card.set_accent(darken_color(theme_color, factor=0.6))
        self.question_lbl.setText(payload.question_text)
        self.correct_answer.setText(f"Correct answer: {correct_answer}")

        self.answer_bar_chart.set_values(
            payload.answer_frequency, payload.correct_answer
        )

        self.answer_button_grid.set_answers(payload.answer_options)
        self.answer_button_grid.set_result(
            payload.correct_answer, payload.correct_answer
        )

        # Show players in leaderboard, if it isn't the last question, else, show overlay
        if payload.leaderboard is not None:
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

            self.show_leaderboard_values(leaderboard_players)
        else:
            self.set_leaderboard_hidden(True)

            self.get_info_btn.hide()
            self.kick_btn.hide()

        # If the question is the last question, change button text
        if payload.question_num == payload.total_questions:
            self.next_btn.setText("Final Results")
            self.end_game_btn.setDisabled(True)

    def on_leave(self) -> None:
        self.heading.setStyleSheet("font-size: 36px;" "font-weight: 600;")
        self.accuracy.setText("")

        self.left_card.reset_accent()
        self.question_lbl.setText("")
        self.correct_answer.setText("")

        self.answer_button_grid.reset_buttons()

        self.set_leaderboard_hidden(False)
        self.clear_leaderboard()

        self.get_info_btn.setHidden(False)
        self.kick_btn.setHidden(False)

        self.next_btn.setText("Next Question")
        self.end_game_btn.setDisabled(False)
