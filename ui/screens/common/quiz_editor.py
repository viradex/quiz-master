from PyQt6.QtWidgets import (
    QWidget,
    QStackedWidget,
    QFrame,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal

from core.app.screen_ids import Screens
from ui.screens.base_screen import BaseScreen
from ui.components.card import QuestionCard
from ui.components.question_editor import QuestionEditor
from models.quiz import Quiz
from models.question import Question


class CommonQuizEditorScreen(BaseScreen):
    title_text = "Quiz Master – Quiz Editor (Quiz Name)"

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.quiz: Quiz | None = None

        # Question ID -> widget
        self.cards: dict[str, QuestionCard] = {}
        self.editors: dict[str, QuestionEditor] = {}

        self.setup_ui()

    def setup_ui(self) -> None:
        ## WIDGETS SETUP ##
        sidebar = QFrame()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #252526;
            }
        """)

        # All questions
        question_container = QWidget()
        question_container.setStyleSheet("background-color: #252526;")

        self.question_list = QVBoxLayout(question_container)
        self.question_list.setSpacing(15)
        self.question_list.setContentsMargins(5, 5, 5, 5)
        self.question_list.addStretch()

        self.question_scroll = QScrollArea()
        self.question_scroll.setWidgetResizable(True)
        self.question_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.question_scroll.setWidget(question_container)
        self.question_scroll.setFrameShape(QFrame.Shape.NoFrame)

        # Action buttons
        self.add_btn = QPushButton("+ Add")
        self.add_btn.setFixedHeight(40)
        self.add_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.add_btn.clicked.connect(self._on_add_question)
        self.add_btn.setStyleSheet("font-size: 18px;")

        self.discard_btn = QPushButton("Discard")
        self.discard_btn.setFixedHeight(30)
        self.discard_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.discard_btn.clicked.connect(
            lambda: self.go_to(Screens.COMMON_QUIZ_MANAGER)
        )
        self.discard_btn.setStyleSheet("font-size: 14px;")

        self.save_btn = QPushButton("Save")
        self.save_btn.setFixedHeight(30)
        self.save_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.save_btn.setStyleSheet("font-size: 14px;")

        # Main screen editor
        self.editor_stack = QStackedWidget()

        ## LAYOUTS SETUP ##
        sidebar_btn_hbox = QHBoxLayout()
        sidebar_btn_hbox.addWidget(self.discard_btn)
        sidebar_btn_hbox.addWidget(self.save_btn)

        sidebar_vbox = QVBoxLayout(sidebar)
        sidebar_vbox.addWidget(self.question_scroll, stretch=1)
        sidebar_vbox.addWidget(self.add_btn)
        sidebar_vbox.addLayout(sidebar_btn_hbox)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(sidebar)
        hbox.addWidget(self.editor_stack, stretch=1)

        self.setLayout(hbox)

    def deselect_all_cards(self) -> None:
        for card in self.cards.values():
            card.deselect()

    def add_question(self, question: Question, question_num: int) -> None:
        if question.question_id in self.editors:
            self.display_question(question)
            return

        total_questions = len(self.quiz.get_all_questions())

        # Initialize editor and card
        editor = QuestionEditor(question, question_num, total_questions)
        card = QuestionCard(question, question_num)

        # Save editor and show
        self.editors[question.question_id] = editor
        self.editor_stack.addWidget(editor)
        self.editor_stack.setCurrentWidget(editor)

        # Save card and show
        self.cards[question.question_id] = card
        self.question_list.insertWidget(self.question_list.count() - 1, card)

        # Setup editor
        editor.question_text_changed.connect(self._on_question_text)

        # Setup card
        self.deselect_all_cards()
        card.select()
        card.clicked.connect(lambda: self.display_question(question))

    def remove_question(self, question: Question) -> None:
        editor = self.editors.pop(question.question_id, None)
        if editor is None:
            return

        self.editor_stack.removeWidget(editor)
        editor.deleteLater()

    def display_question(self, question: Question) -> None:
        editor = self.editors.get(question.question_id)
        card = self.cards.get(question.question_id)

        if editor and card:
            self.editor_stack.setCurrentWidget(editor)

            total_questions = len(self.quiz.get_all_questions())
            editor.on_enter(total_questions)

            self.deselect_all_cards()
            card.select()

    def _on_add_question(self) -> None:
        question = Question(Question.generate_random_id(), "", [""] * 4, -1, 20)
        question_index = self.quiz.add_question(question)

        self.add_question(question, question_index + 1)

    def _on_question_text(self, question: Question) -> None:
        self.cards[question.question_id].update_question_text(question.question_text)

    def on_enter(self, payload: dict) -> None:
        self.quiz = payload["quiz"]
        self._on_add_question()
