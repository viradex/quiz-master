"""
lobby.py

The logic respective to the server lobby screen.
"""

from core.app.screen_ids import Screen
from core.config.constants import MIN_PLAYERS_FOR_GAME
from core.game.game_controller import GameController
from core.services.app_context import Services
from core.services.game_server import GameServer
from data.quiz_repo import QuizRepository
from logic.base_logic import BaseLogic
from models.quiz import Quiz
from ui.components.dialog import confirm_warning
from ui.screens.server.lobby import ServerLobbyScreen
from utils.error_messages import (
    QUESTION_ERROR_MESSAGES,
    QUIZ_ERROR_MESSAGES,
    format_errors,
)
from utils.formatting import format_ping


class ServerLobbyLogic(BaseLogic):
    """
    Creates the lobby logic class, inheriting BaseLogic. This logic is part of the 'server' category.

    This logic class is responsible for adding/removing players from the UI player list, and disconnecting
    the client if and when they wish to leave the server.

    Arguments:
        screen: The screen respective to this logic class, to allow listening to signals from it and invoking
            methods to modify the UI.

        services: All the application Services, to allow access to various functions of the application
            in one single wrapper class.
    """

    def __init__(self, screen: ServerLobbyScreen, services: Services) -> None:
        super().__init__()
        self.screen: ServerLobbyScreen = screen
        self.server: GameServer = services.server
        self.controller: GameController = services.controller
        self.quiz_repo: QuizRepository = services.quiz_repo

        # Screen PyQt signal connections
        self.screen.player_info_requested.connect(self._on_player_info_requested)
        self.screen.player_kicked.connect(self._on_player_kicked)
        self.screen.game_started.connect(self._on_game_started)
        self.screen.server_closed.connect(self._on_server_closed)

        # Server PyQt signal connections
        self.server.player_joined.connect(self._on_player_joined)
        self.server.player_left.connect(self._on_player_left)
        self.server.rtt_updated.connect(self._on_rtt_updated)

    def _on_player_info_requested(self, player_id: str) -> None:
        """
        Internal method. Intended to be called when the host requests detailed player information on a specific
        player.

        Retrieves and displays all available player information in an information modal box.

        Arguments:
            player_id: A string describing the ID of the player to get information about. A string is used as
                it can flexibly store IDs and can store many characters to make them more unique.

        Returns:
            None.
        """
        nickname = self.server.get_player(player_id).nickname
        address = self.server.get_client_address(player_id)

        # In normal operation, the address should never be None
        if address is not None:
            ip = address[0]
            port = address[1]
        else:
            ip = "N/A"
            port = "N/A"

        # The hostname can be unavailable if the reverse DNS lookup takes too long or fails
        hostname = self.server.get_client_hostname(player_id) or "N/A"

        # The RTT could still be calculating, therefore show 'Unknown' if that is the case
        rtt = self.server.get_client_rtt(player_id)
        rtt_text = format_ping(rtt) if rtt is not None else "Unknown"

        self.screen.show_info(
            "Player Info",
            f"Nickname: {nickname}\nPing: {rtt_text}\n\nIP address: {ip}\nPort: {port}\nHostname: {hostname}",
        )

    def _on_player_kicked(self, player_id: str) -> None:
        """
        Internal method. Intended to be called when the host wishes to kick a player.

        Kicks the player from the server. There is no confirmation prompt shown here.

        Arguments:
            player_id: A string describing the ID of the player to kick. A string is used as it can flexibly
                store IDs and can store many characters to make them more unique.

        Returns:
            None.
        """
        self.server.kick_player(player_id, "Kicked by host")
        self.screen.set_status("Kicked player", 2000)

    def _on_game_started(self, quiz_id: str) -> None:
        """
        Internal method. Intended to be called when the host wishes to begin the quiz game.

        The method begins by validating the conditions required to start a game, such as if a quiz has been
        selected, if there are enough players to start the game, and if the quiz is complete. If all initial
        checks pass, the logic performs more rigorous testing on the quiz as a whole, as well as individual
        questions, to ensure the quiz has not been tampered with and will not crash the server. If all the
        checks pass, the quiz is loaded and the quiz is started.

        Arguments:
            quiz_id: A string describing the ID of the quiz to play. A string is used as it can flexibly store
                IDs and can store many characters to make them more unique.

        Returns:
            None.
        """
        # Get number of players in server
        players = self.server.get_total_players()

        # Get the entire quiz from ID
        self.quiz_repo.refresh_cache()
        quiz = self.quiz_repo.get(quiz_id)

        # Perform validation, which should have already been performed by the UI.
        # However, this validation is more accurate as the UI validation bases
        # it off of UI state, which can be potentially inaccurate.
        if quiz is None:
            self.screen.show_error(
                "Invalid Conditions for Start", "The quiz selected does not exist."
            )
            return
        elif players < MIN_PLAYERS_FOR_GAME:
            self.screen.show_error(
                "Invalid Conditions for Start",
                "There are not enough players to start the game.",
            )
            return
        elif not quiz.is_complete:
            self.screen.show_error(
                "Invalid Conditions for Start",
                "The quiz is incomplete and cannot be used to host a game yet.",
            )
            return

        # Store issues for quizzes, and if no errors in quizzes, questions
        issues: list[str] = []

        # Start by validating the quiz as a whole for any corruption errors
        validation_errors = quiz.validate_quiz()

        if validation_errors:
            # If there are errors, display them to the user with user-friendly messages
            for error in QUIZ_ERROR_MESSAGES:
                if error in validation_errors:
                    issues.append(QUIZ_ERROR_MESSAGES[error])

            self.screen.show_error(
                "Quiz Errors",
                f"The program has found critical errors with this quiz that prevent it from being played.\n\n{format_errors(issues)}",
            )
            return

        # Even if the quiz is_complete is True, check again to ensure the
        # file itself hasn't been tampered with.
        for question_num, question in enumerate(quiz.questions, start=1):
            # The issues list should be empty if at this stage, since no
            # errors should have been detected in the quiz.
            validation_errors = question.validate_question()

            if validation_errors:
                # If there are errors, display them to the user with user-friendly messages
                for error in QUESTION_ERROR_MESSAGES:
                    if error in validation_errors:
                        issues.append(QUESTION_ERROR_MESSAGES[error])

                self.screen.show_error(
                    "Quiz Question Errors",
                    f"The program has found errors with Question #{question_num} on this quiz that prevents it from being played.\n\n{format_errors(issues)}",
                )
                return

        # Remove any empty C and D answers, if not already done
        for question in quiz.questions:
            question.remove_empty_answers(mutate_answers=True)

        # Load the quiz and start the game
        self.controller.load_quiz(quiz)
        self.controller.start_game()
        self.server.game_started = True

    def _on_server_closed(self) -> None:
        """
        Internal method. Intended to be called when the user wishes to stop the server.

        If there are any players currently in the server, shows a confirmation asking to stop. If there are no
        players, the server stops anyways. The screen is switched to the main menu if the server is stopped.

        Returns:
            None.
        """
        # Do not show the confirmation if there aren't any players currently in the server
        if self.server.get_total_players() > 0:
            confirm = confirm_warning(
                self.screen,
                "Confirm Closing",
                "Are you sure you want to close the server and return to menu? All players in the server will be disconnected.",
            )

            if not confirm:
                return

        # Stop the server and return to main menu
        self.server.stop()
        self.screen.go_to(Screen.COMMON_MENU)

        self.screen.reset_status()
        self.screen.set_status("Stopped server", 2000)

    def _on_player_joined(self, player_id: str, nickname: str) -> None:
        """
        Internal method. Intended to be called when a player joins the server.

        Adds the player name to the lobby UI, along with the hidden player ID for easier unique identification.

        Arguments:
            player_id: The player ID of the player that joined. A string is used as it can flexibly store
                IDs and can store many characters to make them more unique.

            nickname: The nickname of the player that joined. A string is used as a nickname is easily
                represented by a string.

        Returns:
            None.
        """
        self.screen.add_player_lobby(player_id, nickname)

    def _on_player_left(self, player_id: str, nickname: str) -> None:
        """
        Internal method. Intended to be called when a player leaves the server.

        Removes the player name from the lobby UI, along with the hidden player ID.

        Arguments:
            player_id: The player ID of the player that left. A string is used as it can flexibly store
                IDs and can store many characters to make them more unique.

            nickname: The nickname of the player that left. This value is unused by the method, however, is
                required to exist as the signal that calls this forces the nickname argument.

        Returns:
            None.
        """
        self.screen.remove_player_lobby(player_id)

    def _on_rtt_updated(self, player_id: str, rtt: float) -> None:
        """
        Internal method. Intended to be called when the round-trip time for a certain client has been updated.

        Updates the round-trip time color on the lobby screen for a specific player.

        Arguments:
            player_id: The player ID that the round-trip time was calculated for. A string is used as it can
                flexibly store IDs and can store many characters to make them more unique.

            rtt: The time taken to communicate to the client and back in milliseconds, with decimal precision,
                or None if no time has been calculated yet. A float is used for decimal precision.

        Returns:
            None.
        """
        self.screen.update_rtt_color(player_id, rtt)

    def on_enter(self, payload: None = None) -> None:
        # Get all quizzes on disk
        self.quiz_repo.refresh_cache()
        quizzes = self.quiz_repo.get_all()

        valid_quizzes: dict[str, Quiz] = {}

        for quiz_id, quiz in quizzes.items():
            # Only add the quiz to valid quizzes if there are no errors returned in the set
            if not quiz.validate_quiz():
                valid_quizzes[quiz_id] = quiz

        # Index 1 is the value of the dict, therefore look at index 1 for quiz data
        sorted_quizzes = dict(
            sorted(
                valid_quizzes.items(),
                key=lambda quiz: (quiz[1].is_premade, quiz[1].quiz_title),
            )
        )

        # Filter out incomplete quizzes
        quiz_names = {
            quiz_id: quiz.quiz_title
            for quiz_id, quiz in sorted_quizzes.items()
            if quiz.is_complete
        }

        # Append '(default)' if the quiz is a default quiz
        for quiz_id, quiz in sorted_quizzes.items():
            if quiz.is_premade:
                quiz_names[quiz_id] += " (default)"

        # Set quizzes in UI dropdown
        self.screen.set_quizzes(quiz_names)
