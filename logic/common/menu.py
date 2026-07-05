from ui.screens.common.menu import CommonMenuScreen
from logic.base_logic import BaseLogic
from core.services.app_context import GameServer
from core.app.screen_ids import Screens


class CommonMenuLogic(BaseLogic):
    def __init__(self, screen, services) -> None:
        super().__init__()
        self.screen: CommonMenuScreen = screen
        self.game_server: GameServer = services.server

        self.screen.start_server.connect(self.handle_start)

        self.game_server.started.connect(self.on_started)
        self.game_server.start_failed.connect(self.on_start_failed)

    def handle_start(self) -> None:
        self.game_server.start()
        self.screen.set_status("Starting...")

    def on_started(self) -> None:
        self.screen.go_to(Screens.SERVER_LOBBY)
        self.screen.set_status("In lobby")

    def on_start_failed(self, reason: str) -> None:
        self.screen.reset_status()
        self.screen.set_status("Failed to start server", 5000)

        if reason == "in_use":
            self.screen.show_error(
                "Failed to Start",
                "Unable to start the server. Another instance of the server is already running on this device, or the port is in use. Please try again.",
            )
        if reason == "permission":
            self.screen.show_error(
                "Failed to Start",
                "Unable to start the server. Permission denied. Please try again.",
            )
        if reason == "invalid_ip":
            self.screen.show_error(
                "Failed to Start",
                "Unable to start the server. The server was attempted to be started on an IP that does not belong to the device. Please try again.",
            )
        if reason == "invalid":
            self.screen.show_error(
                "Failed to Start",
                "Unable to start the server. Invalid argument(s). Please try again.",
            )
        if reason == "unknown":
            self.screen.show_error(
                "Failed to Start",
                "Unable to start the server. An unknown error occurred. Please try again.",
            )
