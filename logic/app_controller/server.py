from typing import TYPE_CHECKING

from core.services.app_context import Services
from core.app.screen_ids import Screens
from core.services.game_server import GameServer
from core.game.game_controller import GameController
from data.quiz_repo import QuizRepository
from models.payloads import QuestionPayload

if TYPE_CHECKING:
    from ui.main_window import MainWindow


class ServerAppController:
    """Global server-side logic, connected to MainWindow."""

    def __init__(self, window: "MainWindow", services: Services) -> None:
        super().__init__()
        self.window: MainWindow = window
        self.server: GameServer = services.server
        self.controller: GameController = services.controller
        self.quiz_repo: QuizRepository = services.quiz_repo

        self.server.player_joined.connect(self.on_player_joined)
        self.server.player_left.connect(self.on_player_left)

        self.controller.start_countdown.connect(self.on_start_countdown)
        self.controller.start_question.connect(self.on_start_question)

    def on_player_joined(self, nickname: str) -> None:
        player_id = self.server.registry.get_id_by_nickname(nickname)
        player = self.server.registry.get(player_id).player

        self.controller.add_player(player)

    def on_player_left(self, nickname: str) -> None:
        player_id = self.server.registry.get_id_by_nickname(nickname)
        self.controller.remove_player(player_id)

    def on_start_countdown(self, duration: int) -> None:
        self.server.send_countdown_start(duration)
        self.window.go_to(Screens.COMMON_COUNTDOWN, {"duration": duration * 1000})

        self.window.handle_status("Counting down...")

    def on_start_question(self, question_info: QuestionPayload) -> None:
        self.server.send_question_data(question_info.to_dict())
        self.window.go_to(Screens.SERVER_MULTI_QUESTION, question_info)

        self.window.handle_status("In question")
