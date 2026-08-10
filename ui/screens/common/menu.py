"""
menu.py

The menu UI screen. The starting screen of the app, giving easy access to the primary functions of
the application.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.app.screen_ids import Screen
from ui.screens.base_screen import BaseScreen


class CommonMenuScreen(BaseScreen):
    """
    Creates the menu screen, inheriting BaseScreen. This screen is part of the 'common' category.

    This screen is responsible for giving users easy access to the primary functions of the application
    when entering for the first time and when navigating throughout the program.

    Attributes:
        started_server: A `pyqtSignal` that emits when the user clicks the Host button. No arguments
            are provided.

    Arguments:
        parent: The parent of this screen, or None. Typically, this is the MainWindow.
    """

    started_server = pyqtSignal()

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

        self.desc_font = QFont()
        self.desc_font.setPointSize(14)

    def _setup_widgets(self) -> None:
        """
        Internal method. Sets up all widgets used by the screen, including styling and slots, if needed. These
        widgets are not added to any global layout in this method, however.

        Returns:
            None.
        """
        # Top heading
        self.title = QLabel("Welcome to Quiz Master!")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setFont(self.title_font)

        self.desc = QLabel("Choose how you want to play:")
        self.desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.desc.setFont(self.desc_font)

        # Buttons selection
        # Large buttons
        self.join_btn = QPushButton("Join Lobby")
        self.join_btn.setFixedSize(275, 60)
        self.join_btn.setStyleSheet("font-size: 22px;")
        self.join_btn.clicked.connect(lambda: self.go_to(Screen.CLIENT_SETUP))

        self.host_btn = QPushButton("Host Game")
        self.host_btn.setFixedSize(275, 60)
        self.host_btn.setStyleSheet("font-size: 22px;")
        self.host_btn.clicked.connect(self.started_server.emit)

        # Medium buttons
        self.manage_quizzes_btn = QPushButton("Manage Quizzes")
        self.manage_quizzes_btn.setFixedSize(275, 45)
        self.manage_quizzes_btn.setStyleSheet("font-size: 16px;")
        self.manage_quizzes_btn.clicked.connect(
            lambda: self.go_to(Screen.COMMON_QUIZ_MANAGER)
        )

        # Small buttons
        self.about_btn = QPushButton("About")
        self.about_btn.setFixedSize(135, 35)
        self.about_btn.setStyleSheet("font-size: 12px;")
        self.about_btn.clicked.connect(lambda: self.go_to(Screen.COMMON_ABOUT))

        self.exit_btn = QPushButton("Exit")
        self.exit_btn.setFixedSize(135, 35)
        self.exit_btn.setStyleSheet("font-size: 12px;")
        self.exit_btn.clicked.connect(self._on_exit_clicked)

    def _setup_layouts(self) -> None:
        """
        Internal method. Sets up all the layouts on this screen, adding widgets and controlling alignment, spacing,
        and stretching. The main layout is also applied as this screen's primary layout via `setLayout()`.

        Returns:
            None.
        """
        # Add stretch on both left and right to center buttons
        small_btn_hbox = QHBoxLayout()
        small_btn_hbox.addStretch()
        small_btn_hbox.addWidget(self.about_btn)
        small_btn_hbox.addWidget(self.exit_btn)
        small_btn_hbox.addStretch()

        vbox = QVBoxLayout()
        vbox.setContentsMargins(20, 20, 20, 20)

        # Add 1:2 ratio stretch to make bottom have more space than top, aligning more
        # with the brain's perceived center rather than the perfect geometric center,
        # which can look 'off' for users. Align all widgets to center of page.
        vbox.addStretch(1)
        vbox.addWidget(self.title)
        vbox.addSpacing(10)
        vbox.addWidget(self.desc)
        vbox.addSpacing(20)
        vbox.addWidget(self.join_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        vbox.addSpacing(5)
        vbox.addWidget(self.host_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        vbox.addSpacing(30)
        vbox.addWidget(self.manage_quizzes_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        vbox.addSpacing(5)
        vbox.addLayout(small_btn_hbox)
        vbox.addStretch(2)

        self.setLayout(vbox)

    def _on_exit_clicked(self) -> None:
        """
        Internal method. Intended to be run when the user clicks the Exit button. Confirms that the user wishes
        to exit the application, then exits if they confirm.

        Returns:
            None.
        """
        confirm = self.show_question(
            "Exit Quiz Master?",
            "Are you sure you want to exit Quiz Master?",
            default="yes",
        )

        if confirm:
            QApplication.exit()
