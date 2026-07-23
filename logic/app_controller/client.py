from PyQt6.QtGui import QCloseEvent

from core.app.screen_ids import Screens
from core.services.game_client import GameClient
from models.payloads import QuestionPayload

from ui.components.dialogs import confirm_warning

# Needed to avoid circular imports
from typing import TYPE_CHECKING

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

    def on_error_occurred(self, reason: str, from_who: str) -> None:
        """When the client has been kicked due to an error."""
        if from_who not in ("client", "server"):
            raise ValueError(f"Invalid 'from_who': {from_who}")

        self.window.reset_status()
        self.window.set_status("Disconnected from server (fatal error)", 5000)

        self.window.go_to(Screens.CLIENT_DISCONNECT, {"reason": reason})
        self.window.show_error(
            "Protocol Error",
            f"The connection was terminated by the {from_who} due to a fatal communication error.\n\nReason: {reason}",
        )

    def on_invalid_action_occurred(self, reason: str) -> None:
        """When the client has sent a request deemed invalid by the server."""
        self.window.set_status("Invalid action rejected by server", 5000)

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

    def on_window_close(self, event: QCloseEvent) -> None:
        if self.client.is_connected:
            confirm = confirm_warning(
                self.window,
                "Confirm Leaving",
                "Are you sure you want to disconnect from the server?",
            )

            if confirm:
                self.client.disconnect_client()
                event.accept()
            else:
                event.ignore()
