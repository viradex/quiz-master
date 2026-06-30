from ui.screens.client.setup import ClientSetupScreen
from logic.base_logic import BaseLogic
from core.services.app_context import GameClient
from core.app.screen_ids import Screens


class ClientSetupLogic(BaseLogic):
    def __init__(self, screen, services) -> None:
        super().__init__()
        self.screen: ClientSetupScreen = screen
        self.game_client: GameClient = services.client

        self.screen.submitted.connect(self.handle_submit)

        self.game_client.connection_success.connect(self.on_connection_success)
        self.game_client.connection_fail.connect(self.on_connection_fail)

    def handle_submit(self, data: dict[str, str]) -> None:
        self.game_client.set_ip(data["ip"])
        self.game_client.set_nickname(data["nickname"])

        self.game_client.connect()
        self.screen.set_status("Connecting to server...")

        self.screen.go_to(
            Screens.COMMON_LOADING,
            {"loading_msg": "Connecting...", "status_msg": "Connecting to server..."},
        )

    def on_connection_success(self) -> None:
        self.screen.go_to(Screens.CLIENT_LOBBY)
        self.screen.set_status("In lobby")

    def on_connection_fail(self, reason: str) -> None:
        self.screen.go_to(Screens.CLIENT_SETUP)

        self.screen.reset_status()
        self.screen.set_status("Failed to connect", 5000)

        if reason == "refused":
            self.screen.show_error(
                "Failed to Connect",
                "Unable to connect to the server. The connection was refused. Please try again.",
            )
        elif reason == "timeout":
            self.screen.show_error(
                "Failed to Connect",
                "Unable to connect to the server. The server did not respond within a certain period of time. Please try again.",
            )
        elif reason == "unreachable":
            self.screen.show_error(
                "Failed to Connect",
                "Unable to connect to the server. The server is unreachable. Please try again.",
            )
