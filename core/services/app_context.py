from core.services.game_client import GameClient
from core.services.game_server import GameServer
from core.game.game_controller import GameController
from data.quiz_repo import QuizRepository


class Services:
    """Contains app services."""

    def __init__(self) -> None:
        self.client = GameClient()
        self.server = GameServer()
        self.controller = GameController()
        self.quiz_repo = QuizRepository()
