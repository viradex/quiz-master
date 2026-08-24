"""
game_controller.py

Contains the central coordinator for the quiz game, and is a mediator between the quiz manager and
logic. Does not contain game logic.
"""

import time

from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from core.app.enums import AnswerValidationResult
from core.config.constants import COUNTDOWN_TIME, MIN_PLAYERS_FOR_GAME
from core.game.quiz_manager import QuizManager
from models.payloads import (
    QuestionPayload,
    ServerFinalResultsPayload,
    ServerResultsPayload,
)
from models.player import Player
from models.question import Question
from models.quiz import Quiz


class GameController(QObject):
    """
    Manages the game controller, which acts as the central game manager and coordinator, for things
    such as timers. Does not contain game logic; that is stored in QuizManager. Inherits `QObject`
    to allow support for `pyqtSignal`.

    Attributes:
        started_countdown: A `pyqtSignal` that emits when the countdown begins. Provides an integer
            as an argument that describes the duration of the countdown. An integer is used as the
            countdown is always a whole number.

        started_question: A `pyqtSignal` that emits when the question begins. Provides a QuestionPayload
            that contains data relating to the question, that is required for the client and server
            screens to correctly display the question. A specialized data transfer object is used as
            it allows easier access to properties and the structure of the payload without using
            dictionaries.

        question_results_ready: A `pyqtSignal` that emits when the question ends and the results for
            the question have been calculated. Provides both a single ServerResultsPayload and multiple
            ClientResultsPayloads in a dictionary identified by the player ID, as arguments. Both are
            specialized data transfer objects as it allows easier access to properties and the structure
            of the payload without using dictionaries. A dictionary is used for the client payload as
            the player ID allows sending the specialized data to each individual player.

        final_results_ready: A `pyqtSignal` that emits when the final results have been calculated.
            Provides both a single ServerFinalResultsPayload and multiple ClientFinalResultsPayloads in
            a dictionary identified by the player ID, as arguments. Both are specialized data transfer
            objects as it allows easier access to properties and the structure of the payload without
            using dictionaries. A dictionary is used for the client payload as the player ID allows
            sending the specialized data to each individual player.

        no_players_found: A `pyqtSignal` that emits when the number of players dips below the number
            of players required to start the game in the first place, or if all the players leave the
            game. No arguments are provided.
    """

    started_countdown = pyqtSignal(int)
    started_question = pyqtSignal(QuestionPayload)

    # Dictionary contains multiple ClientResultsPayload
    question_results_ready = pyqtSignal(ServerResultsPayload, dict)
    # Dictionary contains multiple ClientFinalResultsPayload
    final_results_ready = pyqtSignal(ServerFinalResultsPayload, dict)

    no_players_found = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()

        # Quiz manager to manage game rules
        self.quiz_manager = QuizManager()

        # Global game state
        self.game_running: bool = False
        self.question_running: bool = False

        # Question state
        # Zero-based index. Starts at -1 so the first increment sets the index to 0; the first question.
        self.current_question_index: int = -1
        self.current_question: Question | None = None
        self.question_start_time: float | None = None
        self.question_deadline: float | None = None

        self._setup_timers()

    def _setup_timers(self) -> None:
        """
        Internal method. Sets up the needed amount of `QTimer` needed to run the countdown timer as
        well as the question countdown timer.

        Returns:
            None.
        """
        # Both timers are single-shot to prevent them from restarting when the
        # timer is over. To restart the timer, run start() on the respective timer again.
        self.countdown_timer = QTimer(self)
        self.countdown_timer.setSingleShot(True)
        self.countdown_timer.timeout.connect(self._start_current_question)

        self.question_timer = QTimer(self)
        self.question_timer.setSingleShot(True)
        self.question_timer.timeout.connect(self._finish_current_question)

    def load_quiz(self, quiz: Quiz) -> None:
        """
        Loads and uses the Quiz provided to run the quiz game off of.

        Arguments:
            quiz: The Quiz to run the game off of. A Quiz object is used as it contains the required
                metadata used for running the game.

        Returns:
            None.
        """
        self.quiz_manager.load_quiz(quiz)

    def add_player(self, player: Player) -> None:
        """
        Adds a player to the quiz game, if the game has not already started. If the game has already started,
        the player is not added.

        Arguments:
            player: The Player to add to the quiz manager and game. A Player object is used as it allows using
                its helper properties and methods for storing per-player data relating to the game.

        Returns:
            None.
        """
        if self.game_running:
            return

        self.quiz_manager.add_player(player)

    def remove_player(self, player_id: str) -> None:
        """
        Removes a player from the game. Performs checks after removing the player to ensure the number of
        players is not below the number of players that was required for the game to start. If it is, the
        game is quit prematurely and a signal is sent. If the player that left was the only player who hadn't
        answered, the game progresses as normal.

        When a player is removed from the game, they are permanently removed from records and the leaderboard.

        Arguments:
            player_id: A string describing the ID of the Player instance to remove. A string is used as it
                can flexibly store IDs and can store many characters to make them more unique.

        Returns:
            None.
        """
        self.quiz_manager.remove_player(player_id)

        # If the number of players remaining is less than the minimum players
        # that was needed for the game to start, prematurely end the game.
        if self.game_running and len(self.quiz_manager.players) < MIN_PLAYERS_FOR_GAME:
            self.reset()
            self.no_players_found.emit()
            return

        # If the player that left was the only one who hadn't answered, progress the quiz
        if self.question_running and self.quiz_manager.all_players_answered():
            self.question_timer.stop()
            self._finish_current_question()

    def start_game(self) -> None:
        """
        Begins the quiz game. The quiz must be set via `load_quiz()` before running this method.

        Returns:
            None.

        Raises:
            RuntimeError: If the game is requested to be started while already running.

            ValueError: If the quiz has not been set.
        """
        if self.game_running:
            raise RuntimeError("Cannot start a game while it is already running")

        if self.quiz_manager.quiz is None:
            raise ValueError("Cannot start a game without a loaded quiz")

        self.game_running = True

        self.quiz_manager.prepare_for_game()
        self.start_next_question()

    def start_next_question(self) -> None:
        """
        Begins the next question, by incrementing the current question index and starting the countdown if the
        question is not the final question. After incrementing the question index, if it exceeds the number of
        questions, it finishes the quiz due to running out of questions (a normal finish).

        Returns:
            None.
        """
        # As the current question index starts from -1 rather than None, incrementing
        # by 1 on the first question will simply set it to 0, being the correct
        # index of the first question.
        self.current_question_index += 1
        self.quiz_manager.reset_for_question()

        # If the current question index exceeds the number of questions, finish,
        # otherwise, start the question countdown like normal.
        if self.quiz_manager.get_total_questions() == self.current_question_index:
            self.finish_quiz()
        else:
            self._start_countdown()

    def _start_countdown(self) -> None:
        """
        Internal method. Starts the countdown timer before displaying a question. This does not run the question
        countdown timer. Upon the timer ending, the question is started.

        Returns:
            None.
        """
        self.started_countdown.emit(COUNTDOWN_TIME)
        self.countdown_timer.start(COUNTDOWN_TIME * 1000)

    def _start_current_question(self) -> None:
        """
        Internal method. Begins the current question, as defined in `current_question_index`. This method
        does not increment the current question index, as this is expected to have been done before running
        this method to progress the quiz.

        This method calculates the time for the question, starts the question timer, and sends question data
        to the clients and server for UI display.

        Returns:
            None.
        """
        # Prevents certain race conditions with timers going off when the game is ended prematurely
        if not self.game_running:
            return

        # Any pre-question checks or processes
        self.quiz_manager.prepare_for_question()

        # Get the current Question object to retrieve data from
        self.question_running = True
        self.current_question = self.quiz_manager.get_question(
            self.current_question_index
        )

        # Get the start time and calculate deadline to ensure clients do not answer after that
        self.question_start_time = time.monotonic()
        self.question_deadline = (
            self.question_start_time + self.current_question.time_limit
        )

        # Get question payload
        question_data = self.quiz_manager.get_question_data(
            self.current_question, self.current_question_index + 1
        )

        # Start question timer and send data to server and clients
        self.question_timer.start(self.current_question.time_limit * 1000)
        self.started_question.emit(question_data)

    def _finish_current_question(self) -> None:
        """
        Internal method. Finishes the current question. This method concludes the question internally and
        sends the question results payloads to both client and server. If the current question is not set,
        this method does nothing.

        Returns:
            None.
        """
        # Prevents certain race conditions with timers going off when the game is ended prematurely
        if not self.game_running:
            return

        if self.current_question is None:
            return

        self.question_running = False
        self.quiz_manager.finish_question()

        server_data = self.quiz_manager.get_server_result_stats(
            self.current_question, self.current_question_index + 1
        )
        clients_data = self.quiz_manager.generate_clients_result_stats(
            self.current_question, self.current_question_index + 1
        )

        self.question_results_ready.emit(server_data, clients_data)
        self.current_question = None

    def skip_question(self) -> None:
        """
        End the current question prematurely. This should only be run when a question is currently running.

        Returns:
            None.
        """
        self.question_timer.stop()
        self._finish_current_question()

    def receive_answer(
        self, player_id: str, answer_index: int, timestamp: float
    ) -> None:
        """
        Submits the answer provided to the respective player based on their player ID. Calculates the points
        that the player earned based on the answer index chosen and the timestamp entered. If all players have
        answered after submitting this answer, the current question is finished.

        While this method checks the answer's legality before submitting, if the checks fail, the method will
        raise a `RuntimeError`. To avoid this, run `is_answer_legal()` before this method.

        Arguments:
            player_id: The player ID of the player to submit this answer on behalf of. A string is used as it
                can flexibly store IDs and can store many characters to make them more unique.

            answer_index: The index of the answer selected, as a zero-based index respective to the answer the
                player selected, ranging from 0 to the number of valid answers, minus 1. For example, for a
                question with 4 answers, the valid range is 0-3.

            timestamp: A float derived from `time.monotonic()` at the time the answer was submitted. The time
                should be calculated from the server, not the client, to avoid false times reported by the
                client, and also since monotonic time is not the same on different devices. A monotonic time
                is used to avoid the time being changed by DST or NTP and causing issues.

        Returns:
            None.

        Raises:
            RuntimeError: If the answer provided is not legal.
        """
        if self.current_question is None or self.question_start_time is None:
            return

        # Ensure answer is legal before submitting. This should have been run
        # beforehand, so instead of returning the result it will raise an exception.
        answer_legality = self.is_answer_legal(answer_index, timestamp)

        if answer_legality is not AnswerValidationResult.OK:
            raise RuntimeError(f"The answer provided is not legal: {answer_legality}")

        is_correct = self.quiz_manager.is_answer_correct(
            self.current_question, answer_index
        )

        # Get the difference between the time submitted and the start time
        time_taken = timestamp - self.question_start_time

        # Only give points if answer is correct
        if is_correct:
            points = self.quiz_manager.calculate_points(
                time_taken, self.current_question.time_limit
            )
        else:
            points = 0

        self.quiz_manager.submit_answer(
            player_id, points, answer_index, time_taken, is_correct
        )

        # If all players have answered now, finish the question
        if self.quiz_manager.all_players_answered():
            self.question_timer.stop()
            self._finish_current_question()

    def is_answer_legal(
        self, answer_index: int, timestamp: float
    ) -> AnswerValidationResult:
        """
        Ensures the answer index and timestamp provided is legal for answering a question with. This method
        does not check answer correctness. This method should only be run when the question is running.

        The validation done includes:
        - Whether the answer index is within the valid range of answers in the question.
        - Whether the timestamp is within the valid range of the start time to the end time.

        Arguments:
            answer_index: The index of the answer selected, as a zero-based index. An integer is used as it
                represents an index of an iterable easily.

            timestamp: A float derived from `time.monotonic()` at the time the answer was submitted, which
                should be run on the server-side.

        Returns:
            The AnswerValidationResult, which details the issue the answer has, or `OK` if there are no
            issues.
        """
        if (
            self.current_question is None
            or self.question_start_time is None
            or self.question_deadline is None
        ):
            return AnswerValidationResult.TIME

        if not self.quiz_manager.is_answer_valid(self.current_question, answer_index):
            return AnswerValidationResult.ANSWER

        if not (self.question_start_time <= timestamp <= self.question_deadline):
            return AnswerValidationResult.TIME

        return AnswerValidationResult.OK

    def finish_quiz(self) -> None:
        """
        Ends the quiz game, by calculating and sending the final results data to the server and clients. All
        data is reset to prepare for any future game, if needed.

        Returns:
            None.
        """
        # Avoid race conditions
        if not self.game_running:
            return

        server_data = self.quiz_manager.get_server_final_result_stats()
        clients_data = self.quiz_manager.generate_clients_final_result_stats(
            self.current_question_index + 1
        )

        # Reset quiz manager and game controller to prepare for any future game
        self.reset()
        self.final_results_ready.emit(server_data, clients_data)

    def reset(self) -> None:
        """
        Resets the game controller and quiz manager attributes to their original initial values, to prepare
        for any future game and ensure no data from the current game remains in the next game. All timers
        are also stopped immediately.

        Returns:
            None.
        """
        self.quiz_manager.reset()

        self.countdown_timer.stop()
        self.question_timer.stop()

        self.game_running = False
        self.question_running = False

        self.current_question_index = -1
        self.current_question = None
        self.question_start_time = None
        self.question_deadline = None
