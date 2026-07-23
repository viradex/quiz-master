from core.app.screen_ids import Screens
from core.services.game_client import GameClient
from logic.base_logic import BaseLogic
from ui.screens.client.lobby import ClientLobbyScreen


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
        self.game_client.latency_updated.connect(self.on_latency_updated)

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

    def on_latency_updated(self, rtt: float) -> None:
        """When the round trip time is updated. Prompts UI to update it on UI."""
        if rtt == -1:
            self.screen.update_ping(None)
        else:
            self.screen.update_ping(rtt)

    def on_left_server(self) -> None:
        """When the client leaves the server."""
        self.game_client.disconnect_client()
        self.screen.go_to(Screens.COMMON_MENU)

        self.screen.reset_status()
        self.screen.set_status("Disconnected from server", 2000)
