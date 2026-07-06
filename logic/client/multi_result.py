from ui.screens.client.multi_result import ClientMultiResultScreen
from logic.base_logic import BaseLogic
from core.services.game_client import GameClient
from core.app.screen_ids import Screens
from models.payloads import ClientFinalResultsPayload


class ClientMultiResultLogic(BaseLogic):
    def __init__(self, screen, services) -> None:
        super().__init__()
        self.screen: ClientMultiResultScreen = screen
        self.game_client: GameClient = services.client

        # Screen
        self.screen.left_server.connect(self.on_left_server)

        # Client
        self.game_client.final_results_received.connect(self.on_final_results_received)

    def on_left_server(self) -> None:
        """When the client leaves the server."""
        self.game_client.disconnect_client()
        self.screen.go_to(Screens.COMMON_MENU)

        self.screen.reset_status()
        self.screen.set_status("Disconnected from server", 2000)

    def on_final_results_received(self, data: dict) -> None:
        """When the client receives final results."""
        self.screen.set_status("Showing final results")
        self.screen.go_to(
            Screens.CLIENT_FINAL_RESULT, ClientFinalResultsPayload.from_dict(data)
        )
