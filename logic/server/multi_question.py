from ui.screens.server.multi_question import ServerMultiQuestionScreen
from logic.base_logic import BaseLogic
from core.services.game_server import GameServer
from core.app.screen_ids import Screens
from core.game.game_controller import GameController
from data.quiz_repo import QuizRepository


class ServerMultiQuestionLogic(BaseLogic):
    def __init__(self, screen, services) -> None:
        super().__init__()
        self.screen: ServerMultiQuestionScreen = screen
        self.server: GameServer = services.server
        self.controller: GameController = services.controller
        self.quiz_repo: QuizRepository = services.quiz_repo

        self.server.answer_submitted.connect(self.on_answer_submitted)

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

        self.controller.receive_answer(player_id, selected_index, received_time)
        self.screen.update_submission_count(1)
