"""
quiz_editor.py

The logic respective to the common quiz editor screen.
"""

from copy import deepcopy

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QMessageBox

from core.app.screen_ids import Screen
from core.config.constants import QUIZ_AUTOSAVE_INTERVAL
from core.services.app_context import Services
from data.quiz_repo import QuizRepository
from logic.base_logic import BaseLogic
from models.question import Question
from models.quiz import Quiz
from ui.components.dialog import confirm_warning
from ui.screens.common.quiz_editor import CommonQuizEditorScreen


class CommonQuizEditorLogic(BaseLogic):
    """
    Creates the quiz editor logic class, inheriting BaseLogic. This logic is part of the 'common' category.

    This logic class is responsible for editing the Quiz instance itself while editing, while saving copies
    from different states. Also, saves the quizzes to disk, and runs autosave functionality.

    Arguments:
        screen: The screen respective to this logic class, to allow listening to signals from it and invoking
            methods to modify the UI.

        services: All the application Services, to allow access to various functions of the application
            in one single wrapper class.
    """

    def __init__(self, screen: CommonQuizEditorScreen, services: Services) -> None:
        super().__init__()
        self.screen: CommonQuizEditorScreen = screen
        self.quiz_repo: QuizRepository = services.quiz_repo

        # Values for logic
        # In-memory quiz (shared with UI)
        self.quiz: Quiz | None = None

        # Updated when first opening quiz and on every MANUAL save, not autosave.
        # Used for the Discard button.
        self.checkpoint_quiz: Quiz | None = None

        # Updated on every save to disk, including autosave. Used to know whether
        # to warn the user for unsaved changes when they close the window or not.
        self.last_saved_quiz: Quiz | None = None

        # If the quiz cannot be edited (only for default quizzes)
        self.read_only: bool = False

        self._setup_timer()

        # Screen PyQt signal connections
        self.screen.blank_question_requested.connect(self._on_blank_question_requested)
        self.screen.duplicate_requested.connect(self._on_duplicate_requested)
        self.screen.delete_requested.connect(self._on_delete_requested)
        self.screen.question_reorder_requested.connect(
            self._on_question_reorder_requested
        )
        self.screen.discard_requested.connect(self._on_discard_requested)
        self.screen.save_requested.connect(self._on_save_requested)

    def _setup_timer(self) -> None:
        """
        Internal method. Sets up the autosave `QTimer` needed to automatically save the current progress made
        to the quiz to avoid losing data accidentally.

        Returns:
            None.
        """
        self.autosave_timer = QTimer()
        self.autosave_timer.setInterval(QUIZ_AUTOSAVE_INTERVAL * 1000)
        self.autosave_timer.timeout.connect(self._autosave)

    def quiz_changed(self, only_manual: bool = False) -> bool:
        """
        Whether the current quiz has changed since the last save. If not `only_manual`, it includes both
        autosaves as well as manual saves. Otherwise, it only includes manual saves.

        Arguments:
            only_manual: Whether to include autosaves in the 'last changes' check or not. If False, includes
                manual saves as well as autosaves. Otherwise, only includes manual saves in the check for if
                the current quiz has been changed. Defaults to False, meaning it checks for both autosaves and
                manual saves. A boolean is used as it makes it easier to read with the argument.

        Returns:
            A boolean that determines whether the quizzes are identical or not. True if the quizzes match,
            else, False.
        """
        if not only_manual:
            return self.quiz != self.last_saved_quiz
        else:
            return self.quiz != self.checkpoint_quiz

    def create_new_question(self) -> None:
        """
        Creates a new blank question with a random unique ID, no question text, no answer options, no correct
        answer, and a time limit of 20 seconds. Adds this question to the Quiz and the end of the UI sidebar,
        as the last question in the current quiz.

        Returns:
            None.
        """
        # Create new blank question and add to Quiz
        question = Question(Question.generate_random_id(), "", [], None, 20)
        index = self.quiz.add_question(question)

        # Adds question to end of sidebar on UI
        self.screen.add_question(question, index + 1)

    def save_quiz(self, show_status: bool = True) -> None:
        """
        Saves the current main quiz progress to disk. Updates the last saved quiz to reflect the quiz that was
        just saved, as a copy. If the current quiz that is being edited is read-only, this method does nothing.

        Arguments:
            show_status: Whether to show the saved successfully message in the UI status bar. A boolean is used
                as it is naturally a yes/no option.

        Returns:
            None.
        """
        if self.read_only:
            return

        # Save current quiz and make a deepcopy of the current quiz, to see if
        # any changes were made since last saved in future.
        self.quiz_repo.save(self.quiz)
        self.last_saved_quiz = deepcopy(self.quiz)

        if show_status:
            self.screen.set_status("Saved quiz to disk", 5000)

    def _on_blank_question_requested(self) -> None:
        """
        Internal method. Intended to be called when a new blank question is requested by the user.

        Creates a new blank question, and adds it to the Quiz. Shows the new question on the UI.

        Returns:
            None.
        """
        self.create_new_question()

    def _on_duplicate_requested(self, question: Question) -> None:
        """
        Internal method. Intended to be called when a duplicate of a question is requested by the user.

        Gets the question that was requested by the user to be duplicated, makes a copy of the question (while
        also making a new unique ID for the duplicated question), and inserts it one space below the original
        question in the Quiz instance and UI.

        Arguments:
            question: The Question instance to make a copy of and duplicate. A Question instance is used as it
                contains all the data for the question that can be easily copied.

        Returns:
            None.
        """
        # Use deepcopy() rather than shallow copy to ensure attributes like lists are not shared
        duplicate = deepcopy(question)
        duplicate.question_id = Question.generate_random_id()

        # Get position of original question
        index = self.quiz.get_question_index(question.question_id)

        # Add one ahead (zero-based index for internal question indexes)
        self.quiz.add_question(duplicate, index + 1)

        # Add one ahead too, even though it says +2. This is because the index is
        # zero-based, but the screen uses one-based numbering, so the value needs
        # to have one added to suit that starting position, and then another one
        # added to match the same position as the internal quiz saved location.
        self.screen.add_question(duplicate, index + 2)

        self.screen.update_question_order()

    def _on_delete_requested(self, question: Question) -> None:
        """
        Internal method. Intended to be called when a question is requested to be deleted by the user.

        Gets the question that was requested by the user to be deleted, and removes the question from the quiz
        and the UI. The next question to display is then found. The next question is preferred to be the question
        that is the next in question numbers (for example, if question #2 was deleted, the logic would prefer
        showing question #3, which is now question #2 after the deletion). If no question exists after the one
        that was just deleted, the previous question is chosen to be shown instead.

        If there is only one question remaining, an error modal box is displayed to the user and nothing happens.

        Arguments:
            question: The Question instance to remove. A Question instance is used as it can be easily found the
                index of said question to find the next question to display

        Returns:
            None.
        """
        if self.quiz.get_total_questions() == 1:
            # Ordinarily, this should never happen. This is here as a defensive check.
            self.screen.show_error(
                "Cannot Delete Question", "Cannot delete the only question."
            )
            return

        questions = self.quiz.questions

        # Use to find the next question to show
        next_question = None
        index = questions.index(question)

        # Prefer the next question, otherwise the previous one if ending question was removed
        if index < len(questions) - 1:
            next_question = questions[index + 1]
        else:
            next_question = questions[index - 1]

        # Remove question from both Quiz instance and UI
        self.quiz.remove_question(question.question_id)
        self.screen.remove_question(question, next_question)

    def _on_question_reorder_requested(
        self, question: Question, new_question_num: int
    ) -> None:
        """
        Internal method. Intended to be called when a question is requested to be reordered, or, in other words,
        have its question number changed.

        Gets the question that was requested by the user to be reordered, and moves it to the new question number
        requested. The Quiz instance and UI are both updated to reflect these changes.

        Arguments:
            question: The Question instance to reorder. A Question instance is used as it contains the question
                ID needed for moving the question.

            new_question_num: The new question number to move the current question to. The number is not a
                zero-based index, but the question number starting from 1. An integer is used as a question
                number is naturally represented by a whole number integer.

        Returns:
            None.
        """
        # Move question in the Quiz instance and force UI to reflect the changes
        self.quiz.move_question(question.question_id, new_question_num - 1)
        self.screen.update_question_order()

    def _on_discard_requested(self) -> None:
        """
        Internal method. Intended to be called when the user wishes to discard all the changes they made in the
        current session before the last manual save, and return to the manager.

        Checks if the quiz has actually been changed since the last manual save and that the quiz is not in
        read-only mode. If both conditions are true, the user is warned before the quiz state from the last
        manual save is written to disk to overwrite any possible changes by the autosave, and the user is returned
        to the quiz manager screen.

        Returns:
            None.
        """
        # Only checks if the quiz is not the same as the last manual save, not autosave
        if self.quiz_changed(only_manual=True) and not self.read_only:
            confirm = confirm_warning(
                self.screen,
                "Discard All Changes?",
                "Are you sure you want to discard all changes you made since saving this quiz?",
            )

            # Save last manual save state back to disk, to overwrite any autosave progress
            if confirm:
                self.quiz_repo.save(self.checkpoint_quiz)
        else:
            confirm = True

        # Returns back to quiz manager
        if confirm:
            self.screen.clear_questions()
            self.screen.go_to(Screen.COMMON_QUIZ_MANAGER)

    def _on_save_requested(self) -> None:
        """
        Internal method. Intended to be called when the user wishes to save all changes they made to disk and
        return to the quiz manager screen.

        Checks if the quiz has any errors before saving. If it does, the quiz is marked as unable to be played,
        but is still saved to disk. If the quiz is unable to be played, the user is shown with a warning asking
        if they want to fix the issues now or later. The last manually saved checkpoint is also updated. If no
        changes were made, nothing is saved to disk and the user is returned back to the quiz manager immediately.

        Returns:
            None.
        """
        # Quiz is incomplete if it has errors
        has_errors = self._check_for_errors()
        self.quiz.is_complete = not has_errors

        # Remove any empty C and D answers, only if it is complete
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

            # Stay in the quiz editor
            if not confirm:
                return

        # Returns back to quiz manager
        self.screen.clear_questions()
        self.screen.go_to(Screen.COMMON_QUIZ_MANAGER)

    def _autosave(self) -> None:
        """
        Internal method. Intended to be called by the autosave timer automatically. Saves the current quiz state
        to disk in case of a crash or corruption that causes the user to lose data. The quiz is only saved to
        disk if changes have been made and the quiz is not in read-only mode.

        Returns:
            None.
        """
        if self.quiz_changed() and not self.read_only:
            # Checks if quiz is ready to play or not in this autosave
            has_errors = self._check_for_errors()
            self.quiz.is_complete = not has_errors

            # Save to disk without showing its own status
            self.save_quiz(show_status=False)
            self.screen.set_status("Auto-saved quiz", 2000)

    def _check_for_errors(self) -> bool:
        """
        Internal method. Checks if the current quiz that is being edited (not the checkpoint quizzes) has any
        validation failures in any of the questions, meaning it cannot be safely played.

        Returns:
            A boolean determining whether the quiz has errors or not. Returns True if at least one error was
            detected in the quiz, else, returns False if no validation issues were present.
        """
        for question in self.quiz.questions:
            errors = question.validate_question()

            if errors:
                return True

        return False

    def on_enter(self, payload: dict) -> None:
        # Does not change any data if returning from question preview
        if self.screen.returning_from_preview:
            self.screen.returning_from_preview = False
            return

        # Save a copy of original quiz for checking if changes were made later.
        # Deep copy is required to ensure changes to the original quiz are not
        # reflected in its child mutables, e.g. lists.
        self.quiz = payload["quiz"]
        self.checkpoint_quiz = deepcopy(self.quiz)
        self.last_saved_quiz = deepcopy(self.quiz)

        # If pre-made (default) quiz, set read-only mode
        self.read_only = self.quiz.is_premade

        # Set and show questions on UI
        self.screen.set_quiz(self.quiz, self.read_only)

        # If brand-new quiz, create starter blank question
        if not self.read_only and not self.quiz.questions:
            self.create_new_question()

        # If not read-only mode, start autosaver
        if not self.read_only:
            self.autosave_timer.start()

    def on_leave(self) -> None:
        # Stop autosave timer to save CPU usage when screen is not used
        self.autosave_timer.stop()

    def on_window_close(self, event: QCloseEvent) -> None:
        # If the quiz has been changed since last saved, warn the user
        if self.quiz_changed() and not self.read_only:
            # Saves whether the quiz is safe to play or not prematurely
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
                # Remove any empty C and D answers
                if not has_errors:
                    for question in self.quiz.questions:
                        question.remove_empty_answers(mutate_answers=True)

                # Save quiz to disk and allow window to close
                self.save_quiz()
                event.accept()
            elif action == QMessageBox.StandardButton.Discard:
                # Save last saved state (not from autosave) and allow window to close
                self.quiz_repo.save(self.checkpoint_quiz)
                event.accept()
            else:
                # If user pressed Cancel, don't close the window
                event.ignore()
