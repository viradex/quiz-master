"""
quiz_manager.py

The logic respective to the common quiz manager screen.
"""

from core.app.enums import QuizSortingOrder
from core.app.screen_ids import Screen
from core.services.app_context import Services
from data.quiz_repo import QuizRepository
from logic.base_logic import BaseLogic
from models.quiz import Quiz
from ui.components.dialog import confirm_warning
from ui.screens.common.quiz_manager import CommonQuizManagerScreen
from utils.error_messages import QUIZ_ERROR_MESSAGES, format_errors


class CommonQuizManagerLogic(BaseLogic):
    """
    Creates the quiz manager logic class, inheriting BaseLogic. This logic is part of the 'common' category.

    This logic class is responsible for displaying all the quizzes currently saved on disk, and allowing the
    user to sort and search through the quizzes, as well as edit/delete their own custom quizzes and preview
    default quizzes.

    Arguments:
        screen: The screen respective to this logic class, to allow listening to signals from it and invoking
            methods to modify the UI.

        services: All the application Services, to allow access to various functions of the application
            in one single wrapper class.
    """

    def __init__(self, screen: CommonQuizManagerScreen, services: Services) -> None:
        super().__init__()
        self.screen: CommonQuizManagerScreen = screen
        self.quiz_repo: QuizRepository = services.quiz_repo

        # Values for logic
        self.quizzes: list[Quiz] = []
        self.invalid_quizzes: list[Quiz] = []

        # Current modifications/filters to list
        self.current_search: str = ""
        self.current_sort: QuizSortingOrder = QuizSortingOrder.NEWEST

        # Used for counter at top of screen
        self.total_quizzes: int = 0
        self.custom_quizzes: int = 0

        # Screen PyQt signal connections
        self.screen.edit_requested.connect(self._on_edit_requested)
        self.screen.delete_requested.connect(self._on_delete_requested)
        self.screen.invalid_quiz_info_requested.connect(
            self._on_invalid_quiz_info_requested
        )
        self.screen.search_requested.connect(self._on_search_requested)
        self.screen.sort_requested.connect(self._on_sort_requested)

    def refresh_quizzes(self, on_first_load: bool = False) -> None:
        """
        Refreshes the list of quizzes in the UI, applying any search criteria defined in the attributes, as
        well as any search query. The quizzes are sorted by the custom quizzes first, then the default quizzes,
        sorted separately (for example, alphabetical sorting applies to the custom and default quizzes as if
        completely separate).

        If this is being called when the screen is first shown, the total number of quizzes and custom quizzes
        is also saved and displayed.

        Any quizzes that are corrupted at the file level are not shown in the quiz list. If a quiz is incomplete,
        they are still shown in the quiz list, however.

        Arguments:
            on_first_load: A boolean that determines whether this method is being called when the screen is being
                shown or simply when the sorting/search criteria have been modified. If True, the total and custom
                quiz numbers are updated. Otherwise, they are untouched. Defaults to False.

        Returns:
            None.
        """
        # Refresh cache in case quizzes have been modified on disk
        self.quiz_repo.refresh_cache()
        self.invalid_quizzes.clear()

        quizzes = self.quiz_repo.get_all()
        self.quizzes = list(quizzes.values())

        valid_quizzes = []

        # If there are quizzes with corruption errors, do not show them in the list
        for quiz in self.quizzes:
            errors = quiz.validate_quiz(critical_only=True)

            if errors:
                self.invalid_quizzes.append(quiz)
            else:
                valid_quizzes.append(quiz)

        self.quizzes = valid_quizzes

        # Search by lowercase criteria, contains-style search
        if self.current_search:
            self.quizzes = [
                q
                for q in self.quizzes
                if self.current_search.lower() in q.quiz_title.lower()
            ]

        # Filter
        # Separate quizzes ensuring the unique sorting that happens in some
        # places doesn't affect the other. Also, the UI prefers them split.
        custom_quizzes = [q for q in self.quizzes if not q.is_premade]
        default_quizzes = [q for q in self.quizzes if q.is_premade]

        # Default quizzes don't have an updated_at field, so for sorting related
        # to dates, they sort alphabetically instead.
        if self.current_sort is QuizSortingOrder.NEWEST:
            custom_quizzes.sort(key=lambda q: q.updated_at, reverse=True)
            default_quizzes.sort(key=lambda q: q.quiz_title)
        elif self.current_sort is QuizSortingOrder.OLDEST:
            custom_quizzes.sort(key=lambda q: q.updated_at)
            default_quizzes.sort(key=lambda q: q.quiz_title)
        elif self.current_sort is QuizSortingOrder.TITLE_ASC:
            custom_quizzes.sort(key=lambda q: q.quiz_title)
            default_quizzes.sort(key=lambda q: q.quiz_title)
        elif self.current_sort is QuizSortingOrder.TITLE_DESC:
            custom_quizzes.sort(key=lambda q: q.quiz_title, reverse=True)
            default_quizzes.sort(key=lambda q: q.quiz_title, reverse=True)

        self.quizzes = custom_quizzes + default_quizzes

        # Refresh UI
        self.screen.remove_all_quizzes()
        self.screen.add_quizzes(self.quizzes)

        # Only update the totals when first loading, with no search criteria
        # or sorting, to avoid the numbers from changing when applying those.
        if on_first_load:
            self.total_quizzes = len(self.quizzes)
            self.custom_quizzes = len(custom_quizzes)
            self.screen.set_quizzes_number(self.total_quizzes, self.custom_quizzes)

    def subtract_from_counter(self, include_custom: bool = True) -> None:
        """
        Subtracts one from the UI counters, used when removing a single quiz. If removing a default quiz, set
        `include_custom` to False. Otherwise, set it to True.

        Arguments:
            include_custom: Whether to subtract one from the custom quizzes counter as well as the total quizzes
                counter. Defaults to True.

        Returns:
            None.
        """
        self.total_quizzes -= 1

        if include_custom:
            self.custom_quizzes -= 1

        self.screen.set_quizzes_number(self.total_quizzes, self.custom_quizzes)

    def _on_edit_requested(self, quiz: Quiz) -> None:
        """
        Internal method. Intended to be called when a quiz is requested to be edited by the user, or to be
        previewed if the quiz is a default quiz.

        If the quiz no longer exists, it is removed from the UI. If the quiz is not a default quiz, opens
        the quiz setup screen to allow editing the quiz details such as the title. Otherwise, the editor is
        opened directly if the quiz is a default quiz, as for those quizzes, the Edit button acts instead as
        the Preview button.

        Arguments:
            quiz: The Quiz instance to edit/preview. A Quiz instance is used as it can be easily used to
                extract specific needed details from it.

        Returns:
            None.
        """
        self.quiz_repo.refresh_cache()

        # Check if the quiz still exists
        if not self.quiz_repo.exists(quiz.quiz_id):
            self.screen.show_error(
                "Quiz Not Found",
                f"The quiz you're trying to {'preview' if quiz.is_premade else 'edit'} could not be found. It may have been deleted, or you may no longer have access to it.",
            )

            self.refresh_quizzes()

            # Don't subtract from the custom counter if it's a default quiz
            self.subtract_from_counter(include_custom=not quiz.is_premade)
            return

        if not quiz.is_premade:
            # Opens setup screen to allow editing high-level quiz details
            self.screen.go_to(
                Screen.COMMON_QUIZ_SETUP,
                {
                    "quiz_id": quiz.quiz_id,
                    "quiz_title": quiz.quiz_title,
                    "do_shuffle": quiz.do_shuffle,
                },
            )
        else:
            # Skips setup screen if default quiz; goes directly to editor to preview
            self.screen.go_to(Screen.COMMON_QUIZ_EDITOR, {"quiz": quiz})

    def _on_delete_requested(self, quiz: Quiz) -> None:
        """
        Internal method. Intended to be called when a quiz is requested to be deleted by the user. Default
        quizzes cannot be deleted.

        If the quiz no longer exists, it is removed from the UI. It removes the quiz save file from disk and
        updates the UI to remove it from the UI as well. The counters are also updated to reflect the removal.

        Arguments:
            quiz: The Quiz instance to remove. A Quiz instance is used as it can be easily used to get the quiz
                ID from it.

        Returns:
            None.
        """
        self.quiz_repo.refresh_cache()

        # Check if the quiz still exists
        if not self.quiz_repo.exists(quiz.quiz_id):
            self.screen.show_error(
                "Quiz Not Found",
                "The quiz you're trying to delete could not be found. It may have already been deleted.",
            )

            self.refresh_quizzes()
            self.subtract_from_counter()
            return

        if quiz.is_premade:
            # Should never happen in regular use; this is here as a safeguard
            self.screen.show_error(
                "Cannot Delete Default Quiz",
                "Default quizzes cannot be deleted. Only custom quizzes may be modified.",
            )
            return

        # Confirm before deleting
        confirm = confirm_warning(
            self.screen,
            "Confirm Deleting Quiz",
            f'Are you sure you want to permanently delete the quiz "{quiz.quiz_title}"? This cannot be undone!',
        )

        if not confirm:
            return

        # Remove from disk and refresh list to show that
        self.quiz_repo.remove(quiz.quiz_id)

        self.refresh_quizzes()
        self.subtract_from_counter()

    def _on_invalid_quiz_info_requested(self) -> None:
        """
        Internal method. Intended to be called when the user wishes to understand why certain quizzes could not
        be loaded onto the quiz list.

        Searches through the list of invalid quizzes and takes note of all the errors within each quiz that has
        issues. When done, displays all the errors in a warning modal box.

        Returns:
            None.
        """
        if not self.invalid_quizzes:
            # Should never happen under normal operation. This is here as defensive programming.
            self.screen.show_info(
                "No Invalid Quizzes", "No invalid quizzes were found in the quiz list."
            )
            self.screen.set_invalid_quizzes_visibility(False)
            return

        # Quiz title -> list of errors
        issues: dict[str, list[str]] = {}

        # Go through every invalid quiz and get a list of errors for each
        for quiz_num, quiz in enumerate(self.invalid_quizzes, start=1):
            quiz_errors: list[str] = []

            # Validate the quiz for only issues that prevent editing, not playing
            validation_errors = quiz.validate_quiz(critical_only=True)

            # Adds the user-friendly error messages
            for error in QUIZ_ERROR_MESSAGES:
                if error in validation_errors:
                    quiz_errors.append(QUIZ_ERROR_MESSAGES[error])

            # Set the key to the quiz title, or if that is corrupt, an increasing generic counter
            key = str(quiz.quiz_title) if quiz.quiz_title else f"Quiz #{quiz_num}"
            issues[key] = quiz_errors

        error_str = ""

        # Make a list for each quiz, labelled by its title as the subheading
        for title, errors in issues.items():
            error_str += f"{title}:\n{format_errors(errors)}\n\n"

        self.screen.show_warning(
            "Invalid Quizzes",
            f"The following quizzes contain invalid data and have been excluded from the quiz manager.\n\n{error_str}These issues must be fixed manually in the quiz file(s).",
        )

    def _on_search_requested(self, query: str) -> None:
        """
        Internal method. Intended to be called when the user updates the search query.

        Sets the query and updates the quiz list to only show quizzes that match the search query.

        Arguments:
            query: The query to search for in the quiz titles, to see if the titles contain the query. A string
                is used to allow flexibility in what can be searched for.

        Returns:
            None.
        """
        self.current_search = query
        self.refresh_quizzes()

    def _on_sort_requested(self, sort_order: QuizSortingOrder) -> None:
        """
        Internal method. Intended to be called when the user updates the sorting order.

        Sets the sorting order and updates the quiz list to show the quizzes in the correct order that the user
        requested.

        Arguments:
            sort_order: The order that the user wishes for the quizzes to be sorted in, as a QuizSortingOrder
                enum. An enum is used as opposed to a string to allow for better type safety and type hints.

        Returns:
            None.
        """
        self.current_sort = sort_order
        self.refresh_quizzes()

    def on_enter(self, payload: None = None) -> None:
        self.refresh_quizzes(on_first_load=True)

        # Set number of invalid quizzes after refresh_quizzes() has calculated it
        self.screen.set_invalid_quizzes_visibility(
            bool(self.invalid_quizzes), len(self.invalid_quizzes)
        )
