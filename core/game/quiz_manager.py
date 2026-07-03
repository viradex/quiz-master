import math

from models.player import Player
from models.leaderboard import Leaderboard
from models.quiz import Quiz
from models.question import Question


class QuizManager:
    def __init__(self) -> None:
        self.quiz: Quiz | None = None
        self.players: dict[str, Player] = {}
        self.leaderboard = Leaderboard()

    def load_quiz(self, quiz: Quiz) -> None:
        self.quiz = quiz

    def add_player(self, player: Player) -> None:
        self.players[player.player_id] = player

    def remove_player(self, player_id: str) -> None:
        self.players.pop(player_id, None)

    def get_question(self, index: int) -> Question:
        # Raises IndexError if question does not exist
        return self.quiz.questions[index]

    def get_total_questions(self) -> int:
        return len(self.quiz.questions)

    def submit_answer(
        self, player_id: str, points: int, selected_answer: int, is_correct: bool
    ) -> None:
        player = self.players[player_id]
        player.submit_answer(points, selected_answer, is_correct)

    def reset_for_question(self) -> None:
        for player in self.players.values():
            player.reset_for_question()

    def is_answer_valid(self, question: Question, answer_index: int) -> bool:
        if answer_index < 0 or answer_index > len(question.answer_options) - 1:
            return False

        return True

    def is_answer_correct(self, question: Question, answer_index: int) -> bool:
        return answer_index == question.correct_answer_index

    def calculate_score(self, time_taken: float, max_time: float | int) -> int:
        if max_time <= 0.5:
            raise ValueError("max_time must be greater than 0.5")

        if time_taken < 0 or time_taken > max_time:
            return 0

        if time_taken <= 0.5:
            score = 1000
        elif time_taken > 0.5 and time_taken <= max_time:
            slope = -500 / (max_time - 0.5)
            score = slope * (time_taken - 0.5) + 1000

        return math.floor(score)

    def update_player_score(self, player_id: str, points: int) -> None:
        pass

    def generate_leaderboard(self, delta: bool = False) -> list[dict]:
        pass

    def lock_answers(self) -> None:
        pass

    def unlock_answers(self) -> None:
        pass

    def all_players_answered(self) -> bool:
        pass

    def apply_scores(self) -> None:
        pass
