from ui.screens.client.lobby import ClientLobbyScreen
from logic.base_logic import BaseLogic
from core.services.app_context import GameClient
from core.app.screen_ids import Screens


class ClientLobbyLogic(BaseLogic):
    def __init__(self, screen, services):
        super().__init__()
        self.screen: ClientLobbyScreen = screen
        self.game_client: GameClient = services.client

        self.game_client.connection_success.connect(self.on_connection_success)
        self.game_client.player_joined.connect(self.on_player_joined)
        self.game_client.player_left.connect(self.on_player_left)
        self.game_client.player_list.connect(self.on_player_list)

        self.screen.leave_server.connect(self.on_leave_server)

    def on_connection_success(self):
        self.game_client.ask_player_list()

    def on_player_joined(self, player):
        if player != self.game_client.nickname:
            self.screen.add_player_lobby(player, is_you=False)

    def on_player_left(self, player):
        self.screen.remove_player_lobby(player)

    def on_player_list(self, player_list):
        own_nickname = self.game_client.nickname

        if own_nickname in player_list:
            player_list.remove(own_nickname)
            player_list.insert(0, own_nickname)

        self.screen.reset_lobby()

        for player in player_list:
            is_you = player == own_nickname
            self.screen.add_player_lobby(player, is_you=is_you)

    def on_leave_server(self):
        self.game_client.disconnect_client()
        self.screen.go_to(Screens.COMMON_MENU)

    def on_enter(self):
        ip, port = self.game_client.get_server_address()
        self.screen.set_connection_details(ip, port)
