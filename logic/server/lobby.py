from ui.screens.server.lobby import ServerLobbyScreen
from logic.base_logic import BaseLogic
from core.services.game_server import GameServer
from core.app.screen_ids import Screens
from core.game.game_controller import GameController
from data.quiz_repo import QuizRepository

from utils.networking import get_hostname
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

    def on_player_joined(self, player_id: str, nickname: str) -> None:
        """When a player joins. Prompts UI to add a player to the player list."""
        self.screen.add_player_lobby(player_id, nickname)

    def on_player_left(self, player_id: str, nickname: str) -> None:
        """When a player leaves. Prompts UI to remove a player from the player list."""
        self.screen.remove_player_lobby(player_id)

    def on_player_info_requested(self, player_id: str) -> None:
        """When player info is requested by the UI. Returns player info to user."""
        # TODO The logic reaches too deep into the server and knows too much about the registry
        # and where the nickname is stored. The server should instead have its own method to
        # expose the registry.
        nickname = self.server.registry.get(player_id).player.nickname

        ip, port = self.server.get_player_address(player_id)
        hostname = get_hostname(ip)

        self.screen.show_info(
            "Player Info",
            f"Player name: {nickname}\n\nIP address: {ip}\nPort: {port}\nHostname: {hostname}",
        )

    def on_player_kicked(self, player_id: str) -> None:
        """When a player is requested to be kicked by the UI. Sends a request to kick the player to the server."""
        self.server.kick_player(player_id, "Kicked by host")
        self.screen.set_status("Kicked player", 2000)

    def on_game_started(self, quiz_id: str) -> None:
        """When the UI requests to start a game."""
        # Get number of players in server
        players = len(self.server.registry.get_all())

        # Get all quiz names
        self.quiz_repo.refresh_cache()
        quiz = self.quiz_repo.load_quiz(quiz_id)

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

        self.controller.load_quiz(quiz)
        self.controller.start_game()
        self.server.game_started = True

    def on_server_closed(self) -> None:
        """When the UI requests to stop the server."""
        self.server.stop()
        self.screen.go_to(Screens.COMMON_MENU)

        self.screen.reset_status()
        self.screen.set_status("Stopped server", 2000)

    def on_enter(self):
        # Show all quiz names in dropdown screen in UI
        quizzes = self.quiz_repo.load_quizzes()
        quiz_names = {quiz_id: quiz.quiz_title for quiz_id, quiz in quizzes.items()}

        for quiz_id, quiz in quizzes.items():
            if quiz.is_premade:
                quiz_names[quiz_id] += " (default)"

        self.screen.set_quizzes(quiz_names)
