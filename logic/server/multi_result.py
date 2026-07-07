from ui.screens.server.multi_result import ServerMultiResultScreen
from logic.base_logic import BaseLogic
from core.services.game_server import GameServer
from core.app.screen_ids import Screens
from core.game.game_controller import GameController
from data.quiz_repo import QuizRepository
from models.payloads import ClientFinalResultsPayload, ServerFinalResultsPayload

from utils.networking import get_hostname


class ServerMultiResultLogic(BaseLogic):
    def __init__(self, screen, services) -> None:
        super().__init__()
        self.screen: ServerMultiResultScreen = screen
        self.server: GameServer = services.server
        self.controller: GameController = services.controller
        self.quiz_repo: QuizRepository = services.quiz_repo

        # Screen
        self.screen.next_question_requested.connect(self.on_next_question_requested)
        self.screen.end_game_requested.connect(self.on_end_game_requested)
        self.screen.player_info_requested.connect(self.on_player_info_requested)
        self.screen.player_kicked.connect(self.on_player_kicked)

        # Server
        self.server.player_left.connect(self.on_player_left)

        # Controller
        self.controller.final_results_ready.connect(self.on_final_results_ready)

    def on_player_left(self, player_id: str, nickname: str) -> None:
        """When a player leaves the server."""
        self.screen.remove_player(nickname)

    def on_next_question_requested(self) -> None:
        """When the next question is requested."""
        self.controller.start_next_question()

    def on_end_game_requested(self) -> None:
        """When the game is requested to be ended prematurely."""
        self.controller.finish_quiz()

    def on_player_info_requested(self, nickname: str) -> None:
        """When player info is requested by the UI. Returns player info to user."""
        player_id = self.server.registry.get_id_by_nickname(nickname)

        ip, port = self.server.get_player_address(player_id)
        hostname = get_hostname(ip)

        self.screen.show_player_info(nickname, ip, port, hostname)

    def on_player_kicked(self, nickname: str) -> None:
        """When a player is requested to be kicked by the UI.
        Sends a request to kick the player to the server."""
        player_id = self.server.registry.get_id_by_nickname(nickname)
        self.server.kick_player(player_id, "Kicked by host")

        self.screen.set_status("Kicked player", 2000)
        self.screen.remove_player(nickname)

    def on_final_results_ready(
        self,
        global_data: ServerFinalResultsPayload,
        individual_data: dict[str, ClientFinalResultsPayload],
    ) -> None:
        """When the final results are ready to be displayed."""
        self.screen.set_status("Showing final results")
        self.screen.go_to(Screens.SERVER_FINAL_RESULT, global_data)

        # Send data to each individual player
        for player_id, data in individual_data.items():
            self.server.send_final_results(player_id, data.to_dict())

        # Disconnect users, since no more data is needed to be transferred
        # The clients should've been disconnected by themselves at this point,
        # so this should happen silently
        self.server.stop("Game over")
