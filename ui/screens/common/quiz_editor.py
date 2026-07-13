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

from ui.components.dialogs import confirm_warning


class CommonQuizEditorScreen(BaseScreen):
    title_text = "Quiz Master – Quiz Editor (Quiz Name)"

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.quiz: Quiz | None = None
        self.mode: str | None = None
        self.changes_made: bool = False

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
        self.add_btn.clicked.connect(self.add_blank_question)
        self.add_btn.setStyleSheet("font-size: 18px;")

        self.discard_btn = QPushButton("Discard")
        self.discard_btn.setFixedHeight(30)
        self.discard_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.discard_btn.clicked.connect(self._on_discard_clicked)
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
        self._show_editor(editor, first=True)

        # Save card and show
        self.cards[question.question_id] = card
        self.question_list.insertWidget(self.question_list.count() - 1, card)

        # Setup editor
        editor.error_results.connect(self._on_error_results)
        editor.question_text_changed.connect(self._on_question_text)
        editor.global_time_requested.connect(self._on_global_time)
        editor.delete_requested.connect(self.remove_question)

        # Setup card
        card.select()
        card.clicked.connect(lambda: self.display_question(question))

        self._update_delete_state()

    def remove_question(self, question: Question) -> None:
        if len(self.quiz.get_all_questions()) == 1:
            # Ordinarily, this should never happen
            self.show_error(
                "Cannot Delete Question", "Cannot delete the only question."
            )
            return

        self.quiz.remove_question(question.question_id)

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

        # Ensure styles and other processes update from Qt automatic stacked widget switching
        current_editor = self.editor_stack.currentWidget()
        if current_editor is not None:
            self._show_editor(current_editor)
            self.cards[current_editor.question.question_id].select()

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

        if editor and card:
            self._show_editor(editor)
            card.select()

    def add_blank_question(self) -> None:
        question = Question(Question.generate_random_id(), "", [], None, 20)
        question_index = self.quiz.add_question(question)

        self.add_question(question, question_index + 1)

    def _show_editor(self, editor: QuestionEditor, first: bool = False) -> None:
        old = self.editor_stack.currentWidget()
        if old is not None and old is not editor:
            old.on_leave()

        self.editor_stack.setCurrentWidget(editor)
        editor.on_enter(len(self.quiz.get_all_questions()), first)

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
            self.cards[question.question_id].deselect_error()
        else:
            self.cards[question.question_id].deselect()

    def _on_discard_clicked(self) -> None:
        if self.changes_made:
            confirm = confirm_warning(
                self,
                "Discard Quiz?",
                "Are you sure you want to discard any unsaved work? The changes made will be permanently deleted and irrecoverable!",
            )
        else:
            confirm = True

        if confirm:
            self.clear_questions()
            self.go_to(Screens.COMMON_QUIZ_MANAGER)

    def _on_global_time(self, seconds: int) -> None:
        for editor in self.editors.values():
            editor.set_time_limit(seconds)

    def _on_question_text(self, question: Question) -> None:
        self.cards[question.question_id].update_question_text(question.question_text)

    def on_enter(self, payload: dict) -> None:
        self.quiz = payload["quiz"]

        if self.quiz.get_all_questions():
            # Edit mode
            self.mode = "edit"

            for i, question in enumerate(self.quiz.get_all_questions(), start=1):
                self.add_question(question, i)

            first_question = self.quiz.get_all_questions()[0]
            self.display_question(first_question)
        else:
            # Create mode
            self.mode = "create"
            self.add_blank_question()

    def on_window_close(self, event) -> None:
        pass
        # TODO make it save the quiz instead
        # confirm = confirm_warning(
        #     self,
        #     "Close and Discard",
        #     "Are you sure you want to discard any unsaved work? The changes made will be permanently deleted and irrecoverable!",
        # )

        # if confirm:
        #     event.accept()
        # else:
        #     event.ignore()
