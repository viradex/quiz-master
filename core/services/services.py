from core.services.game_client import GameClient
from core.services.game_server import GameServer
from core.services.quiz_manager import QuizManager


class Services:
    def __init__(self):
        self.client = GameClient()
        self.server = GameServer()
        self.quiz_manager = QuizManager()
