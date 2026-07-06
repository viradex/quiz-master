from ui.screens.client.disconnect import ClientDisconnectScreen
from logic.base_logic import BaseLogic
from core.services.game_client import GameClient


class ClientDisconnectLogic(BaseLogic):
    def __init__(self, screen, services) -> None:
        super().__init__()
        self.screen: ClientDisconnectScreen = screen
        self.game_client: GameClient = services.client
