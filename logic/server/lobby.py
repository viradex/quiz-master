from core.app.screen_ids import Screens
from core.game.game_controller import GameController
from core.services.game_server import GameServer
from data.quiz_repo import QuizRepository
from logic.base_logic import BaseLogic
from ui.screens.server.lobby import ServerLobbyScreen

from ui.components.dialogs import confirm_warning
from utils.networking import get_hostname
from utils.error_messages import (
    format_errors,
    QUIZ_ERROR_MESSAGES,
    QUESTION_ERROR_MESSAGES,
)
from utils.formatting import format_ping
from core.config.constants import MIN_PLAYERS_FOR_GAME


class ServerLobbyLogic(BaseLogic):
    def __init__(self, screen, services) -> None:
        super().__init__()
        self.screen: ServerLobbyScreen = screen
        self.server: GameServer = services.server
        self.controller: GameController = services.controller
        self.quiz_repo: QuizRepository = services.quiz_repo

        # Screen
        self.screen.player_info_requested.connect(self.on_player_info_requested)
        self.screen.player_kicked.connect(self.on_player_kicked)
        self.screen.game_started.connect(self.on_game_started)
        self.screen.server_closed.connect(self.on_server_closed)

        # Server
        self.server.player_joined.connect(self.on_player_joined)
        self.server.player_left.connect(self.on_player_left)
        self.server.latency_updated.connect(self.on_latency_updated)

    def on_player_joined(self, player_id: str, nickname: str) -> None:
        """When a player joins. Prompts UI to add a player to the player list."""
        self.screen.add_player_lobby(player_id, nickname)

    def on_player_left(self, player_id: str, nickname: str) -> None:
        """When a player leaves. Prompts UI to remove a player from the player list."""
        self.screen.remove_player_lobby(player_id)

    def on_latency_updated(self, player_id: str, rtt: float) -> None:
        """When a player's latency is updated. Prompts UI to update visual latency display."""
        self.screen.update_ping(player_id, rtt)

    def on_player_info_requested(self, player_id: str) -> None:
        """When player info is requested by the UI. Returns player info to user."""
        nickname = self.server.get_player(player_id).nickname

        ip, port = self.server.get_player_address(player_id)
        hostname = get_hostname(ip)

        latency = self.server.get_client_latency(player_id)

        if latency is None:
            latency_text = "Unknown"
        else:
            latency_text = format_ping(latency)

        self.screen.show_info(
            "Player Info",
            f"Player name: {nickname}\nPing: {latency_text}\n\nIP address: {ip}\nPort: {port}\nHostname: {hostname}",
        )

    def on_player_kicked(self, player_id: str) -> None:
        """When a player is requested to be kicked by the UI. Sends a request to kick the player to the server."""
        self.server.kick_player(player_id, "Kicked by host")
        self.screen.set_status("Kicked player", 2000)

    def on_game_started(self, quiz_id: str) -> None:
        """When the UI requests to start a game."""
        # Get number of players in server
        players = self.server.get_total_players()

        # Get all quiz names
        self.quiz_repo.refresh_cache()
        quiz = self.quiz_repo.get(quiz_id)

        # Validation
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

        issues: list[str] = []
        validation_errors = quiz.validate_quiz()

        if validation_errors:
            for error in QUIZ_ERROR_MESSAGES:
                if error in validation_errors:
                    issues.append(QUIZ_ERROR_MESSAGES[error])

            self.screen.show_error(
                "Quiz Errors",
                f"The program has found critical errors with this quiz that prevent it from being played.\n\n{format_errors(issues)}",
            )
            return

        # Even if quiz data reports no errors, check to ensure the file itself hasn't been tampered with
        for question_num, question in enumerate(quiz.questions, start=1):
            # The issues list should be empty if at this stage
            validation_errors = question.validate_question()

            if validation_errors:
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

        self.controller.load_quiz(quiz)
        self.controller.start_game()
        self.server.game_started = True

    def on_server_closed(self) -> None:
        """When the UI requests to stop the server."""
        # Do not show the confirmation if there aren't any players in the server
        if self.server.get_total_players() > 0:
            confirm = confirm_warning(
                self.screen,
                "Confirm Closing",
                "Are you sure you want to close the server and return to menu? All players in the server will be disconnected.",
            )
        else:
            confirm = True

        if not confirm:
            return

        self.server.stop()
        self.screen.go_to(Screens.COMMON_MENU)

        self.screen.reset_status()
        self.screen.set_status("Stopped server", 2000)

    def on_enter(self, payload=None) -> None:
        # Show all quiz names in dropdown screen in UI
        quizzes = self.quiz_repo.get_all()

        # Index 1 is the key of the dict, therefore look at index 1 for quiz data
        sorted_quizzes = dict(
            sorted(
                quizzes.items(),
                key=lambda quiz: (quiz[1].is_premade, quiz[1].quiz_title),
            )
        )

        quiz_names = {
            quiz_id: quiz.quiz_title
            for quiz_id, quiz in sorted_quizzes.items()
            if quiz.is_complete
        }

        for quiz_id, quiz in sorted_quizzes.items():
            if quiz.is_premade:
                quiz_names[quiz_id] += " (default)"

        self.screen.set_quizzes(quiz_names)
