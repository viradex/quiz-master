import math

from models.player import Player
from models.leaderboard import Leaderboard
from models.quiz import Quiz
from models.question import Question
from models.payloads import (
    QuestionPayload,
    ClientResultsPayload,
    ClientFinalResultsPayload,
    ServerResultsPayload,
    ServerFinalResultsPayload,
)


class QuizManager:
    def __init__(self) -> None:
        self.quiz: Quiz | None = None
        self.players: dict[str, Player] = {}
        self.leaderboard = Leaderboard()

        self.all_time_taken: list[float] = []
        self.all_accuracies: list[float] = []

    def load_quiz(self, quiz: Quiz) -> None:
        """Load the quiz to run the game off of, and shuffle the questions if needed."""
        self.quiz = quiz

        if self.quiz.do_shuffle:
            self.quiz.shuffle_questions()

    def add_player(self, player: Player) -> None:
        """Add a player to the manager and leaderboard."""
        self.players[player.player_id] = player
        self.leaderboard.add_player(player)

    def remove_player(self, player_id: str) -> None:
        """Remove a player from the manager and leaderboard."""
        self.players.pop(player_id, None)
        self.leaderboard.remove_player(player_id)

    def get_question(self, index: int) -> Question:
        """Get a Question from an index (not question number, therefore zero-based).
        Raises an IndexError if the question does not exist."""
        return self.quiz.questions[index]

    def get_total_questions(self) -> int:
        """Gets the total questions in the quiz (not the highest question index)."""
        return len(self.quiz.questions)

    def prepare_for_question(self) -> None:
        """Preare for an upcoming question."""
        self.leaderboard.snapshot_points()

    def submit_answer(
        self,
        player_id: str,
        points: int,
        selected_answer: int,
        time_taken: float,
        is_correct: bool,
    ) -> None:
        """Submit an answer from the player. The data is assumed to have been pre-validated
        and is not automatically validated in this layer."""
        player = self.players[player_id]
        player.submit_answer(points, selected_answer, time_taken, is_correct)

        self.all_time_taken.append(time_taken)

    def finish_question(self) -> None:
        """End the current question, by forcing all remaining submissions and sorting the leaderboard."""
        self.force_remaining_submissions()
        self.leaderboard.sort_players()

        self.all_accuracies.append(self.calculate_global_question_accuracy())

    def force_remaining_submissions(self) -> None:
        """Force remaining submissions from all players who have not answered yet."""
        for player in self.players.values():
            if not player.submitted:
                player.submit_forced_answer()

    def all_players_answered(self) -> bool:
        """Returns whether all players have answered yet or not."""
        return all(player.submitted for player in self.players.values())

    def reset_for_question(self) -> None:
        """Reset all player's data for an upcoming question."""
        for player in self.players.values():
            player.reset_for_question()

    def is_answer_valid(self, question: Question, answer_index: int) -> bool:
        """Whether the answer index provided is within the valid answer range of the question provided."""
        if answer_index < 0 or answer_index > len(question.answer_options) - 1:
            return False

        return True

    def is_answer_correct(self, question: Question, answer_index: int) -> bool:
        """Whether the answer index provided is the correct answer for the question provided."""
        return answer_index == question.correct_answer_index

    def calculate_points(self, time_taken: float, max_time: float | int) -> int:
        """
        Calculate the number of points that the player earned based on the time taken compared to the
        maximum time of the question.

        The function used for calculating points is defined as a piecewise, when the condition `m > 0.5` is satisfied:

        > `P(t) = 1000`

        > where `0 <= t <= 0.5`

        and:

        > `P(t) = -(500 / (m - 0.5)) * (t - 0.5) + 1000`

        > where `0.5 < t <= m`

        Where:
        - `P(t)` is the number of points
        - `t` is the time taken in seconds (`time_taken`)
        - `m` is the maximum time for the question in seconds (`max_time`)

        The number of points returned is `0` if the time taken is not in the range `[0, m]`.

        The final number of points returned is floored.
        """
        # If max_time does not satisfy condition m > 0.5
        if max_time <= 0.5:
            raise ValueError("max_time must be greater than 0.5")

        # If time_taken is not in the range [0,m]
        if time_taken < 0 or time_taken > max_time:
            return 0

        if time_taken <= 0.5:
            # Full score window for very fast responses
            points = 1000
        elif time_taken > 0.5 and time_taken <= max_time:
            # Apply linear decay to reduce score at constant rate
            slope = -500 / (max_time - 0.5)
            points = slope * (time_taken - 0.5) + 1000

        # Remove decimal values by flooring
        return math.floor(points)

    def calculate_global_question_accuracy(self) -> float:
        """Calculate the average accuracy across all players for the question that last completed."""
        correctness = [player.is_correct for player in self.players.values()]

        # As True = 1 and False = 0, this counts all Trues
        corrects = sum(correctness)
        total = len(correctness)

        # Avoid ZeroDivisionError
        percentage = corrects / total if total > 0 else 0
        return percentage

    def calculate_answer_frequency(self, num_answers: int) -> list[int]:
        """Calculate the number of responses for each answer for the question that last completed."""
        answers_frequency = []
        selected_answers = [player.selected_answer for player in self.players.values()]

        for answer in range(num_answers):
            answers_frequency.append(selected_answers.count(answer))

        return answers_frequency

    def get_question_data(
        self, question: Question, question_num: int
    ) -> QuestionPayload:
        """Get question data from the question provided and return as a payload."""
        total_questions = self.get_total_questions()
        question_text = question.question_text
        answer_options = question.answer_options
        time_limit = question.time_limit

        return QuestionPayload(
            question_num=question_num,
            total_questions=total_questions,
            question_text=question_text,
            answer_options=answer_options,
            time_limit=time_limit,
        )

    def get_server_result_stats(
        self, question: Question, question_num: int
    ) -> ServerResultsPayload:
        """Get server result stats from the question provided and return as a payload."""
        total_questions = self.get_total_questions()

        accuracy = self.calculate_global_question_accuracy()
        answer_frequency = self.calculate_answer_frequency(len(question.answer_options))

        question_text = question.question_text
        answer_options = question.answer_options
        correct_answer = question.correct_answer_index

        if self.get_total_questions() != question_num:
            leaderboard = self.leaderboard.get_global_leaderboard(include_delta=True)
        else:
            leaderboard = None

        return ServerResultsPayload(
            question_num=question_num,
            total_questions=total_questions,
            accuracy=accuracy,
            answer_frequency=answer_frequency,
            question_text=question_text,
            answer_options=answer_options,
            correct_answer=correct_answer,
            leaderboard=leaderboard,
        )

    def get_server_final_result_stats(self) -> ServerFinalResultsPayload:
        """Get server final result stats and return as a payload."""
        winner = self.leaderboard.sorted_players[0].nickname
        highest_points = self.leaderboard.sorted_players[0].total_points

        fastest_answer = min(self.all_time_taken, default=None)
        average_accuracy = (
            sum(self.all_accuracies) / len(self.all_accuracies)
            if self.all_accuracies
            else 0.0
        )

        total_players = len(self.players)
        total_questions = self.get_total_questions()

        leaderboard = self.leaderboard.get_global_leaderboard()

        return ServerFinalResultsPayload(
            winner=winner,
            highest_points=highest_points,
            fastest_answer=fastest_answer,
            average_accuracy=average_accuracy,
            total_players=total_players,
            total_questions=total_questions,
            leaderboard=leaderboard,
        )

    def get_client_result_stats(
        self, player_id: str, question: Question, question_index: int
    ) -> ClientResultsPayload:
        """Get client result stats from the question provided and return as a payload."""
        player = self.players[player_id]
        nickname = player.nickname

        question_text = question.question_text
        answer_options = question.answer_options
        correct_answer = question.correct_answer_index

        selected_answer = player.selected_answer
        is_correct = player.is_correct

        time_taken = player.time_taken
        total_points = player.total_points
        gained_points = player.question_points

        if self.get_total_questions() - 1 != question_index:
            rank = self.leaderboard.get_player_rank(player_id)
        else:
            rank = None

        return ClientResultsPayload(
            question_text=question_text,
            answer_options=answer_options,
            correct_answer=correct_answer,
            selected_answer=selected_answer,
            is_correct=is_correct,
            time_taken=time_taken,
            total_points=total_points,
            gained_points=gained_points,
            rank=rank,
            nickname=nickname,
        )

    def get_client_final_result_stats(
        self, player_id: str
    ) -> ClientFinalResultsPayload:
        """Get client final result stats and return as a payload."""
        player = self.players[player_id]
        nickname = player.nickname

        rank = self.leaderboard.get_player_rank(player_id)
        total_points = player.total_points
        total_correct = player.total_correct
        total_questions = self.get_total_questions()
        accuracy = player.calculate_accuracy(self.get_total_questions())

        on_podium = self.leaderboard.is_on_podium(player_id)
        is_first = self.leaderboard.is_first(player_id)
        is_last = self.leaderboard.is_last(player_id)
        behind_nickname, points_behind = self.leaderboard.get_points_behind(player_id)

        adjacent = self.leaderboard.get_adjacent_players(player_id, radius=1)
        leaderboard = self.leaderboard.get_leaderboard(adjacent)

        return ClientFinalResultsPayload(
            rank=rank,
            total_points=total_points,
            total_correct=total_correct,
            total_questions=total_questions,
            accuracy=accuracy,
            on_podium=on_podium,
            is_first=is_first,
            is_last=is_last,
            behind_nickname=behind_nickname,
            points_behind=points_behind,
            nickname=nickname,
            leaderboard=leaderboard,
        )

    def generate_individual_result_stats(
        self, question: Question, question_index: int
    ) -> dict[str, ClientResultsPayload]:
        """Generates result stats for each player and categorize them by player ID."""
        individual_stats = {}

        for player_id in self.players.keys():
            stats = self.get_client_result_stats(player_id, question, question_index)
            individual_stats[player_id] = stats

        return individual_stats

    def generate_individual_final_result_stats(
        self,
    ) -> dict[str, ClientFinalResultsPayload]:
        """Generates final result stats for each player and categorize them by player ID."""
        individual_stats = {}

        for player_id in self.players.keys():
            stats = self.get_client_final_result_stats(player_id)
            individual_stats[player_id] = stats

        return individual_stats

    def reset(self) -> None:
        """Reset the quiz manager."""
        self.quiz = None
        self.players.clear()
        self.leaderboard.reset()

        self.all_time_taken.clear()
        self.all_accuracies.clear()
