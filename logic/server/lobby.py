from ui.screens.server.lobby import ServerLobbyScreen
from logic.base_logic import BaseLogic
from core.services.app_context import GameServer
from core.app.screen_ids import Screens
from utils.networking import get_hostname


class ServerLobbyLogic(BaseLogic):
    def __init__(self, screen, services) -> None:
        super().__init__()
        self.screen: ServerLobbyScreen = screen
        self.server: GameServer = services.server

        self.server.player_joined.connect(self.on_player_joined)
        self.server.player_left.connect(self.on_player_left)

        self.screen.get_player_info.connect(self.on_get_player_info)
        self.screen.kick_player.connect(self.on_kick_player)
        self.screen.close_server.connect(self.on_close_server)

    def on_player_joined(self, nickname: str) -> None:
        self.screen.add_player_lobby(nickname)
        self.screen.set_status("Player joined", 2000)

    def on_player_left(self, nickname: str) -> None:
        self.screen.remove_player_lobby(nickname)
        self.screen.set_status("Player left", 2000)

    def on_get_player_info(self, nickname: str) -> None:
        player_id = self.server.get_id_from_nickname(nickname)

        ip, port = self.server.get_player_address(player_id)
        hostname = get_hostname(ip)

        self.screen.show_player_info(nickname, ip, port, hostname)

    def on_kick_player(self, nickname: str) -> None:
        player_id = self.server.get_id_from_nickname(nickname)
        self.server.kick_player(player_id, "Kicked by host")

        self.screen.set_status("Kicked player", 2000)

    def on_close_server(self) -> None:
        self.server.stop()
        self.screen.go_to(Screens.COMMON_MENU)

        self.screen.reset_status()
        self.screen.set_status("Stopped server", 2000)
