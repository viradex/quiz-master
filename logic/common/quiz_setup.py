from core.app.screen_ids import Screens
from data.quiz_repo import QuizRepository
from models.quiz import Quiz
from logic.base_logic import BaseLogic
from ui.screens.common.quiz_editor import CommonQuizEditorScreen


class CommonQuizSetupLogic(BaseLogic):
    def __init__(self, screen, services) -> None:
        super().__init__()
        self.screen: CommonQuizEditorScreen = screen
        self.quiz_repo: QuizRepository = services.quiz_repo

        # Screen
        self.screen.save_requested.connect(self.on_save_requested)

    def on_save_requested(self, data: dict, edit_questions: bool = True) -> None:
        """Update or create a new quiz on disk, and open the quiz editor if `edit_questions` is True."""
        quiz_id = data.get("quiz_id")

        # Quiz already exists
        if quiz_id is not None:
            # Edit existing quiz
            quiz = self.quiz_repo.get(quiz_id)
            if quiz is None:
                return

            quiz.quiz_title = data["quiz_title"]
            quiz.do_shuffle = data["do_shuffle"]

            self.quiz_repo.save(quiz)

            if edit_questions:
                self.screen.go_to(Screens.COMMON_QUIZ_EDITOR, {"quiz": quiz})
            else:
                self.screen.go_to(Screens.COMMON_QUIZ_MANAGER)

            return

        # Create new blank quiz if it doesn't exist with data provided in setup
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

        if quiz.quiz_title in custom_quiz_titles:
            confirm = self.screen.show_question(
                "Create Duplicate Quiz?",
                f'A quiz named "{quiz.quiz_title}" already exists. Do you want to create another quiz with this name?',
            )

            if not confirm:
                return

        self.quiz_repo.save(quiz)

        if edit_questions:
            self.screen.go_to(Screens.COMMON_QUIZ_EDITOR, {"quiz": quiz})
        else:
            self.screen.go_to(Screens.COMMON_QUIZ_MANAGER)
