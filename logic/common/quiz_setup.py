from ui.screens.common.quiz_editor import CommonQuizEditorScreen
from logic.base_logic import BaseLogic
from data.quiz_repo import QuizRepository
from core.app.screen_ids import Screens
from models.quiz import Quiz


class CommonQuizSetupLogic(BaseLogic):
    def __init__(self, screen, services) -> None:
        super().__init__()
        self.screen: CommonQuizEditorScreen = screen
        self.quiz_repo: QuizRepository = services.quiz_repo

        self.screen.save_requested.connect(self.on_save_requested)

    def on_save_requested(self, data: dict) -> None:
        quiz_id = data.get("quiz_id")

        if quiz_id is not None:
            self.quiz_repo.edit(quiz_id, data)
            return

        quiz = Quiz(
            Quiz.generate_random_id(), data["quiz_title"], [], data["do_shuffle"], False
        )

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
        self.screen.go_to(Screens.COMMON_QUIZ_EDITOR, {"quiz": quiz})
