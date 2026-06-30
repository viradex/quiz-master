from typing import TYPE_CHECKING
import time
from PyQt6.QtCore import QTimer

from core.services.app_context import Services
from core.app.screen_ids import Screens
from core.services.game_client import GameClient

if TYPE_CHECKING:
    from ui.main_window import MainWindow


class ClientAppController:
    """Global client-side logic, connected to MainWindow."""

    def __init__(self, window: MainWindow, services: Services) -> None:
        super().__init__()
        self.window: MainWindow = window
        self.client: GameClient = services.client

        self.client.start_countdown.connect(self.on_start_countdown)
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

    def on_start_countdown(self, start_time: float, duration: int) -> None:
        # TODO does not account for network latency
        now = time.time()
        remaining = (start_time + duration) - now

        self.window.go_to(Screens.COMMON_COUNTDOWN, {"duration": duration})

        remaining_ms = max(0, int(remaining * 1000))
        QTimer.singleShot(remaining_ms, self._on_countdown_finish)

    def _on_countdown_finish(self) -> None:
        self.window.go_to(Screens.CLIENT_MULTI_QUESTION)
