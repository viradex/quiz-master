from core.app.screen_ids import Screens
from core.game.game_controller import GameController
from core.services.game_server import GameServer
from models.payloads import ClientFinalResultsPayload, ServerFinalResultsPayload
from logic.base_logic import BaseLogic
from ui.screens.server.multi_result import ServerMultiResultScreen

from utils.formatting import format_ping
from utils.networking import get_hostname


class ServerMultiResultLogic(BaseLogic):
    def __init__(self, screen, services) -> None:
        super().__init__()
        self.screen: ServerMultiResultScreen = screen
        self.server: GameServer = services.server
        self.controller: GameController = services.controller

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
        self.screen.remove_player(player_id)

    def on_next_question_requested(self) -> None:
        """When the next question is requested."""
        self.controller.start_next_question()

    def on_end_game_requested(self) -> None:
        """When the game is requested to be ended prematurely."""
        self.controller.finish_quiz()

    def on_player_info_requested(self, player_id: str) -> None:
        """When player info is requested by the UI. Returns player info to user."""
        nickname = self.server.get_player(player_id).nickname

        ip, port = self.server.get_player_address(player_id)
        hostname = get_hostname(ip)

        latency = self.server.get_client_latency(player_id)
        latency_text = format_ping(latency)

        self.screen.show_info(
            "Player Info",
            f"Player name: {nickname}\nPing: {latency_text}\n\nIP address: {ip}\nPort: {port}\nHostname: {hostname}",
        )

    def on_player_kicked(self, player_id: str) -> None:
        """When a player is requested to be kicked by the UI. Sends a request to kick the player to the server."""
        self.server.kick_player(player_id, "Kicked by host")
        self.screen.set_status("Kicked player", 2000)

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

        # Disconnect users, since no more data is needed to be transferred now
        # The clients should've disconnected themselves at this point,
        # so this should happen silently and they shouldn't get the disconnection screen
        self.server.stop("Game over")
