from ui.screens.client.multi_result import ClientMultiResultScreen
from logic.base_logic import BaseLogic
from core.services.app_context import GameClient
from core.app.screen_ids import Screens
from models.payloads import ClientFinalResultsPayload


class ClientMultiResultLogic(BaseLogic):
    def __init__(self, screen, services) -> None:
        super().__init__()
        self.screen: ClientMultiResultScreen = screen
        self.game_client: GameClient = services.client

        self.game_client.final_results_data.connect(self.on_final_results_data)

    def on_final_results_data(self, data: dict) -> None:
        self.screen.go_to(
            Screens.CLIENT_FINAL_RESULT, ClientFinalResultsPayload.from_dict(data)
        )
