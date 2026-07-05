import time
from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from core.game.quiz_manager import QuizManager
from models.player import Player
from models.quiz import Quiz
from models.question import Question
from core.config.constants import MIN_PLAYERS_FOR_START, COUNTDOWN_TIME


class GameController(QObject):
    start_countdown = pyqtSignal(int)
    start_question = pyqtSignal(object)

    question_results = pyqtSignal(object, dict)
    final_results = pyqtSignal(object, dict)

    no_players = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.quiz_manager = QuizManager()

        self.game_running: bool = False
        self.question_running: bool = False

        self.current_question_index: int = -1
        self.current_question: Question | None = None
        self.question_start_time: float | None = None
        self.question_deadline: float | None = None

        self.setup_timers()

    def setup_timers(self) -> None:
        self.countdown_timer = QTimer(self)
        self.countdown_timer.setSingleShot(True)
        self.countdown_timer.timeout.connect(self.start_current_question)

        self.question_timer = QTimer(self)
        self.question_timer.setSingleShot(True)
        self.question_timer.timeout.connect(self.finish_current_question)

    def load_quiz(self, quiz: Quiz) -> None:
        self.quiz_manager.load_quiz(quiz)

    def add_player(self, player: Player) -> None:
        self.quiz_manager.add_player(player)

    def remove_player(self, player_id: str) -> None:
        self.quiz_manager.remove_player(player_id)

        if len(self.quiz_manager.players) < MIN_PLAYERS_FOR_START and self.game_running:
            self.reset()
            self.no_players.emit()
            return

        if self.question_running and self.quiz_manager.all_players_answered():
            self.question_timer.stop()
            self.finish_current_question()

    def start_game(self) -> None:
        self.game_running = True
        self.start_next_question()

    def start_next_question(self) -> None:
        self.current_question_index += 1
        self.quiz_manager.reset_for_question()

        if self.quiz_manager.get_total_questions() == self.current_question_index:
            self.finish_quiz()
        else:
            self.countdown_start()

    def countdown_start(self) -> None:
        self.start_countdown.emit(COUNTDOWN_TIME)
        self.countdown_timer.start(COUNTDOWN_TIME * 1000)

    def start_current_question(self) -> None:
        if not self.game_running:
            return

        self.quiz_manager.prepare_for_question()

        self.current_question = self.quiz_manager.get_question(
            self.current_question_index
        )
        self.question_running = True
        self.question_start_time = time.monotonic()
        self.question_deadline = (
            self.question_start_time + self.current_question.time_limit
        )

        question_data = self.quiz_manager.get_question_data(
            self.current_question, self.current_question_index + 1
        )

        self.question_timer.start(self.current_question.time_limit * 1000)
        self.start_question.emit(question_data)

    def finish_current_question(self) -> None:
        if not self.game_running:
            return

        self.question_running = False
        self.quiz_manager.finish_question()

        global_data = self.quiz_manager.get_live_global_stats(
            self.current_question, self.current_question_index + 1
        )
        individual_data = self.quiz_manager.generate_individual_live_stats(
            self.current_question, self.current_question_index
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
        global_data = self.quiz_manager.get_final_global_stats()
        individual_data = self.quiz_manager.generate_individual_final_stats()

        self.reset()
        self.final_results.emit(global_data, individual_data)

    def reset(self) -> None:
        self.quiz_manager.reset()

        self.countdown_timer.stop()
        self.question_timer.stop()

        self.game_running = False
        self.question_running = False

        self.current_question_index = -1
        self.current_question = None
        self.question_start_time = None
        self.question_deadline = None
