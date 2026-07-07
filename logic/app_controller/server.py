from core.app.screen_ids import Screens
from core.services.game_server import GameServer
from core.game.game_controller import GameController
from data.quiz_repo import QuizRepository
from models.payloads import QuestionPayload

from typing import TYPE_CHECKING

# Needed to avoid circular imports
if TYPE_CHECKING:
    from ui.main_window import MainWindow


class ServerAppController:
    """Global server-side logic, connected to MainWindow."""

    def __init__(self, window, services) -> None:
        super().__init__()
        self.window: MainWindow = window
        self.server: GameServer = services.server
        self.controller: GameController = services.controller
        self.quiz_repo: QuizRepository = services.quiz_repo

        # Server
        self.server.player_joined.connect(self.on_player_joined)
        self.server.player_left.connect(self.on_player_left)

        # Controller
        self.controller.started_countdown.connect(self.on_started_countdown)
        self.controller.started_question.connect(self.on_started_question)
        self.controller.no_players_found.connect(self.on_no_players_found)

    def on_player_joined(self, nickname: str) -> None:
        """When a player joins. Adds player to the game controller."""
        player_id = self.server.registry.get_id_by_nickname(nickname)
        player = self.server.registry.get(player_id).player

        self.controller.add_player(player)
        self.window.set_status(f"{nickname} joined the game", 5000)

    def on_player_left(self, player_id: str, nickname: str) -> None:
        """When a player leaves. Removes player from the game controller."""
        self.controller.remove_player(player_id)
        self.window.set_status(f"{nickname} left the game", 5000)

    def on_started_countdown(self, duration: int) -> None:
        """When the question countdown has started."""
        self.server.send_countdown_start(duration)
        self.window.go_to(Screens.COMMON_COUNTDOWN, {"duration": duration * 1000})

        self.window.set_status("Counting down...")

    def on_started_question(self, question_info: QuestionPayload) -> None:
        """When the question data is received."""
        self.server.send_question_data(question_info.to_dict())
        self.window.go_to(Screens.SERVER_MULTI_QUESTION, question_info)

        self.window.set_status("In question")

    def on_no_players_found(self) -> None:
        """When the number of players has gone below the limited required players for a game."""
        self.window.reset_status()
        self.window.set_status("Game ended prematurely", 5000)

        self.server.stop("Game over")
        self.window.show_warning(
            "Quiz Ended Early",
            "There are not enough players to continue the quiz, so the game has ended prematurely.",
        )

        self.window.go_to(Screens.COMMON_MENU)
