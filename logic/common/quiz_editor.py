from copy import deepcopy

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QMessageBox

from core.app.screen_ids import Screens
from data.quiz_repo import QuizRepository
from models.question import Question
from models.quiz import Quiz
from logic.base_logic import BaseLogic
from ui.screens.common.quiz_editor import CommonQuizEditorScreen

from ui.components.dialogs import confirm_warning
from core.config.constants import QUIZ_AUTOSAVE_INTERVAL


class CommonQuizEditorLogic(BaseLogic):
    def __init__(self, screen, services) -> None:
        super().__init__()
        self.screen: CommonQuizEditorScreen = screen
        self.quiz_repo: QuizRepository = services.quiz_repo

        # In-memory quiz (shared with UI)
        self.quiz: Quiz | None = None

        # Updated when first opening quiz and on every MANUAL save, not autosave
        self.checkpoint_quiz: Quiz | None = None

        # Updated on every save to disk, including autosave
        self.last_saved_quiz: Quiz | None = None

        # If the quiz cannot be edited (currently only for default quizzes)
        self.read_only: bool = False

        self.setup_timer()

        # Screen
        self.screen.blank_question_requested.connect(self.create_new_question)
        self.screen.duplicate_requested.connect(self.on_duplicate_requested)
        self.screen.delete_requested.connect(self.on_delete_requested)
        self.screen.question_reorder_requested.connect(
            self.on_question_reorder_requested
        )
        self.screen.revert_requested.connect(self.on_revert_requested)
        self.screen.save_requested.connect(self.on_save_requested)

    def setup_timer(self) -> None:
        """Set up the autosave timer."""
        self.autosave_timer = QTimer()
        self.autosave_timer.timeout.connect(self._autosave)
        self.autosave_timer.setInterval(QUIZ_AUTOSAVE_INTERVAL * 1000)

    def quiz_changed(self, since_checkpoint=False) -> bool:
        """
        When `since_checkpoint`, returns True if the quiz has been changed since last manually saved, False otherwise.
        Otherwise, returns True if the quiz has been changed since it was last saved (typically through autosave).
        """
        if not since_checkpoint:
            return self.quiz != self.last_saved_quiz
        else:
            return self.quiz != self.checkpoint_quiz

    def create_new_question(self) -> None:
        """Create a new blank question with a unique ID, and add it to the quiz and UI."""
        question = Question(Question.generate_random_id(), "", [], None, 20)
        index = self.quiz.add_question(question)

        self.screen.add_question_widgets(question, index + 1)

    def save_quiz(self, show_status: bool = True) -> None:
        """Save a custom quiz to disk."""
        self.quiz_repo.save(self.quiz)
        self.last_saved_quiz = deepcopy(self.quiz)

        if show_status:
            self.screen.set_status("Saved quiz to disk", 5000)

    def on_duplicate_requested(self, question: Question) -> None:
        """
        Create an identical copy of the question provided, and generate a new unique ID for the newly
        copied question. Adds the duplicate question one position in front of the question it was copied
        from in both the Quiz and UI.
        """

        # Use deepcopy() rather than shallow copy to ensure attributes like lists are not shared
        duplicate = deepcopy(question)
        duplicate.question_id = Question.generate_random_id()

        # Get position of original question
        index = self.quiz.get_question_index(question.question_id)

        # Internal question indexes are 0-based, but UI is 1-based
        # We want the new question to be one ahead of the original
        self.quiz.add_question(duplicate, index + 1)
        self.screen.add_question_widgets(duplicate, index + 2)

        self.screen.update_question_order()

    def on_delete_requested(self, question: Question) -> None:
        """
        Delete the specified question from the quiz and UI. After deletion, prefers showing the
        question that was originally in front of it, else, shows the one behind. Does not allow deleting
        a question if only one question remains.
        """

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
        """Move a question to a new index in the Quiz instance and the UI."""
        self.quiz.move_question(question.question_id, new_question_num - 1)
        self.screen.update_question_order()

    def on_revert_requested(self) -> None:
        """
        Discard any and all changes made in this session. Shows a confirmation dialog
        if any changes were made and the quiz was not in read-only mode. Upon accepting, the
        starting quiz version is restored and the user is returned to the quiz manager.
        """

        if self.quiz_changed(since_checkpoint=True) and not self.read_only:
            confirm = confirm_warning(
                self.screen,
                "Revert All Changes?",
                "Are you sure you want to discard all changes you made since saving this quiz?",
            )

            if confirm:
                self.quiz_repo.save(self.checkpoint_quiz)
        else:
            confirm = True

        if confirm:
            self.screen.clear_questions()
            self.screen.go_to(Screens.COMMON_QUIZ_MANAGER)

    def on_save_requested(self) -> None:
        """
        Save any changes made in this session to disk and return to the quiz manager. Does not
        allow saving the quiz if question validation errors were detected. If no changes were made,
        the save file is not updated and the user is immediately returned to the quiz manager.
        """
        # Quiz is incomplete if it has errors
        has_errors = self._check_for_errors()
        self.quiz.is_complete = not has_errors

        # Remove any empty C and D answers
        if not has_errors:
            for question in self.quiz.questions:
                question.remove_empty_answers(mutate_answers=True)

        # Save quiz before showing warning, if needed
        if self.quiz_changed() and not self.read_only:
            self.save_quiz()

        if has_errors:
            self.checkpoint_quiz = deepcopy(self.quiz)

            confirm = confirm_warning(
                self.screen,
                "Question Issues",
                "Some questions have issues that prevent the quiz from being played. The quiz has been saved, but you cannot play it until the issues are fixed.\n\nQuestions with errors are highlighted with a red outline. Would you like to ignore the issues and go to the quiz manager?",
            )

            if not confirm:
                # Return to editor without saving
                return

        self.screen.clear_questions()
        self.screen.go_to(Screens.COMMON_QUIZ_MANAGER)

    def _autosave(self) -> None:
        """Run quiz autosave. Saves quiz to disk silently."""
        if self.quiz_changed() and not self.read_only:
            has_errors = self._check_for_errors()
            self.quiz.is_complete = not has_errors

            self.save_quiz(show_status=False)
            self.screen.set_status("Auto-saved quiz", 2000)

    def _check_for_errors(self) -> bool:
        """Returns True if there are errors detected in any question in the quiz, else False."""
        for question in self.quiz.questions:
            errors = question.validate_question()

            if errors:
                return True

        return False

    def on_enter(self, payload: dict | None = None) -> None:
        if self.screen.returning_from_preview:
            self.screen.returning_from_preview = False
            return

        # Save a copy of original quiz for checking if changes were made later
        # Deep copy is required to ensure changes to the original quiz are not reflected
        self.quiz = payload["quiz"]
        self.checkpoint_quiz = deepcopy(self.quiz)
        self.last_saved_quiz = deepcopy(self.quiz)

        # If pre-made quiz, read-only mode
        self.read_only = self.quiz.is_premade

        self.screen.set_quiz(self.quiz, self.read_only)

        # If brand-new quiz, create starter blank question
        if not self.read_only and not self.quiz.questions:
            self.create_new_question()

        if not self.read_only:
            self.autosave_timer.start()

    def on_leave(self) -> None:
        self.autosave_timer.stop()

    def on_window_close(self, event) -> None:
        if self.quiz_changed() and not self.read_only:
            has_errors = self._check_for_errors()
            self.quiz.is_complete = not has_errors

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
                # Quiz is incomplete if it has errors
                has_errors = self._check_for_errors()
                self.quiz.is_complete = not has_errors

                # Remove any empty C and D answers
                if not has_errors:
                    for question in self.quiz.questions:
                        question.remove_empty_answers(mutate_answers=True)

                self.save_quiz()
                event.accept()
            elif action == QMessageBox.StandardButton.Discard:
                # Save last saved state (not from autosave)
                self.quiz_repo.save(self.checkpoint_quiz)
                event.accept()
            else:
                event.ignore()
