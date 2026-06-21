from ui.screens.client.setup import ClientSetupScreen
from logic.base_logic import BaseLogic
from core.services.app_context import GameClient
from core.app.screen_ids import Screens


class ClientSetupLogic(BaseLogic):
    def __init__(self, screen, services):
        super().__init__()
        self.screen: ClientSetupScreen = screen
        self.game_client: GameClient = services.client

        self.screen.submitted.connect(self.handle_submit)

        self.game_client.connecting.connect(self.on_connecting)
        self.game_client.connection_success.connect(self.on_connection_success)
        self.game_client.connection_fail.connect(self.on_connection_fail)

    def handle_submit(self, data):
        self.game_client.set_ip(data["ip"])
        self.game_client.set_nickname(data["nickname"])
        self.game_client.set_random_player_id()

        self.game_client.connect()

    def on_connecting(self):
        self.screen.go_to(
            Screens.COMMON_LOADING,
            {"loading_msg": "Connecting...", "status_msg": "Connecting to server..."},
        )

    def on_connection_success(self):
        self.screen.go_to(Screens.CLIENT_LOBBY)

    def on_connection_fail(self, reason):
        self.screen.go_to(Screens.CLIENT_SETUP)

        if reason == "unreachable":
            self.screen.show_connection_error(
                "Failed to Connect",
                "Unable to connect to the server. Please check your internet connection and try again.",
            )
        elif reason == "refused":
            self.screen.show_connection_error(
                "Failed to Connect",
                "Unable to connect to the server. The connection was refused. Please verify the IP is correct and try again.",
            )
