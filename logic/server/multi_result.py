from ui.screens.server.multi_result import ServerMultiResultScreen
from logic.base_logic import BaseLogic
from core.services.game_server import GameServer
from core.app.screen_ids import Screens
from core.game.game_controller import GameController
from data.quiz_repo import QuizRepository
from models.payloads import ClientFinalResultsPayload, ServerFinalResultsPayload


class ServerMultiResultLogic(BaseLogic):
    def __init__(self, screen, services) -> None:
        super().__init__()
        self.screen: ServerMultiResultScreen = screen
        self.server: GameServer = services.server
        self.controller: GameController = services.controller
        self.quiz_repo: QuizRepository = services.quiz_repo

        self.screen.next_question.connect(self.on_next_question)

        self.controller.final_results.connect(self.on_final_results)

    def on_next_question(self) -> None:
        self.controller.start_next_question()

    def on_final_results(
        self,
        global_data: ServerFinalResultsPayload,
        individual_data: dict[str, ClientFinalResultsPayload],
    ) -> None:
        self.screen.go_to(Screens.SERVER_FINAL_RESULT, global_data)

        for player_id, data in individual_data.items():
            self.server.send_final_results(player_id, data.to_dict())

        self.server.stop()
