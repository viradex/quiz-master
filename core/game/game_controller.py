import time
from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from core.game.quiz_manager import QuizManager
from models.player import Player
from models.quiz import Quiz
from models.question import Question
from core.config.constants import COUNTDOWN_TIME


class GameController(QObject):
    start_countdown = pyqtSignal(dict)
    start_question = pyqtSignal(dict)

    question_results = pyqtSignal(dict, dict)
    final_results = pyqtSignal(dict, dict)

    def __init__(self) -> None:
        super().__init__()
        self.quiz_manager = QuizManager()

        self.game_running: bool = False
        self.question_running: bool = False

        self.current_question_index: int = -1
        self.current_question: Question | None = None
        self.question_start_time: float | None = None
        self.question_deadline: float | None = None

        self.setup_question_timer()

    def setup_question_timer(self) -> None:
        self.question_timer = QTimer(self)
        self.question_timer.setSingleShot(True)
        self.question_timer.timeout.connect(self.finish_current_question)

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
        self.quiz_manager.reset_for_question()

        if self.quiz_manager.get_total_questions() == self.current_question_index:
            self.finish_quiz()
        else:
            self.countdown_start()

    def countdown_start(self) -> None:
        self.start_countdown.emit({"duration": COUNTDOWN_TIME})

        QTimer.singleShot(COUNTDOWN_TIME * 1000, self.start_current_question)

    def start_current_question(self) -> None:
        self.quiz_manager.prepare_for_question()

        self.current_question = self.quiz_manager.get_question(
            self.current_question_index
        )
        self.question_running = True
        self.question_start_time = time.monotonic()
        self.question_deadline = (
            self.question_start_time + self.current_question.time_limit
        )

        self.question_timer.start(self.current_question.time_limit * 1000)

        self.start_question.emit(
            {
                "question_num": self.current_question_index + 1,
                "total_questions": self.quiz_manager.get_total_questions(),
                "question_text": self.current_question.question_text,
                "answer_options": self.current_question.answer_options,
                "time_limit": self.current_question.time_limit,
            }
        )

    def finish_current_question(self) -> None:
        self.question_running = False
        self.quiz_manager.finish_question()

        global_leaderboard = self.quiz_manager.generate_global_leaderboard(
            include_delta=True
        )
        global_stats = self.quiz_manager.get_live_global_stats(
            self.current_question, self.current_question_index + 1
        )

        global_data = {**global_stats, "leaderboard": global_leaderboard}
        individual_data = self.quiz_manager.generate_individual_live_stats(
            self.current_question
        )

        self.question_results.emit(global_data, individual_data)

    def skip_question(self) -> None:
        self.question_timer.stop()
        self.finish_current_question()

    def receive_answer(
        self, player_id: str, answer_index: int, timestamp: float
    ) -> None:
        is_correct = self.quiz_manager.is_answer_correct(
            self.current_question, answer_index
        )
        time_taken = timestamp - self.question_start_time

        if is_correct:
            points = self.quiz_manager.calculate_score(
                time_taken, self.current_question.time_limit
            )
        else:
            points = 0

        self.quiz_manager.submit_answer(
            player_id, points, answer_index, time_taken, is_correct
        )

        if self.quiz_manager.all_players_answered():
            self.question_timer.stop()
            self.finish_current_question()

    def is_answer_valid(self, answer_index: int, timestamp: float) -> tuple[bool, str]:
        is_time_valid = self.question_start_time <= timestamp <= self.question_deadline
        is_answer_valid = self.quiz_manager.is_answer_valid(
            self.current_question, answer_index
        )

        if not is_time_valid:
            return (False, "time")
        elif not is_answer_valid:
            return (False, "answer")
        else:
            return (True, "")

    def finish_quiz(self) -> None:
        self.quiz_manager.force_remaining_submissions()

        global_leaderboard = self.quiz_manager.generate_global_leaderboard(
            include_delta=False
        )
        global_stats = self.quiz_manager.get_final_global_stats()

        individual_leaderboards = self.quiz_manager.generate_individual_leaderboards(
            include_delta=False
        )
        individual_stats = self.quiz_manager.generate_individual_final_stats()

        global_data = {**global_stats, "leaderboard": global_leaderboard}
        individual_data = {
            player_id: {
                **stats,
                "leaderboard": individual_leaderboards[player_id],
            }
            for player_id, stats in individual_stats.items()
        }

        self.final_results.emit(global_data, individual_data)
        self.reset()

    def reset(self) -> None:
        self.quiz_manager.reset()

        self.game_running = False
        self.question_running = False

        self.current_question_index = -1
        self.current_question = None
        self.question_start_time = None
        self.question_deadline = None
