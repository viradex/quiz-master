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

        # Screen
        self.screen.next_question_requested.connect(self.on_next_question_requested)
        self.screen.end_game_requested.connect(self.on_end_game_requested)

        # Controller
        self.controller.final_results_ready.connect(self.on_final_results_ready)

    def on_next_question_requested(self) -> None:
        """When the next question is requested."""
        self.controller.start_next_question()

    def on_end_game_requested(self) -> None:
        """When the game is requested to be ended prematurely."""
        self.controller.finish_quiz()

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
