from PyQt6.QtWidgets import (
    QLabel,
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
from ui.components.spinner import Spinner
from ui.components.button import LeaveButton


class ClientLobbyScreen(BaseScreen):
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

        table_font = QFont()
        table_font.setPointSize(12)

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

        # TODO only for prototype
        data = [
            "Viradex (you)",
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

            if value.endswith("(you)"):
                font = item.font()
                font.setBold(True)
                item.setFont(font)

            self.lobby_table.setItem(row, 0, item)

        connected_font = QFont()
        connected_font.setPointSize(8)

        self.connection_details = QLabel("Connected to 127.0.0.1:7878")
        self.connection_details.setFont(connected_font)

        vbox_left = QVBoxLayout()
        vbox_left.addWidget(title)

        vbox_left.addSpacing(10)
        vbox_left.addWidget(self.lobby_table, stretch=1)
        vbox_left.addStretch()
        vbox_left.addSpacing(20)
        vbox_left.addWidget(self.connection_details)

        ### RIGHT SIDE ###
        waiting_font = QFont()
        waiting_font.setPointSize(18)

        waiting_lbl = QLabel("Waiting for the host to start the game...")
        waiting_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        waiting_lbl.setFont(waiting_font)

        self.spinner = Spinner(self, size=60)

        status_lbl = QLabel("Connected to server. Game will begin shortly.")
        status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_lbl.setStyleSheet("font-size: 14px;" "color: #A7A7A7;")

        leave_btn = LeaveButton("Leave Lobby", btn_width=100)
        leave_btn.confirm_leave.connect(lambda: self.go_to(Screens.COMMON_MENU))

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

    def on_enter(self):
        self.spinner.start()

    def on_leave(self):
        self.spinner.stop()
