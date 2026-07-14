from copy import deepcopy
from PyQt6.QtWidgets import QMessageBox

from ui.screens.common.quiz_editor import CommonQuizEditorScreen
from logic.base_logic import BaseLogic
from data.quiz_repo import QuizRepository
from core.app.screen_ids import Screens
from models.quiz import Quiz
from models.question import Question

from ui.components.dialogs import confirm_warning


class CommonQuizEditorLogic(BaseLogic):
    def __init__(self, screen, services) -> None:
        super().__init__()
        self.screen: CommonQuizEditorScreen = screen
        self.quiz_repo: QuizRepository = services.quiz_repo

        self.quiz: Quiz | None = None
        self.original_quiz: Quiz | None = None
        self.read_only: bool = False

        self.screen.blank_question_requested.connect(self.on_blank_question_requested)
        self.screen.duplicate_requested.connect(self.on_duplicate_requested)
        self.screen.delete_requested.connect(self.on_delete_requested)
        self.screen.question_reorder_requested.connect(
            self.on_question_reorder_requested
        )
        self.screen.discard_requested.connect(self.on_discard_requested)
        self.screen.save_requested.connect(self.on_save_requested)

    def quiz_changed(self) -> bool:
        return self.quiz != self.original_quiz

    def on_blank_question_requested(self) -> None:
        question = Question(Question.generate_random_id(), "", [], None, 20)
        index = self.quiz.add_question(question)

        self.screen.add_question_widgets(question, index + 1)

    def on_duplicate_requested(self, question: Question) -> None:
        duplicate = deepcopy(question)
        duplicate.question_id = Question.generate_random_id()

        index = self.quiz.get_question_index(question.question_id)

        # Internal question indexes are 0-based, but UI is 1-based
        # We want the new question to be one ahead of the original
        self.quiz.add_question(duplicate, index + 1)
        self.screen.add_question_widgets(duplicate, index + 2)

        self.screen.update_question_order()

    def on_delete_requested(self, question: Question) -> None:
        if len(self.quiz.get_all_questions()) == 1:
            # Ordinarily, this should never happen
            self.screen.show_error(
                "Cannot Delete Question", "Cannot delete the only question."
            )
            return

        questions = self.quiz.get_all_questions()

        next_question = None
        index = questions.index(question)

        # Prefer the next question, otherwise the previous one if ending question was removed
        if index < len(questions) - 1:
            next_question = questions[index + 1]
        else:
            next_question = questions[index - 1]

        self.quiz.remove_question(question.question_id)
        self.screen.remove_question_widgets(question, next_question)

    def on_question_reorder_requested(
        self, question: Question, new_question_num: int
    ) -> None:
        self.quiz.move_question(question.question_id, new_question_num - 1)
        self.screen.update_question_order()

    def on_discard_requested(self) -> None:
        if self.quiz_changed() and not self.read_only:
            confirm = confirm_warning(
                self.screen,
                "Discard Quiz?",
                "Are you sure you want to discard your unsaved work?",
            )
        else:
            confirm = True

        if confirm:
            self.screen.clear_questions()
            self.screen.go_to(Screens.COMMON_QUIZ_MANAGER)

    def on_save_requested(self) -> None:
        if not self.quiz_changed() or self.read_only:
            self.screen.clear_questions()
            self.screen.go_to(Screens.COMMON_QUIZ_MANAGER)
            return

        for question in self.quiz.questions:
            errors = question.validate_question()

            if errors:
                self.screen.show_error(
                    "Question Issues",
                    "Some questions have issues that prevent the quiz from being saved. Questions with errors are highlighted with a red outline. Please fix them and try again.",
                )
                return

        self.quiz_repo.edit(self.quiz.quiz_id, self.quiz.to_dict())
        self.screen.go_to(Screens.COMMON_QUIZ_MANAGER)

    def on_enter(self, payload: dict | None = None):
        if self.screen.returning_from_preview:
            self.screen.returning_from_preview = False
            return

        self.quiz = payload["quiz"]
        self.original_quiz = deepcopy(self.quiz)
        self.read_only = self.quiz.is_premade  # If pre-made quiz, view-only mode

        self.screen.set_quiz(self.quiz, self.read_only)

        if not self.read_only and not self.quiz.questions:
            self.on_blank_question_requested()

    def on_window_close(self, event):
        if self.quiz_changed() and not self.read_only:
            for question in self.quiz.questions:
                errors = question.validate_question()

                if errors:
                    confirm = confirm_warning(
                        self.screen,
                        "Discard Changes?",
                        "The quiz cannot be saved as it has errors. Would you like to quit and discard your changes?",
                    )

                    if confirm:
                        event.accept()
                    else:
                        event.ignore()

                    return

            action = QMessageBox.question(
                self.screen,
                "Save Changes?",
                "Would you like to save your changes made to this quiz?",
                buttons=QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel,
                defaultButton=QMessageBox.StandardButton.Save,
            )

            if action == QMessageBox.StandardButton.Save:
                self.quiz_repo.edit(self.quiz.quiz_id, self.quiz.to_dict())
                event.accept()
            elif action == QMessageBox.StandardButton.Discard:
                event.accept()
            else:
                event.ignore()
