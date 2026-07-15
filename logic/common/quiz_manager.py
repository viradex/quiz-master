from core.app.enums import QuizSortingOrder
from core.app.screen_ids import Screens
from data.quiz_repo import QuizRepository
from models.quiz import Quiz
from logic.base_logic import BaseLogic
from ui.screens.common.quiz_manager import CommonQuizManagerScreen


class CommonQuizManagerLogic(BaseLogic):
    def __init__(self, screen, services) -> None:
        super().__init__()
        self.screen: CommonQuizManagerScreen = screen
        self.quiz_repo: QuizRepository = services.quiz_repo

        # Values for logic
        self.quizzes: dict[str, Quiz] | None = None
        self.current_search = ""
        self.current_sort = QuizSortingOrder.NEWEST

        # Screen
        self.screen.edit_requested.connect(self.on_edit_requested)
        self.screen.delete_requested.connect(self.on_delete_requested)
        self.screen.search_requested.connect(self.on_search_requested)
        self.screen.sort_requested.connect(self.on_sort_requested)

    def refresh_quizzes(self) -> None:
        """Refresh the quiz list in the UI. Applies filter and search as defined in
        `self.current_sort` and `self.current_search`, respectively."""
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

        # Refresh UI
        self.screen.remove_all_quizzes()
        self.screen.add_quizzes(quizzes)

    def on_edit_requested(self, quiz: Quiz) -> None:
        """Open the setup screen in Edit mode. If the quiz is a default quiz,
        directly opens the editor in read-only mode."""
        self.quiz_repo.refresh_cache()

        if not quiz.is_premade:
            self.screen.go_to(
                Screens.COMMON_QUIZ_SETUP,
                {
                    "quiz_id": quiz.quiz_id,
                    "quiz_title": quiz.quiz_title,
                    "do_shuffle": quiz.do_shuffle,
                },
            )
        else:
            # Skips setup screen if default quiz
            self.screen.go_to(Screens.COMMON_QUIZ_EDITOR, {"quiz": quiz})

    def on_delete_requested(self, quiz: Quiz) -> None:
        """Deletes a quiz from disk and removes it from the UI. Default quizzes cannot be deleted."""
        self.quiz_repo.refresh_cache()

        if quiz.is_premade:
            self.screen.show_error(
                "Cannot Delete Default Quiz",
                "Default quizzes cannot be deleted. Only custom quizzes may be modified.",
            )
            return

        self.quiz_repo.remove(quiz.quiz_id)
        self.refresh_quizzes()

    def on_search_requested(self, query: str) -> None:
        """Applies the search query and refreshes UI."""
        self.current_search = query
        self.refresh_quizzes()

    def on_sort_requested(self, sort_order: QuizSortingOrder) -> None:
        """Applies the sort order and refreshes UI."""
        self.current_sort = sort_order
        self.refresh_quizzes()

    def on_enter(self, payload=None) -> None:
        self.refresh_quizzes()
