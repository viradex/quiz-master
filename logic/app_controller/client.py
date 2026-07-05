from typing import TYPE_CHECKING

from core.services.app_context import Services
from core.app.screen_ids import Screens
from core.services.game_client import GameClient
from models.payloads import QuestionPayload

if TYPE_CHECKING:
    from ui.main_window import MainWindow


class ClientAppController:
    """Global client-side logic, connected to MainWindow."""

    def __init__(self, window: "MainWindow", services: Services) -> None:
        super().__init__()
        self.window: MainWindow = window
        self.client: GameClient = services.client

        self.client.countdown_started.connect(self.on_countdown_started)
        self.client.question_data.connect(self.on_question_data)
        self.client.kick.connect(self.on_kick)
        self.client.error.connect(self.on_error)
        self.client.invalid_action.connect(self.on_invalid_action)

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

    def on_countdown_started(self, duration: int) -> None:
        self.window.go_to(Screens.COMMON_COUNTDOWN, {"duration": duration * 1000})
        self.window.handle_status("Counting down...")

    def on_question_data(self, data: dict) -> None:
        self.window.go_to(
            Screens.CLIENT_MULTI_QUESTION, QuestionPayload.from_dict(data)
        )
        self.window.handle_status("Waiting for answer")
