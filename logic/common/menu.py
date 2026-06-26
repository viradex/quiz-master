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

        self.game_server.start_success.connect(self.on_start_success)
        self.game_server.start_fail.connect(self.on_start_fail)

    def handle_start(self) -> None:
        self.game_server.start()
        self.screen.set_status("Starting...")

    def on_start_success(self) -> None:
        self.screen.go_to(Screens.SERVER_LOBBY)
        self.screen.set_status("In lobby")

    def on_start_fail(self, reason: str) -> None:
        self.screen.reset_status()
        self.screen.set_status("Failed to start server", 5000)

        if reason == "in_use":
            self.screen.show_error(
                "Server Already Running",
                "Another instance of the server is already running on this device. Only one server instance can be run per device.",
            )
