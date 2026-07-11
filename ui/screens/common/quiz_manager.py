from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget,
    QFrame,
    QLabel,
    QPushButton,
    QLineEdit,
    QComboBox,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QScrollArea,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

from core.app.screen_ids import Screens
from core.app.enums import QuizSortingOrder
from ui.screens.base_screen import BaseScreen
from ui.components.card import Card, QuizCard
from models.quiz import Quiz

from ui.components.button import create_return_button
from ui.components.dialogs import confirm_warning


class CommonQuizManagerScreen(BaseScreen):
    title_text = "Quiz Master – Manage Quizzes"

    edit_requested = pyqtSignal(str)
    delete_requested = pyqtSignal(str)

    search_requested = pyqtSignal(str)
    sort_requested = pyqtSignal(object)

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
        self.search_input.textChanged.connect(self.on_search_change)
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
            QIcon(str(search_icon)), QLineEdit.ActionPosition.LeadingPosition
        )

        sort_by_lbl = QLabel("Sort by:")
        sort_by_lbl.setStyleSheet("font-size: 14px;" "color: #888;")

        self.sort_by_combo = QComboBox()
        self.sort_by_combo.setFixedSize(200, 35)
        self.sort_by_combo.setEditable(False)
        self.sort_by_combo.activated.connect(self.on_sort_changed)
        self.sort_by_combo.setFont(list_mod_font)

        chevron_down_icon = self.icons_path / "chevron_down.png"
        self.sort_by_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: #1e1e1e;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                padding: 4px 8px;
            }}

            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}

            QComboBox::down-arrow {{
                image: url("{chevron_down_icon.as_posix()}");
                width: 12px;
                height: 12px;
            }}
        """)

        self.sort_by_combo.addItem("Newest", QuizSortingOrder.NEWEST)
        self.sort_by_combo.addItem("Oldest", QuizSortingOrder.OLDEST)
        self.sort_by_combo.addItem("Name (A-Z)", QuizSortingOrder.NAME_ASC)
        self.sort_by_combo.addItem("Name (Z-A)", QuizSortingOrder.NAME_DESC)

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
        scroll.setWidget(scroll_contents)

        self.empty_quizzes = QFrame()
        self.empty_quizzes.hide()
        self.empty_quizzes.setObjectName("empty")
        self.empty_quizzes.setStyleSheet("""
            QFrame#empty {
                background-color: transparent;
                border: 2px dotted #5C5C5C;
                border-radius: 10px;
            }
        """)

        empty_title_lbl = QLabel("No Quizzes Found")
        empty_title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_title_lbl.setStyleSheet(
            "font-size: 20px;" "font-weight: 600;" "color: #8A8A8A"
        )

        empty_desc_lbl = QLabel("Try a different search, or create a new quiz.")
        empty_desc_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_desc_lbl.setStyleSheet("font-size: 14px;" "color: #8A8A8A")

        empty_vbox = QVBoxLayout(self.empty_quizzes)
        empty_vbox.setContentsMargins(16, 12, 16, 12)
        empty_vbox.addWidget(empty_title_lbl)
        empty_vbox.addWidget(empty_desc_lbl)

        self.quiz_vbox = QVBoxLayout(scroll_contents)
        self.quiz_vbox.setSpacing(10)
        self.quiz_vbox.addWidget(self.empty_quizzes)

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
        if not quizzes:
            self.empty_quizzes.setHidden(False)
            self.quiz_vbox.addStretch()
            return
        else:
            self.empty_quizzes.hide()

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

                divider = QFrame()
                divider.setFrameShape(QFrame.Shape.HLine)
                divider.setFrameShadow(QFrame.Shadow.Plain)
                divider.setStyleSheet("color: #3C3C3C;")

                self.quiz_vbox.addSpacing(10)
                self.quiz_vbox.addWidget(divider)
                self.quiz_vbox.addSpacing(10)

            quiz_card = QuizCard(
                quiz.quiz_id,
                quiz.quiz_title,
                len(quiz.questions),
                quiz.is_premade,
                quiz.updated_at,
            )

            quiz_card.edit_quiz_requested.connect(self.on_edit_quiz)
            quiz_card.delete_quiz_requested.connect(self.on_delete_quiz)

            self.quiz_vbox.addWidget(quiz_card)

        self.quiz_vbox.addStretch()

    def remove_all_quizzes(self) -> None:
        # Doing in reversed order as removing indicies while iterating starting from 0
        # can cause some to be skipped. Starting from the end prevents that.
        for i in reversed(range(self.quiz_vbox.count())):
            item = self.quiz_vbox.itemAt(i)
            widget = item.widget()

            if widget is None:
                # Remove stretchers and spacers
                self.quiz_vbox.removeItem(item)
            elif widget is self.empty_quizzes:
                continue
            else:
                # Remove all other widets
                self.quiz_vbox.removeWidget(widget)
                widget.deleteLater()

    def on_search_change(self, query: str) -> None:
        self.search_requested.emit(query)

    def on_sort_changed(self, index: int) -> None:
        sort_order = self.sort_by_combo.currentData()
        self.sort_requested.emit(sort_order)

    def on_edit_quiz(self, quiz_id: str, quiz_title: str) -> None:
        self.edit_requested.emit(quiz_id)

    def on_delete_quiz(self, quiz_id: str, quiz_title: str) -> None:
        confirm = confirm_warning(
            self,
            "Confirm Deleting Quiz",
            f'Are you sure you want to permanently delete the quiz "{quiz_title}"? This cannot be undone!',
        )

        if confirm:
            self.delete_requested.emit(quiz_id)

    def on_leave(self) -> None:
        self.search_input.setText("")

        # TODO should we also reset sorting upon leaving screen?
        self.sort_by_combo.setCurrentIndex(0)

        self.remove_all_quizzes()
