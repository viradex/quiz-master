from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QStackedWidget,
    QFrame,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QScrollArea,
    QSizePolicy,
    QSplitter,
)

from core.app.screen_ids import Screens

from models.payloads import QuestionPayload
from models.question import Question
from models.quiz import Quiz
from ui.components.card import QuestionCard
from ui.components.question_editor import QuestionEditor
from ui.screens.base_screen import BaseScreen


class CommonQuizEditorScreen(BaseScreen):
    title_text = "Quiz Master – Quiz Editor"

    blank_question_requested = pyqtSignal()
    duplicate_requested = pyqtSignal(Question)
    delete_requested = pyqtSignal(Question)
    question_reorder_requested = pyqtSignal(Question, int)  # New question index

    revert_requested = pyqtSignal()
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

        # Question list sidebar
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

        # Action buttons (at bottom of sidebar)
        self.add_btn = QPushButton("+ Add")
        self.add_btn.setFixedHeight(40)
        self.add_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.add_btn.clicked.connect(self.blank_question_requested.emit)
        self.add_btn.setStyleSheet("QPushButton { font-size: 18px; }")

        self.revert_btn = QPushButton("Revert")
        self.revert_btn.setFixedHeight(30)
        self.revert_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.revert_btn.clicked.connect(lambda: self.revert_requested.emit())
        self.revert_btn.setStyleSheet("QPushButton { font-size: 14px; }")

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
        sidebar_btn_hbox.addWidget(self.revert_btn)
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
        """Set the quiz to modify, and whether said quiz should be viewed in read-only mode."""
        self.clear_questions()

        self.quiz = quiz
        self.read_only = read_only
        self.returning_from_preview = False

        self.set_window_title()

        # Change button states if in read-only mode
        self.add_btn.setDisabled(self.read_only)
        self.save_btn.setDisabled(self.read_only)

        self.add_btn.setToolTip("Cannot edit read-only quiz" if self.read_only else "")
        self.save_btn.setToolTip("Cannot edit read-only quiz" if self.read_only else "")
        self.revert_btn.setText("Return" if self.read_only else "Revert")

        # If editing existing quiz, prefills quiz editor with all of the widgets immediately
        questions = self.quiz.get_all_questions()
        if questions:
            for i, question in enumerate(self.quiz.get_all_questions(), start=1):
                self.add_question_widgets(question, i)

            # Show the first question when entering for the first time
            first_question = self.quiz.get_all_questions()[0]
            self.display_question(first_question)

    def set_window_title(self) -> None:
        """Set the application title depending on the mode and quiz title."""
        if not self.read_only:
            self.set_title(f"Quiz Master – Editing {self.quiz.quiz_title}")
        else:
            self.set_title(f"Quiz Master – Viewing {self.quiz.quiz_title}")

    def add_question_widgets(self, question: Question, question_num: int) -> None:
        """Adds a QuestionEditor and QuestionCard with the question data and number."""
        # If question is already shown, only show it
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

        # Setup editor signals routing
        editor.error_results.connect(self._on_error_results)
        editor.question_reordered.connect(
            lambda q, new_num: self.question_reorder_requested.emit(q, new_num)
        )
        editor.question_text_changed.connect(self._on_question_text)
        editor.global_time_requested.connect(self._on_global_time)
        editor.preview_requested.connect(self.preview_question)
        editor.duplicate_requested.connect(lambda q: self.duplicate_requested.emit(q))
        editor.delete_requested.connect(lambda q: self.delete_requested.emit(q))

        # Setup card
        card.select()
        card.clicked.connect(lambda q=question: self.display_question(q))

        self._update_delete_state()

    def remove_question_widgets(
        self, question: Question, next_question: Question
    ) -> None:
        """Removes a QuestionEditor and QuestionCard respective to the question
        provided, if they exist. Shows the question provided once done."""
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
        """Remove all editors and cards from UI and data."""
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
        """Display a specific editor on the screen and highlight the card relative to the editor."""
        editor = self.editors.get(question.question_id)
        card = self.cards.get(question.question_id)

        # If selecting the card related to the editor that is already shown, don't show it again
        if self.editor_stack.currentWidget() is editor:
            card.select()
            return

        # If editor is not shown yet on UI
        if editor and card:
            self._show_editor(editor)
            card.select()

    def preview_question(self, payload: QuestionPayload) -> None:
        """Previews a question by opening the `ClientMultiQuestionScreen` with a payload provided."""
        self.returning_from_preview = True
        self.go_to(Screens.CLIENT_MULTI_QUESTION, payload)

    def update_question_order(self) -> None:
        """Updates card order and question numbers to reflect the current internal state."""
        self._refresh_card_order()
        self._update_question_numbers()

    def _show_editor(self, editor: QuestionEditor, first: bool = False) -> None:
        """Shows the QuestionEditor screen requested."""
        # Notify the old widget it is about to be hidden
        old = self.editor_stack.currentWidget()
        if old is not None and old is not editor:
            old.on_leave()

        self.editor_stack.setCurrentWidget(editor)
        editor.on_enter(len(self.quiz.get_all_questions()), first)

    def _refresh_card_order(self) -> None:
        """Remove and readd the question cards on the sidebar to reflect any changes made internally."""
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
        """Update question numbers on all cards and editors."""
        for i, question in enumerate(self.quiz.get_all_questions(), start=1):
            # Update cards
            if question.question_id in self.cards:
                self.cards[question.question_id].update_question_num(i)

            # Update editors (also provide total questions)
            if question.question_id in self.editors:
                self.editors[question.question_id].update_question_num(
                    i, len(self.quiz.get_all_questions())
                )

    def _update_delete_state(self) -> None:
        """Checks if the question(s) can be deleted. Currently, they can only be prevented from deletion
        if there is one question remaining."""
        can_delete = len(self.quiz.get_all_questions()) > 1 or self.read_only

        for editor in self.editors.values():
            if can_delete:
                editor.enable_delete()
            else:
                editor.disable_delete()

    def _on_error_results(self, question: Question, error_occurred: bool) -> None:
        """Typically called when a question editor is left. Colors its respective card depending on whether
        an error occurred or not."""
        if error_occurred:
            self.cards[question.question_id].error()
        else:
            self.cards[question.question_id].deselect()

    def _on_global_time(self, seconds: int, text: str) -> None:
        """Sets the time limit given to all questions in the quiz."""
        confirm = self.show_question(
            "Set Time for All Questions?",
            f"Are you sure you want to change the time limit for all questions to {text}?",
        )

        if confirm:
            for editor in self.editors.values():
                editor.set_time_limit(seconds)

    def _on_question_text(self, question: Question) -> None:
        """Updates the question text of the question's respective card."""
        self.cards[question.question_id].update_question_text(question.question_text)

    def on_enter(self, payload=None) -> None:
        if self.returning_from_preview and self.quiz is not None:
            # Do not reset returning_from_preview here, the logic does that
            self.set_window_title()
