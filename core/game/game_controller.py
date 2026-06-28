from PyQt6.QtCore import QObject, pyqtSignal

from core.game.quiz_manager import QuizManager
from models.player import Player
from models.leaderboard import Leaderboard
from models.quiz import Quiz
from models.question import Question


class GameController(QObject):
    def __init__(self) -> None:
        super().__init__()
        self.quiz_manager = QuizManager()

        self.game_running: bool = False
        self.question_running: bool = False

        self.current_question_index: int | None = None

        self.question_start_time: float | None = None
        self.question_deadline: float | None = None

    def load_quiz(self, quiz: Quiz) -> None:
        pass

    def start_game(self) -> None:
        pass

    def end_game(self) -> None:
        pass

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
