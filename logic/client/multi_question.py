from core.app.screen_ids import Screens
from core.services.game_client import GameClient
from models.payloads import ClientResultsPayload
from logic.base_logic import BaseLogic
from ui.screens.client.multi_question import ClientMultiQuestionScreen


class ClientMultiQuestionLogic(BaseLogic):
    def __init__(self, screen, services) -> None:
        super().__init__()
        self.screen: ClientMultiQuestionScreen = screen
        self.game_client: GameClient = services.client

        # Screen
        self.screen.answer_submitted.connect(self.on_answer_submitted)
        self.screen.left_server.connect(self.on_left_server)

        # Client
        self.game_client.results_received.connect(self.on_results_received)

    def on_answer_submitted(self, index: int) -> None:
        """When the user submits an answer."""
        self.game_client.send_answer_submit(index)
        self.screen.set_status("Answer submitted")

    def on_left_server(self) -> None:
        """When the client leaves the server."""
        self.game_client.disconnect_client()
        self.screen.go_to(Screens.COMMON_MENU)

        self.screen.reset_status()
        self.screen.set_status("Disconnected from server", 2000)

    def on_results_received(self, data: dict) -> None:
        """When the client receives question answer results."""
        self.screen.set_status("Showing results")
        self.screen.go_to(
            Screens.CLIENT_MULTI_RESULT, ClientResultsPayload.from_dict(data)
        )
