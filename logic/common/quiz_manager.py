from ui.screens.common.quiz_manager import CommonQuizManagerScreen
from logic.base_logic import BaseLogic
from data.quiz_repo import QuizRepository
from core.app.screen_ids import Screens
from core.app.enums import QuizSortingOrder
from models.quiz import Quiz


class CommonQuizManagerLogic(BaseLogic):
    def __init__(self, screen, services) -> None:
        super().__init__()
        self.screen: CommonQuizManagerScreen = screen
        self.quiz_repo: QuizRepository = services.quiz_repo

        self.quizzes: dict[str, Quiz] | None = None

        self.current_search = ""
        self.current_sort = QuizSortingOrder.NEWEST

        self.screen.edit_requested.connect(self.on_edit_requested)
        self.screen.delete_requested.connect(self.on_delete_requested)
        self.screen.search_requested.connect(self.on_search_requested)
        self.screen.sort_requested.connect(self.on_sort_requested)

    def refresh_quizzes(self):
        self.quiz_repo.refresh_cache()
        self.quizzes = self.quiz_repo.get_all()

        quizzes = list(self.quizzes.values())
        if quizzes is None:
            return

        # Sort
        if self.current_search:
            quizzes = [
                q
                for q in quizzes
                if self.current_search.lower() in q.quiz_title.lower()
            ]

        # Filter
        # Separate quizzes ensuring the unique sorting that happens in some
        # places doesn't affect the other. Also, the UI prefers them split
        custom_quizzes = [q for q in quizzes if not q.is_premade]
        default_quizzes = [q for q in quizzes if q.is_premade]

        # Default quizzes don't have an updated_at field, so for sorting related
        # to dates, they sort alphabetically instead
        if self.current_sort == QuizSortingOrder.NEWEST:
            custom_quizzes.sort(key=lambda q: q.updated_at, reverse=True)
            default_quizzes.sort(key=lambda q: q.quiz_title)

        elif self.current_sort == QuizSortingOrder.OLDEST:
            custom_quizzes.sort(key=lambda q: q.updated_at)
            default_quizzes.sort(key=lambda q: q.quiz_title)

        elif self.current_sort == QuizSortingOrder.NAME_ASC:
            custom_quizzes.sort(key=lambda q: q.quiz_title)
            default_quizzes.sort(key=lambda q: q.quiz_title)

        elif self.current_sort == QuizSortingOrder.NAME_DESC:
            custom_quizzes.sort(key=lambda q: q.quiz_title, reverse=True)
            default_quizzes.sort(key=lambda q: q.quiz_title, reverse=True)

        quizzes = custom_quizzes + default_quizzes

        self.screen.remove_all_quizzes()
        self.screen.add_quizzes(quizzes, do_default_spacing=True)

    def on_edit_requested(self, quiz_id: str) -> None:
        self.quiz_repo.refresh_cache()
        quiz = self.quiz_repo.get(quiz_id)

        if quiz is None:
            self.screen.show_error(
                "Quiz Not Found", "The quiz selected no longer exists."
            )
            self.refresh_quizzes()
            return

        if not quiz.is_premade:
            self.screen.go_to(
                Screens.COMMON_QUIZ_SETUP,
                {
                    "quiz_id": quiz_id,
                    "quiz_title": quiz.quiz_title,
                    "do_shuffle": quiz.do_shuffle,
                },
            )
        else:
            self.screen.go_to(Screens.COMMON_QUIZ_EDITOR, {"quiz": quiz})

    def on_delete_requested(self, quiz_id: str) -> None:
        self.quiz_repo.refresh_cache()
        quiz = self.quiz_repo.get(quiz_id)

        if quiz is None:
            self.screen.show_error(
                "Quiz Not Found", "The quiz selected no longer exists."
            )
        elif quiz.is_premade:
            self.screen.show_error(
                "Cannot Delete Default Quiz",
                "Default quizzes cannot be deleted. Only custom quizzes may be modified.",
            )
            return

        self.quiz_repo.remove(quiz_id)
        self.refresh_quizzes()

    def on_search_requested(self, query: str) -> None:
        self.current_search = query
        self.refresh_quizzes()

    def on_sort_requested(self, sort_order: QuizSortingOrder) -> None:
        self.current_sort = sort_order
        self.refresh_quizzes()

    def on_enter(self, payload=None) -> None:
        self.refresh_quizzes()
