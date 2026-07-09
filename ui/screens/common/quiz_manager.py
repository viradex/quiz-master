from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QLineEdit,
    QComboBox,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QScrollArea,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

from core.app.screen_ids import Screens
from ui.screens.base_screen import BaseScreen
from ui.components.card import Card, QuizCard
from models.quiz import Quiz

from ui.components.button import create_return_button


class CommonQuizManagerScreen(BaseScreen):
    title_text = "Quiz Master – Manage Quizzes"

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.icons_path = self.base_dir / "assets" / "icons"

        self.setup_ui()

    def setup_ui(self) -> None:
        ## FONTS SETUP ##
        list_mod_font = QFont()
        list_mod_font.setPointSize(10)

        ## WIDGETS SETUP ##
        # Header
        heading = QLabel("Manage Quizzes")
        heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        heading.setStyleSheet("font-size: 36px;" "font-weight: 600;")

        return_btn = create_return_button("Return to Menu", btn_width=120)
        return_btn.clicked.connect(lambda: self.go_to(Screens.COMMON_MENU))

        create_btn = QPushButton("Create New Quiz")
        create_btn.setFixedSize(180, 40)
        create_btn.clicked.connect(lambda: self.go_to(Screens.COMMON_QUIZ_SETUP))
        create_btn.setStyleSheet("font-size: 14px;")

        description = QLabel("Create and edit your quizzes!")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setStyleSheet("font-size: 16px;" "color: #A0A0A0;")

        # List modification
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search quizzes...")
        self.search_input.setFixedHeight(35)
        self.search_input.setFont(list_mod_font)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e1e;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                padding: 4px 8px;
            }
                                        
            QLineEdit::placeholder {
                color: #888;
            }
        """)
        search_icon = self.icons_path / "search.png"
        self.search_input.addAction(
            QIcon(search_icon.as_posix()), QLineEdit.ActionPosition.LeadingPosition
        )

        sort_by_lbl = QLabel("Sort by:")
        sort_by_lbl.setStyleSheet("font-size: 14px;" "color: #888;")

        # TODO down arrow appears broken due to styling
        self.sort_by_combo = QComboBox()
        self.sort_by_combo.addItems(["Newest", "Oldest", "Name (A-Z)", "Name (Z-A)"])
        self.sort_by_combo.setFixedSize(200, 35)
        self.sort_by_combo.setEditable(False)
        self.sort_by_combo.setFont(list_mod_font)
        self.sort_by_combo.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.sort_by_combo.setStyleSheet("""
            QComboBox {
                background-color: #1e1e1e;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                padding: 4px 8px;
            }
        """)

        sort_by_hbox = QHBoxLayout()
        sort_by_hbox.addStretch()
        sort_by_hbox.addWidget(sort_by_lbl)
        sort_by_hbox.addSpacing(5)
        sort_by_hbox.addWidget(self.sort_by_combo)

        card = Card(radius=10)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        scroll_contents = QWidget()

        self.quiz_vbox = QVBoxLayout(scroll_contents)
        self.quiz_vbox.setSpacing(10)

        scroll.setWidget(scroll_contents)

        ## LAYOUTS SETUP ##
        nav_grid = QGridLayout()
        nav_grid.addWidget(return_btn, 0, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        nav_grid.addWidget(heading, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        nav_grid.addWidget(create_btn, 0, 2, alignment=Qt.AlignmentFlag.AlignRight)
        nav_grid.setColumnStretch(0, 1)
        nav_grid.setColumnStretch(1, 0)
        nav_grid.setColumnStretch(2, 1)

        vbox_header = QVBoxLayout()
        vbox_header.addLayout(nav_grid)
        vbox_header.addSpacing(2)
        vbox_header.addWidget(description)
        vbox_header.addSpacing(10)

        list_mod_hbox = QHBoxLayout()
        list_mod_hbox.addWidget(self.search_input, stretch=2)
        list_mod_hbox.addStretch(3)
        list_mod_hbox.addLayout(sort_by_hbox, stretch=2)

        card_vbox = QVBoxLayout(card)
        card_vbox.addWidget(scroll)

        vbox = QVBoxLayout()
        vbox.setContentsMargins(20, 20, 20, 20)
        vbox.addLayout(vbox_header)
        vbox.addLayout(list_mod_hbox)
        vbox.addSpacing(10)
        vbox.addWidget(card, stretch=1)

        self.setLayout(vbox)

    def add_quizzes(
        self, quizzes: list[Quiz], do_default_spacing: bool = False
    ) -> None:
        default_started = False
        starts_with_default = quizzes[0].is_premade

        for quiz in quizzes:
            if (
                quiz.is_premade
                and not default_started
                and not starts_with_default
                and do_default_spacing
            ):
                default_started = True
                self.quiz_vbox.addSpacing(20)

            quiz_card = QuizCard(
                quiz.quiz_id,
                quiz.quiz_title,
                len(quiz.questions),
                quiz.is_premade,
                quiz.updated_at,
            )
            quiz_card.delete_quiz_requested.connect(self.delete_quiz)
            quiz_card.edit_quiz_requested.connect(self.edit_quiz)

            self.quiz_vbox.addWidget(quiz_card)

        self.quiz_vbox.addStretch()

    def remove_all_quizzes(self):
        while self.quiz_vbox.count():
            item = self.quiz_vbox.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

    def delete_quiz(self, title: str) -> None:
        print(f"Delete: {title}")

    def edit_quiz(self, title: str) -> None:
        print(f"Edit: {title}")

    def on_enter(self, payload=None) -> None:
        quizzes = [
            Quiz(
                quiz_id="1",
                quiz_title="Weird But True!",
                questions=[""] * 20,
                do_shuffle=False,
                is_premade=False,
                updated_at=datetime(2026, 4, 3, 21, 8, 54),
            ),
            Quiz(
                quiz_id="2",
                quiz_title="Guess the Movie by Emojis!",
                questions=[""] * 20,
                do_shuffle=True,
                is_premade=False,
                updated_at=datetime(2026, 3, 14, 16, 20, 0),
            ),
            Quiz(
                quiz_id="3",
                quiz_title="Python Quiz",
                questions=[""] * 12,
                do_shuffle=True,
                is_premade=False,
                updated_at=datetime(2026, 1, 28, 9, 15, 37),
            ),
            Quiz(
                quiz_id="4",
                quiz_title="General Knowledge Quiz",
                questions=[""] * 10,
                do_shuffle=False,
                is_premade=True,
            ),
            Quiz(
                quiz_id="5",
                quiz_title="Mathematics Quiz",
                questions=[""] * 10,
                do_shuffle=False,
                is_premade=True,
            ),
            Quiz(
                quiz_id="6",
                quiz_title="Science Quiz",
                questions=[""] * 10,
                do_shuffle=False,
                is_premade=True,
            ),
        ]

        self.add_quizzes(quizzes, do_default_spacing=True)

    def on_leave(self):
        self.remove_all_quizzes()
