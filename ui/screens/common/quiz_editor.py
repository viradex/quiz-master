from PyQt6.QtWidgets import (
    QWidget,
    QStackedWidget,
    QFrame,
    QPushButton,
    QScrollArea,
    QSplitter,
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
from models.payloads import QuestionPayload


class CommonQuizEditorScreen(BaseScreen):
    title_text = "Quiz Master – Quiz Editor"

    blank_question_requested = pyqtSignal()
    duplicate_requested = pyqtSignal(Question)
    delete_requested = pyqtSignal(Question)
    question_reorder_requested = pyqtSignal(Question, int)

    discard_requested = pyqtSignal()
    save_requested = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        # When doing methods on self.quiz, avoid running methods that mutate the quiz
        # Good: len(self.quiz.get_all_questions())
        # Bad: self.quiz.remove_question(question.question_id)
        self.quiz: Quiz | None = None
        self.read_only: bool = False
        self.returning_from_preview: bool = False

        # Question ID -> widget
        self.cards: dict[str, QuestionCard] = {}
        self.editors: dict[str, QuestionEditor] = {}

        self.setup_ui()

    def setup_ui(self) -> None:
        ## WIDGETS SETUP ##
        sidebar = QFrame()
        sidebar.setMinimumWidth(160)
        sidebar.setMaximumWidth(500)
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
        self.add_btn.clicked.connect(self.blank_question_requested.emit)
        self.add_btn.setStyleSheet("QPushButton { font-size: 18px; }")

        self.discard_btn = QPushButton("Discard")
        self.discard_btn.setFixedHeight(30)
        self.discard_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.discard_btn.clicked.connect(lambda: self.discard_requested.emit())
        self.discard_btn.setStyleSheet("QPushButton { font-size: 14px; }")

        self.save_btn = QPushButton("Save")
        self.save_btn.setFixedHeight(30)
        self.save_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.save_btn.clicked.connect(lambda: self.save_requested.emit())
        self.save_btn.setStyleSheet("QPushButton { font-size: 14px; }")

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

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(sidebar)
        splitter.addWidget(self.editor_stack)

        # 1:4 starting ratio
        splitter.setSizes([200, 800])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(2)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background: #3a3a3a;
            }

            QSplitter::handle:hover {
                background: #5a5a5a;
            }
        """)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(splitter)

        self.setLayout(hbox)

    def set_quiz(self, quiz: Quiz, read_only: bool) -> None:
        self.quiz = quiz
        self.read_only = read_only

        self.set_window_title()

        self.add_btn.setDisabled(self.read_only)
        self.save_btn.setDisabled(self.read_only)

        self.add_btn.setToolTip("Cannot edit read-only quiz" if self.read_only else "")
        self.save_btn.setToolTip("Cannot edit read-only quiz" if self.read_only else "")
        self.discard_btn.setText("Return" if self.read_only else "Discard")

        questions = self.quiz.get_all_questions()
        if questions:
            for i, question in enumerate(self.quiz.get_all_questions(), start=1):
                self.add_question_widgets(question, i)

            first_question = self.quiz.get_all_questions()[0]
            self.display_question(first_question)

    def set_window_title(self) -> None:
        if not self.read_only:
            self.set_title(f"Quiz Master – Editing {self.quiz.quiz_title}")
        else:
            self.set_title(f"Quiz Master – Viewing {self.quiz.quiz_title}")

    def add_question_widgets(self, question: Question, question_num: int) -> None:
        if question.question_id in self.editors:
            self.display_question(question)
            return

        total_questions = len(self.quiz.get_all_questions())

        # Initialize editor and card
        editor = QuestionEditor(question, question_num, total_questions, self.read_only)
        card = QuestionCard(question, question_num)

        # Save editor and show
        self.editors[question.question_id] = editor
        self.editor_stack.addWidget(editor)
        self._show_editor(editor, first=True)

        # Save card and show
        self.cards[question.question_id] = card
        self.question_list.insertWidget(self.question_list.count() - 1, card)

        # Setup editor
        editor.error_results.connect(self._on_error_results)
        editor.question_reordered.connect(self.question_reorder_requested.emit)
        editor.question_text_changed.connect(self._on_question_text)
        editor.global_time_requested.connect(self._on_global_time)
        editor.preview_requested.connect(self.preview_question)
        editor.duplicate_requested.connect(self.duplicate_requested.emit)
        editor.delete_requested.connect(self.delete_requested.emit)

        # Setup card
        card.select()
        card.clicked.connect(lambda q=question: self.display_question(q))

        self._update_delete_state()

    def remove_question_widgets(
        self, question: Question, next_question: Question
    ) -> None:
        # Remove editor
        editor = self.editors.pop(question.question_id, None)
        if editor is not None:
            self.editor_stack.removeWidget(editor)
            editor.deleteLater()

        # Remove card
        card = self.cards.pop(question.question_id, None)
        if card is not None:
            self.question_list.removeWidget(card)
            card.deleteLater()

        self._update_question_numbers()
        self._update_delete_state()

        self.display_question(next_question)

    def clear_questions(self) -> None:
        # Remove editors
        for editor in self.editors.values():
            self.editor_stack.removeWidget(editor)
            editor.deleteLater()

        self.editors.clear()

        # Remove cards
        for card in self.cards.values():
            self.question_list.removeWidget(card)
            card.deleteLater()

        self.cards.clear()

    def display_question(self, question: Question) -> None:
        editor = self.editors.get(question.question_id)
        card = self.cards.get(question.question_id)

        if self.editor_stack.currentWidget() is editor:
            card.select()
            return

        if editor and card:
            self._show_editor(editor)
            card.select()

    def preview_question(self, payload: QuestionPayload) -> None:
        self.returning_from_preview = True
        self.go_to(Screens.CLIENT_MULTI_QUESTION, payload)

    def update_question_order(self) -> None:
        self._refresh_card_order()
        self._update_question_numbers()

    def _show_editor(self, editor: QuestionEditor, first: bool = False) -> None:
        old = self.editor_stack.currentWidget()
        if old is not None and old is not editor:
            old.on_leave()

        self.editor_stack.setCurrentWidget(editor)
        editor.on_enter(len(self.quiz.get_all_questions()), first)

    def _refresh_card_order(self) -> None:
        # Remove every card
        for card in self.cards.values():
            self.question_list.removeWidget(card)

        # Reinsert in proper order
        for question in self.quiz.get_all_questions():
            self.question_list.insertWidget(
                self.question_list.count() - 1,
                self.cards[question.question_id],
            )

    def _update_question_numbers(self) -> None:
        for i, question in enumerate(self.quiz.get_all_questions(), start=1):
            if question.question_id in self.cards:
                self.cards[question.question_id].update_question_num(i)

            if question.question_id in self.editors:
                self.editors[question.question_id].update_question_num(
                    i, len(self.quiz.get_all_questions())
                )

    def _update_delete_state(self) -> None:
        can_delete = len(self.quiz.get_all_questions()) > 1

        for editor in self.editors.values():
            if can_delete:
                editor.enable_delete()
            else:
                editor.disable_delete()

    def _on_error_results(self, question: Question, error_occurred: bool) -> None:
        if error_occurred:
            self.cards[question.question_id].error()
        else:
            self.cards[question.question_id].deselect()

    def _on_global_time(self, seconds: int, text: str) -> None:
        confirm = self.show_question(
            "Set Time for All Questions?",
            f"Are you sure you want to change the time limit for all questions to {text}?",
        )

        if confirm:
            for editor in self.editors.values():
                editor.set_time_limit(seconds)

    def _on_question_text(self, question: Question) -> None:
        self.cards[question.question_id].update_question_text(question.question_text)

    def on_enter(self, payload=None):
        if self.returning_from_preview and self.quiz is not None:
            # Do not reset returning_from_preview here, the logic does that
            self.set_window_title()
