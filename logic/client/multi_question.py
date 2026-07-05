from ui.screens.client.multi_question import ClientMultiQuestionScreen
from logic.base_logic import BaseLogic
from core.services.app_context import GameClient
from core.app.screen_ids import Screens
from models.payloads import ClientResultsPayload


class ClientMultiQuestionLogic(BaseLogic):
    def __init__(self, screen, services) -> None:
        super().__init__()
        self.screen: ClientMultiQuestionScreen = screen
        self.game_client: GameClient = services.client

        self.screen.answer_submit.connect(self.on_answer_submit)

        self.game_client.results_data.connect(self.on_results_data)

    def on_answer_submit(self, index: int) -> None:
        self.game_client.send_answer_submit(index)
        self.screen.set_status("Answer submitted")

    def on_results_data(self, data: dict) -> None:
        self.screen.go_to(
            Screens.CLIENT_MULTI_RESULT, ClientResultsPayload.from_dict(data)
        )
