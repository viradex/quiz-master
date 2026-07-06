from ui.screens.server.final_result import ServerFinalResultScreen
from logic.base_logic import BaseLogic
from core.services.game_server import GameServer
from core.game.game_controller import GameController
from data.quiz_repo import QuizRepository


class ServerFinalResultLogic(BaseLogic):
    def __init__(self, screen, services) -> None:
        super().__init__()
        self.screen: ServerFinalResultScreen = screen
        self.server: GameServer = services.server
        self.controller: GameController = services.controller
        self.quiz_repo: QuizRepository = services.quiz_repo
