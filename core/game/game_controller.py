import time
from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from core.game.quiz_manager import QuizManager
from models.player import Player
from models.leaderboard import Leaderboard
from models.quiz import Quiz
from models.question import Question
from core.config.constants import COUNTDOWN_TIME


class GameController(QObject):
    start_countdown = pyqtSignal(dict)

    def __init__(self) -> None:
        super().__init__()
        self.quiz_manager = QuizManager()

        self.game_running: bool = False
        self.question_running: bool = False

        self.current_question_index: int = -1

        self.countdown_start_monotonic: float | None = None
        self.countdown_end_monotonic: float | None = None

        self.countdown_start_wall: float | None = None
        self.countdown_duration: float | None = None

        self.question_start_time: float | None = None
        self.question_deadline: float | None = None

    def load_quiz(self, quiz: Quiz) -> None:
        self.quiz_manager.load_quiz(quiz)

    def add_player(self, player: Player) -> None:
        self.quiz_manager.add_player(player)

    def remove_player(self, player_id: str) -> None:
        self.quiz_manager.remove_player(player_id)

    def start_game(self) -> None:
        self.countdown_start()

    def end_game(self) -> None:
        pass

    def countdown_start(self) -> None:
        self.current_question_index += 1

        now_monotonic = time.monotonic()
        now_wall = time.time()

        self.countdown_start_monotonic = now_monotonic
        self.countdown_end_monotonic = now_monotonic + COUNTDOWN_TIME
        self.countdown_start_wall = now_wall

        self.start_countdown.emit(
            {"start_time": self.countdown_start_wall, "duration": COUNTDOWN_TIME}
        )

        QTimer.singleShot(COUNTDOWN_TIME * 1000, self.start_current_question)

    def start_next_question(self) -> bool:
        pass

    def start_current_question(self) -> None:
        pass

    def finish_current_question(self) -> None:
        pass

    def receive_answer(
        self, player_id: str, answer_index: int, timestamp: float
    ) -> None:
        pass

    def check_question_expired(self, current_time: float) -> bool:
        pass

    def skip_question(self) -> None:
        pass

    def can_start_next_question(self) -> bool:
        pass

    def get_current_question(self) -> Question | None:
        pass

    def get_time_remaining(self, current_time: float) -> float:
        pass

    def get_live_leaderboard(self) -> list[dict]:
        pass

    def get_final_leaderboard(self) -> list[dict]:
        pass

    def reset(self) -> None:
        pass
