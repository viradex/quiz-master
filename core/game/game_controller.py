import time
from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from core.app.enums import AnswerValidationResult
from core.game.quiz_manager import QuizManager
from models.player import Player
from models.quiz import Quiz
from models.question import Question

from core.config.constants import MIN_PLAYERS_FOR_GAME, COUNTDOWN_TIME


class GameController(QObject):
    """Handles the flow and orchestration of the quiz game."""

    started_countdown = pyqtSignal(int)
    started_question = pyqtSignal(object)

    question_results_ready = pyqtSignal(object, dict)
    final_results_ready = pyqtSignal(object, dict)

    no_players_found = pyqtSignal()

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
        """Load the quiz to run the game off of."""
        self.quiz_manager.load_quiz(quiz)

    def add_player(self, player: Player) -> None:
        """Add a player to the game."""
        self.quiz_manager.add_player(player)

    def remove_player(self, player_id: str) -> None:
        """
        Remote a player from the game, and perform checks to ensure the game remains
        flowing or ends prematurely depending on the players remaining and their state.
        When a player is removed from the game, they are permantly removed from records and
        the leaderboard.
        """
        self.quiz_manager.remove_player(player_id)

        # If the number of players remaining is less than the minimum players
        # that was needed for the game to start, prematurely end the game
        if len(self.quiz_manager.players) < MIN_PLAYERS_FOR_GAME and self.game_running:
            self.reset()
            self.no_players_found.emit()
            return

        # If the player that left was the only one who hadn't answered, progress the quiz
        if self.question_running and self.quiz_manager.all_players_answered():
            self.question_timer.stop()
            self.finish_current_question()

    def start_game(self) -> None:
        """Start the quiz game."""
        if self.game_running:
            raise RuntimeError("Cannot start game when already running")

        self.game_running = True
        self.start_next_question()

    def start_next_question(self) -> None:
        """Start the next question, by incrementing the current question counter and starting the countdown.
        If the current question is the same as the total questions, the game ends."""
        self.current_question_index += 1
        self.quiz_manager.reset_for_question()

        if self.quiz_manager.get_total_questions() == self.current_question_index:
            self.finish_quiz()
        else:
            self.countdown_start()

    def countdown_start(self) -> None:
        """Start question countdown."""
        self.started_countdown.emit(COUNTDOWN_TIME)
        self.countdown_timer.start(COUNTDOWN_TIME * 1000)

    def start_current_question(self) -> None:
        """Start running the current question as defined in `current_question_index`.
        Sends question data to clients and runs the question timer."""
        # Prevents certain race conditions with timers going off when the game is ended prematurely
        if not self.game_running:
            return

        self.quiz_manager.prepare_for_question()

        # Set current question and find question timer details
        self.current_question = self.quiz_manager.get_question(
            self.current_question_index
        )
        self.question_running = True
        self.question_start_time = time.monotonic()
        self.question_deadline = (
            self.question_start_time + self.current_question.time_limit
        )

        # Get question payload
        question_data = self.quiz_manager.get_question_data(
            self.current_question, self.current_question_index + 1
        )

        # Start question timer and send question payload
        self.question_timer.start(self.current_question.time_limit * 1000)
        self.started_question.emit(question_data)

    def finish_current_question(self) -> None:
        """Finishes the current question. Sends results data to the server and clients."""
        # Prevents certain race conditions with timers going off when the game is ended prematurely
        if not self.game_running:
            return

        self.question_running = False
        self.quiz_manager.finish_question()

        # Get server and client payloads
        server_data = self.quiz_manager.get_server_result_stats(
            self.current_question, self.current_question_index + 1
        )
        clients_data = self.quiz_manager.generate_individual_result_stats(
            self.current_question, self.current_question_index
        )

        # Send server and client payloads
        self.question_results_ready.emit(server_data, clients_data)

    def skip_question(self) -> None:
        """Skip and end current question prematurely."""
        self.question_timer.stop()
        self.finish_current_question()

    def receive_answer(
        self, player_id: str, answer_index: int, timestamp: float
    ) -> None:
        """Receive and handle a player's answer."""
        is_correct = self.quiz_manager.is_answer_correct(
            self.current_question, answer_index
        )

        # Get the difference between the time submitted and the start time
        time_taken = timestamp - self.question_start_time

        if is_correct:
            points = self.quiz_manager.calculate_points(
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

    def is_answer_legal(
        self, answer_index: int, timestamp: float
    ) -> AnswerValidationResult:
        """Checks if a client's answer was legal within the game. Does not check answer correctness."""
        is_time_valid = self.question_start_time <= timestamp <= self.question_deadline
        is_answer_valid = self.quiz_manager.is_answer_valid(
            self.current_question, answer_index
        )

        if not is_time_valid:
            return AnswerValidationResult.TIME
        elif not is_answer_valid:
            return AnswerValidationResult.ANSWER

        return AnswerValidationResult.OK

    def finish_quiz(self) -> None:
        """Finishes the quiz. Sends final results data to the server and clients."""
        # Get server and client payloads
        server_data = self.quiz_manager.get_server_final_result_stats()
        clients_data = self.quiz_manager.generate_individual_final_result_stats()

        # Reset game, then send payloads
        self.reset()
        self.final_results_ready.emit(server_data, clients_data)

    def reset(self) -> None:
        """Reset the game controller and quiz manager completely."""
        self.quiz_manager.reset()

        self.countdown_timer.stop()
        self.question_timer.stop()

        self.game_running = False
        self.question_running = False

        self.current_question_index = -1
        self.current_question = None
        self.question_start_time = None
        self.question_deadline = None
