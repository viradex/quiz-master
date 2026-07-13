from ui.screens.client.lobby import ClientLobbyScreen
from logic.base_logic import BaseLogic
from core.services.game_client import GameClient
from core.app.screen_ids import Screens


class ClientLobbyLogic(BaseLogic):
    def __init__(self, screen, services) -> None:
        super().__init__()
        self.screen: ClientLobbyScreen = screen
        self.game_client: GameClient = services.client

        # Screen
        self.screen.left_server.connect(self.on_left_server)

        # Client
        self.game_client.connected.connect(self.on_connected)
        self.game_client.player_joined.connect(self.on_player_joined)
        self.game_client.player_left.connect(self.on_player_left)

    def on_connected(self, player_list: list[str]) -> None:
        """When successfully connected to the server. Prompts UI to show player list."""
        own_nickname = self.game_client.nickname

        # Adds own player name as the first person in the lobby table
        if own_nickname in player_list:
            player_list.remove(own_nickname)
            player_list.insert(0, own_nickname)

        # Refreshes and adds all players to the lobby screen
        self.screen.reset_lobby()

        for player in player_list:
            is_you = player == own_nickname
            self.screen.add_player_lobby(player, is_you)

    def on_player_joined(self, nickname: str) -> None:
        """When a player joins. Prompts UI to add a player to the player list."""
        if nickname != self.game_client.nickname:
            self.screen.add_player_lobby(nickname, is_you=False)

    def on_player_left(self, nickname: str) -> None:
        """When another player leaves. Prompts UI to add a player to the player list."""
        self.screen.remove_player_lobby(nickname)

    def on_left_server(self) -> None:
        """When the client leaves the server."""
        self.game_client.disconnect_client()
        self.screen.go_to(Screens.COMMON_MENU)

        self.screen.reset_status()
        self.screen.set_status("Disconnected from server", 2000)

    def on_enter(self, payload=None) -> None:
        # Get IP and port of server to display in UI
        ip, port = self.game_client.get_server_address()
        self.screen.set_connection_details(ip, port)
