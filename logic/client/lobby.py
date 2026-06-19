from ui.screens.client.lobby import ClientLobbyScreen
from logic.base_logic import BaseLogic
from core.services.app_context import GameClient
from core.app.screen_ids import Screens


class ClientLobbyLogic(BaseLogic):
    def __init__(self, screen, services):
        super().__init__()
        self.screen: ClientLobbyScreen = screen
        self.game_client: GameClient = services.client

        self.game_client.kick.connect(self.on_kick)

    def on_kick(self, reason):
        self.screen.go_to(Screens.CLIENT_DISCONNECT, {"reason": reason})
