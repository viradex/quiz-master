from core.services.app_context import Services
from core.app.screen_ids import Screens


class AppController:
    """Global logic, connected to MainWindow and generally used to catch general network/app errors."""

    def __init__(self, window, services) -> None:
        super().__init__()
        self.window = window
        self.services: Services = services

        self.services.client.kick.connect(self.on_kick)
        self.services.client.error.connect(self.on_error)
        self.services.client.invalid_action.connect(self.on_invalid_action)

    def on_kick(self, reason: str) -> None:
        self.window.handle_status_reset()
        self.window.handle_status("Disconnected from server", 5000)

        self.window.go_to(Screens.CLIENT_DISCONNECT, {"reason": reason})

    def on_error(self, reason: str) -> None:
        self.window.handle_status_reset()
        self.window.handle_status("Disconnected from server (unexpected error)", 5000)

        self.window.go_to(Screens.CLIENT_DISCONNECT, {"reason": reason})
        self.window.show_error(
            "Protocol Error",
            f"The connection was terminated by the server due to a communication error.\n\nReason: {reason}",
        )

    def on_invalid_action(self, reason: str) -> None:
        self.window.handle_status("Invalid action rejected by sever", 5000)

        self.window.show_warning(
            "Invalid Action",
            f"The server rejected the request because it is not valid in the current state.\n\nReason: {reason}",
        )
