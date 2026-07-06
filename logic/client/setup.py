from ui.screens.client.setup import ClientSetupScreen
from logic.base_logic import BaseLogic
from core.services.game_client import GameClient
from core.app.screen_ids import Screens
from core.app.enums import ClientConnectionError

from core.config.constants import CLIENT_CONNECTION_TIMEOUT


class ClientSetupLogic(BaseLogic):
    def __init__(self, screen, services) -> None:
        super().__init__()
        self.screen: ClientSetupScreen = screen
        self.game_client: GameClient = services.client

        # Screen
        self.screen.submitted.connect(self.handle_submit)

        # Client
        self.game_client.connected.connect(self.on_connected)
        self.game_client.connection_failed.connect(self.on_connection_failed)

    def handle_submit(self, data: dict[str, str]) -> None:
        """When the client submits connection details. Shows loading screen."""
        self.game_client.set_ip(data["ip"])
        self.game_client.set_nickname(data["nickname"])

        self.game_client.connect()
        self.screen.set_status("Connecting to server...")

        self.screen.go_to(
            Screens.COMMON_LOADING,
            {"loading_msg": "Connecting...", "status_msg": "Connecting to server..."},
        )

    def on_connected(self) -> None:
        """When successfully connected to the server."""
        self.screen.go_to(Screens.CLIENT_LOBBY)
        self.screen.set_status("In lobby")

    def on_connection_failed(self, reason: ClientConnectionError) -> None:
        """When the connection to the server failed. Shows an error modal window displaying the reason."""
        self.screen.go_to(Screens.CLIENT_SETUP)

        self.screen.reset_status()
        self.screen.set_status("Failed to connect", 5000)

        if reason == ClientConnectionError.CONNECTION_REFUSED:
            self.screen.show_error(
                "Failed to Connect",
                "Unable to connect to the server. The connection was refused. Please try again.",
            )
        elif reason == ClientConnectionError.TIMEOUT:
            self.screen.show_error(
                "Failed to Connect",
                f"Unable to connect to the server. The server did not respond within {CLIENT_CONNECTION_TIMEOUT} seconds. Please try again.",
            )
        elif reason == ClientConnectionError.UNREACHABLE:
            self.screen.show_error(
                "Failed to Connect",
                "Unable to connect to the server. The server is unreachable. Please try again.",
            )
        elif reason == ClientConnectionError.INVALID:
            self.screen.show_error(
                "Failed to Connect",
                "Unable to connect to the server. The IP address is invalid for connecting to a server. Please try again.",
            )
        elif reason == ClientConnectionError.CONNECTION_RESET:
            self.screen.show_error(
                "Failed to Connect",
                "Unable to connect to the server. The connection was forcibly closed by the server. Please try again.",
            )
        elif reason == ClientConnectionError.CONNECTION_ABORTED:
            self.screen.show_error(
                "Failed to Connect",
                "Unable to connect to the server. The connection was aborted. Please try again.",
            )
        elif reason == ClientConnectionError.PERMISSION:
            self.screen.show_error(
                "Failed to Connect",
                "Unable to connect to the server. Permission denied. Please try again.",
            )
        elif reason == ClientConnectionError.UNKNOWN:
            self.screen.show_error(
                "Failed to Connect",
                "Unable to connect to the server. An unknown error occurred. Please try again.",
            )
