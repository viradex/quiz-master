from ui.screens.server.lobby import ServerLobbyScreen
from logic.base_logic import BaseLogic
from core.services.app_context import GameServer
from core.app.screen_ids import Screens


class ServerLobbyLogic(BaseLogic):
    def __init__(self, screen, services):
        super().__init__()
        self.screen: ServerLobbyScreen = screen
        self.server: GameServer = services.server

        self.screen.close_server.connect(self.on_close_server)

        self.server.player_joined.connect(self.on_player_joined)

    def on_close_server(self):
        self.server.stop()
        self.screen.go_to(Screens.COMMON_MENU)

    def on_player_joined(self, nickname):
        self.screen.add_player_lobby(nickname)
