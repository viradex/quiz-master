"""
quiz_setup.py

The logic respective to the common quiz setup screen.
"""

from core.app.screen_ids import Screen
from core.services.app_context import Services
from data.quiz_repo import QuizRepository
from logic.base_logic import BaseLogic
from models.quiz import Quiz
from ui.screens.common.quiz_editor import CommonQuizEditorScreen


class CommonQuizSetupLogic(BaseLogic):
    """
    Creates the quiz setup logic class, inheriting BaseLogic. This logic is part of the 'common' category.

    This logic class is responsible for allowing creating a new quiz, or editing an existing quiz, and saving
    the details to disk.

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

        # Screen PyQt signal connections
        self.screen.save_requested.connect(self._on_save_requested)

    def _on_save_requested(self, data: dict, edit_questions: bool = True) -> None:
        """
        Internal method. Intended to be called when the user wishes to save the quiz, and possibly further edit
        the questions it contains, or return back to the quiz manager screen.

        If the details entered were for a new quiz, a brand new blank Quiz instance is created. The title is
        checked to see if it exists, and if it does, the user is warned about it (however, they are not prevented
        from making the quiz). The quiz is then saved and the quiz editor is opened.

        If the details were entered for an existing quiz, the existing quiz is retrieved from disk, and the title
        and shuffle properties are updated before being saved back to disk. Then, if the user requested to further
        edit questions after saving changes, the quiz editor is opened. Otherwise, the quiz manager is re-opened
        again.

        Arguments:
            data: The data required to update the Quiz instance. If creating a new quiz, only the 'quiz_title'
                and 'do_shuffle' properties are needed; the 'quiz_id' should not be provided. If editing an
                existing quiz, the 'quiz_id' should be provided alongside the other two values previously
                mentioned. A dictionary is used to group these similar values in one argument, allowing scalability.

            edit_questions: Whether to open the quiz editor screen after saving the quiz to disk, or to open the
                quiz manager screen. If set to True, the quiz editor is opened. Otherwise, the quiz manager is
                opened. A boolean is used as this is naturally a binary value with only yes or no.

        Returns:
            None.
        """
        # If this value is provided, the quiz already existed. Otherwise, the quiz is new.
        quiz_id = data.get("quiz_id")

        # Quiz already exists, so edit an existing quiz from disk
        if quiz_id is not None:
            quiz = self.quiz_repo.get(quiz_id)
            if quiz is None:
                return

            # Set properties from setup screen
            quiz.quiz_title = data["quiz_title"]
            quiz.do_shuffle = data["do_shuffle"]
        else:
            # Create new blank quiz if it doesn't exist with some data provided in setup
            quiz = Quiz(
                Quiz.generate_random_id(),
                data["quiz_title"],
                [],
                data["do_shuffle"],
                is_premade=False,
                is_complete=False,
            )

            # Get all custom quiz titles (not default quizzes) to see if it exists or not
            all_quizzes = self.quiz_repo.get_all()
            custom_quiz_titles = [
                q.quiz_title for q in all_quizzes.values() if not q.is_premade
            ]

            # Confirms that the user still wishes to make the quiz if the title already exists
            if quiz.quiz_title in custom_quiz_titles:
                confirm = self.screen.show_question(
                    "Create Duplicate Quiz?",
                    f'A quiz named "{quiz.quiz_title}" already exists. Do you want to create another quiz with this name?',
                )

                if not confirm:
                    return

        # Saves the quiz to the disk, overwriting it if it exists
        self.quiz_repo.save(quiz)

        if edit_questions:
            self.screen.go_to(Screen.COMMON_QUIZ_EDITOR, {"quiz": quiz})
        else:
            self.screen.go_to(Screen.COMMON_QUIZ_MANAGER)
