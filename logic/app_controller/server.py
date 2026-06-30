from typing import TYPE_CHECKING
import time
from PyQt6.QtCore import QTimer

from core.services.app_context import Services
from core.app.screen_ids import Screens
from core.services.game_server import GameServer
from core.game.game_controller import GameController
from data.quiz_repo import QuizRepository

if TYPE_CHECKING:
    from ui.main_window import MainWindow


class ServerAppController:
    """Global server-side logic, connected to MainWindow."""

    def __init__(self, window: MainWindow, services: Services) -> None:
        super().__init__()
        self.window: MainWindow = window
        self.server: GameServer = services.server
        self.controller: GameController = services.controller
        self.quiz_repo: QuizRepository = services.quiz_repo

        self.server.player_joined.connect(self.on_player_joined)
        self.server.player_left.connect(self.on_player_left)

        self.controller.start_countdown.connect(self.on_start_countdown)

    def on_player_joined(self, nickname: str) -> None:
        player_id = self.server.registry.get_id_by_nickname(nickname)
        player = self.server.registry.get(player_id).player

        self.controller.add_player(player)

    def on_player_left(self, nickname: str) -> None:
        player_id = self.server.registry.get_id_by_nickname(nickname)
        self.controller.remove_player(player_id)

    def on_start_countdown(self, time_info: dict) -> None:
        start_time = time_info["start_time"]
        duration = time_info["duration"]

        self.server.send_countdown_start(start_time, duration)

        now = time.time()
        remaining = (start_time + duration) - now

        self.window.go_to(Screens.COMMON_COUNTDOWN, {"duration": duration})

        remaining_ms = max(0, int(remaining * 1000))
        QTimer.singleShot(remaining_ms, self._on_countdown_finish)

    def _on_countdown_finish(self) -> None:
        self.window.go_to(Screens.SERVER_MULTI_QUESTION)
