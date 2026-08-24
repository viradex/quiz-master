"""
menu.py

The logic respective to the common main menu screen.
"""

from core.app.enums import ServerStartingError
from core.app.screen_ids import Screen
from core.services.app_context import Services
from core.services.game_server import GameServer
from data.quiz_repo import QuizRepository
from logic.base_logic import BaseLogic
from ui.screens.common.menu import CommonMenuScreen
from utils.error_messages import SERVER_STARTING_ERROR_MESSAGES


class CommonMenuLogic(BaseLogic):
    """
    Creates the main menu logic class, inheriting BaseLogic. This logic is part of the 'common' category.

    This logic class is responsible for allowing the server to be started, as well as reporting any errors
    with starting server, if any occurred.

    Arguments:
        screen: The screen respective to this logic class, to allow listening to signals from it and invoking
            methods to modify the UI.

        services: All the application Services, to allow access to various functions of the application
            in one single wrapper class.
    """

    def __init__(self, screen: CommonMenuScreen, services: Services) -> None:
        super().__init__()
        self.screen: CommonMenuScreen = screen
        self.game_server: GameServer = services.server
        self.quiz_repo: QuizRepository = services.quiz_repo

        # Screen PyQt signal connections
        self.screen.started_server.connect(self._on_started_server)

        # Server PyQt signal connections
        self.game_server.started.connect(self._on_started)
        self.game_server.start_failed.connect(self._on_start_failed)

    def _on_started_server(self) -> None:
        """
        Internal method. Intended to be called when the user clicks the button for starting the server on the UI.

        The method checks for if there are any quizzes available, and if all those quizzes are completed. If
        either check fails, the server is prevented from starting until the user creates new quizzes and/or
        completes existing ones.

        Returns:
            None.
        """
        # Get all available quizzes to see if any can be played
        self.quiz_repo.refresh_cache()
        quizzes = self.quiz_repo.get_all()

        # No quizzes are in the directory
        if not quizzes:
            self.screen.show_error(
                "No Quizzes Available",
                "There are no quizzes available. You need at least one quiz before you can host a game. Create a quiz using the quiz manager, then try again.",
            )
            return

        # No quizzes are complete
        if not any(quiz.is_complete for quiz in quizzes.values()) or all(
            quiz.validate_quiz() for quiz in quizzes.values()
        ):
            self.screen.show_error(
                "No Complete Quizzes Available",
                "There are no quizzes available that are ready to play. Finish a quiz using the quiz editor, then try again.",
            )
            return

        # If all quiz validation checks pass, start the server
        self.game_server.start()
        self.screen.set_status("Starting...")

    def _on_started(self) -> None:
        """
        Internal method. Intended to be called when the server successfully starts.

        Shows the lobby UI screen.

        Returns:
            None.
        """
        self.screen.go_to(Screen.SERVER_LOBBY)
        self.screen.set_status("In lobby")

    def _on_start_failed(self, reason: ServerStartingError) -> None:
        """
        Internal method. Intended to be called when the server fails to start for any reason.

        The reason for the failure to connect is given as a ServerStartingError enum, which is in term used
        to provide a user-friendly error message to the client explaining the issue in an error modal box.

        Arguments:
            reason: The reason for the connection to fail, as a ServerStartingError enum. An enum is used
                as it is more type-safe than a regular string and provides easier readability.

        Returns:
            None.
        """
        self.screen.reset_status()
        self.screen.set_status("Failed to start server", 5000)

        # Get and show error message box
        message = SERVER_STARTING_ERROR_MESSAGES.get(
            reason, "An unknown error occurred."
        )

        self.screen.show_error(
            "Failed to Start",
            f"Unable to start the server. {message} Please try again.",
        )
