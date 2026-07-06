from ui.screens.server.multi_question import ServerMultiQuestionScreen
from logic.base_logic import BaseLogic
from core.services.game_server import GameServer
from core.app.screen_ids import Screens
from core.game.game_controller import GameController
from data.quiz_repo import QuizRepository
from core.app.enums import AnswerValidationResult
from models.payloads import ClientResultsPayload, ServerResultsPayload


class ServerMultiQuestionLogic(BaseLogic):
    def __init__(self, screen, services) -> None:
        super().__init__()
        self.screen: ServerMultiQuestionScreen = screen
        self.server: GameServer = services.server
        self.controller: GameController = services.controller
        self.quiz_repo: QuizRepository = services.quiz_repo

        # Screen
        self.screen.question_skipped.connect(self.on_question_skipped)

        # Server
        self.server.answer_submitted.connect(self.on_answer_submitted)

        # Controller
        self.controller.question_results_ready.connect(self.on_question_results_ready)

    def on_question_skipped(self) -> None:
        """When the UI requests to skip a question."""
        self.screen.set_status("Skipped question", 2000)
        self.controller.skip_question()

    def on_answer_submitted(
        self, player_id: str, selected_index: int, received_time: float
    ) -> None:
        """When the server reports a player submitted an answer."""
        is_valid, reason = self.controller.is_answer_legal(
            selected_index, received_time
        )

        # If answer is invalid, sends info back to client about why it was so
        if not is_valid:
            if reason == AnswerValidationResult.TIME:
                message = "Answer submitted at invalid time"
            elif reason == AnswerValidationResult.ANSWER:
                message = "Invalid answer submitted"

            self.server.send_invalid_action(player_id, message)
            return

        # If answer is valid, adds it to count and lets controller read it
        self.screen.update_submission_count(1)
        self.controller.receive_answer(player_id, selected_index, received_time)

        nickname = self.server.registry.get(player_id).player.nickname
        self.screen.set_status(f"{nickname} submitted an answer", 2000)

    def on_question_results_ready(
        self,
        server_data: ServerResultsPayload,
        clients_data: dict[str, ClientResultsPayload],
    ) -> None:
        """When the question answer results are ready to be displayed."""
        self.screen.set_status("Showing results")
        self.screen.go_to(Screens.SERVER_MULTI_RESULT, server_data)

        for player_id, data in clients_data.items():
            self.server.send_question_results(player_id, data.to_dict())
