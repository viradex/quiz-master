from ui.screens.server.multi_question import ServerMultiQuestionScreen
from logic.base_logic import BaseLogic
from core.services.game_server import GameServer
from core.app.screen_ids import Screens
from core.game.game_controller import GameController
from data.quiz_repo import QuizRepository
from models.payloads import ClientResultsPayload, ServerResultsPayload


class ServerMultiQuestionLogic(BaseLogic):
    def __init__(self, screen, services) -> None:
        super().__init__()
        self.screen: ServerMultiQuestionScreen = screen
        self.server: GameServer = services.server
        self.controller: GameController = services.controller
        self.quiz_repo: QuizRepository = services.quiz_repo

        self.screen.question_skipped.connect(self.on_question_skipped)

        self.server.answer_submitted.connect(self.on_answer_submitted)

        self.controller.question_results.connect(self.on_question_results)

    def on_question_skipped(self) -> None:
        self.controller.skip_question()

    def on_answer_submitted(
        self, player_id: str, selected_index: int, received_time: float
    ) -> None:
        is_valid, reason = self.controller.is_answer_valid(
            selected_index, received_time
        )

        if not is_valid:
            if reason == "time":
                message = "Answer submitted at invalid time"
            elif reason == "answer":
                message = "Invalid answer submitted"

            self.server.send_invalid_answer(player_id, message)
            return

        self.screen.update_submission_count(1)
        self.controller.receive_answer(player_id, selected_index, received_time)

        nickname = self.server.registry.get(player_id).player.nickname
        self.screen.set_status(f"{nickname} submitted an answer", 2000)

    def on_question_results(
        self,
        global_data: ServerResultsPayload,
        individual_data: dict[str, ClientResultsPayload],
    ) -> None:
        self.screen.go_to(Screens.SERVER_MULTI_RESULT, global_data)

        for player_id, data in individual_data.items():
            self.server.send_question_results(player_id, data.to_dict())
