from ui.screens.client.final_result import ClientFinalResultScreen
from logic.base_logic import BaseLogic
from core.services.game_client import GameClient


class ClientFinalResultLogic(BaseLogic):
    def __init__(self, screen, services) -> None:
        super().__init__()
        self.screen: ClientFinalResultScreen = screen
        self.game_client: GameClient = services.client
