from core.app.screen_ids import Screens
from core.services.game_client import GameClient
from models.payloads import QuestionPayload

from typing import TYPE_CHECKING

# Needed to avoid circular imports
if TYPE_CHECKING:
    from ui.main_window import MainWindow


class ClientAppController:
    """Global client-side logic, connected to MainWindow."""

    def __init__(self, window, services) -> None:
        super().__init__()
        self.window: MainWindow = window
        self.client: GameClient = services.client

        # Client
        self.client.countdown_started.connect(self.on_countdown_started)
        self.client.question_received.connect(self.on_question_received)
        self.client.kicked.connect(self.on_kicked)
        self.client.error_occurred.connect(self.on_error_occurred)
        self.client.invalid_action_occurred.connect(self.on_invalid_action_occurred)

    def on_kicked(self, reason: str) -> None:
        """When the client has been kicked."""
        self.window.reset_status()
        self.window.set_status("Disconnected from server", 5000)

        self.window.go_to(Screens.CLIENT_DISCONNECT, {"reason": reason})

    def on_error_occurred(self, reason: str) -> None:
        """When the client has been kicked due to an error."""
        self.window.reset_status()
        self.window.set_status("Disconnected from server (unexpected error)", 5000)

        self.window.go_to(Screens.CLIENT_DISCONNECT, {"reason": reason})
        self.window.show_error(
            "Protocol Error",
            f"The connection was terminated by the server due to a communication error.\n\nReason: {reason}",
        )

    def on_invalid_action_occurred(self, reason: str) -> None:
        """When the client has sent a request deemed invalid by the server."""
        self.window.set_status("Invalid action rejected by sever", 5000)

        self.window.show_warning(
            "Invalid Action",
            f"The server rejected the request because it is not valid in the current state.\n\nReason: {reason}",
        )

    def on_countdown_started(self, duration: int) -> None:
        """When the question countdown has started."""
        self.window.go_to(Screens.COMMON_COUNTDOWN, {"duration": duration * 1000})
        self.window.set_status("Counting down...")

    def on_question_received(self, data: dict) -> None:
        """When the question data is received."""
        self.window.go_to(
            Screens.CLIENT_MULTI_QUESTION, QuestionPayload.from_dict(data)
        )
        self.window.set_status("Waiting for answer")
