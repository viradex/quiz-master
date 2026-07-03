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

    start_question = pyqtSignal(dict)

    def __init__(self) -> None:
        super().__init__()
        self.quiz_manager = QuizManager()

        self.game_running: bool = False
        self.question_running: bool = False

        self.current_question_index: int = -1
        self.current_question: Question | None = None
        self.question_start_time: float | None = None
        self.question_deadline: float | None = None

    def load_quiz(self, quiz: Quiz) -> None:
        self.quiz_manager.load_quiz(quiz)

    def add_player(self, player: Player) -> None:
        self.quiz_manager.add_player(player)

    def remove_player(self, player_id: str) -> None:
        self.quiz_manager.remove_player(player_id)

    def start_game(self) -> None:
        self.game_running = True
        self.start_next_question()

    def end_game(self) -> None:
        pass

    def start_next_question(self) -> None:
        self.current_question_index += 1
        self.countdown_start()

    def countdown_start(self) -> None:
        now = time.time()
        self.start_countdown.emit({"start_time": now, "duration": COUNTDOWN_TIME})

        QTimer.singleShot(COUNTDOWN_TIME * 1000, self.start_current_question)

    def start_current_question(self) -> None:
        self.question = self.quiz_manager.get_question(self.current_question_index)
        self.question_running = True
        self.question_start_time = time.monotonic()
        self.question_deadline = self.question_start_time + self.question.time_limit

        QTimer.singleShot(self.question.time_limit * 1000, self.finish_current_question)

        self.start_question.emit(
            {
                "question_num": self.current_question_index + 1,
                "total_questions": self.quiz_manager.get_total_questions(),
                "question_text": self.question.question_text,
                "answer_options": self.question.answer_options,
                "time_limit": self.question.time_limit,
            }
        )

    def finish_current_question(self) -> None:
        self.question_running = False

        print("Question finished whether you like it or not >:)")

    def receive_answer(
        self, player_id: str, answer_index: int, timestamp: float
    ) -> None:
        is_valid, reason = self.is_answer_valid(answer_index, timestamp)
        if not is_valid:
            self.invalid_answer.emit(player_id, reason)
            return

        is_correct = self.quiz_manager.is_answer_correct(self.question, answer_index)

        if is_correct:
            time_taken = timestamp - self.question_start_time
            points = self.quiz_manager.calculate_score(
                time_taken, self.question.time_limit
            )
        else:
            points = 0

        print(f"{player_id=} {points=} {answer_index=} {is_correct=}")  # temp debug
        self.quiz_manager.submit_answer(player_id, points, answer_index, is_correct)

    def is_answer_valid(self, answer_index: int, timestamp: float) -> tuple[bool, str]:
        is_time_valid = self.question_start_time <= timestamp <= self.question_deadline
        is_answer_valid = self.quiz_manager.is_answer_valid(self.question, answer_index)

        if not is_time_valid:
            return (False, "time")
        elif not is_answer_valid:
            return (False, "answer")
        else:
            return (True, "")

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
