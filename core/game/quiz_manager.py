from models.player import Player
from models.leaderboard import Leaderboard
from models.quiz import Quiz
from models.question import Question


class QuizManager:
    def __init__(self) -> None:
        self.quiz: Quiz | None = None
        self.players: dict[str, Player] = {}
        self.leaderboard = Leaderboard()

        self.question_time_limit: int | None = None
        self.answers_locked: bool = True

        # player_id -> (answer_index, timestamp)
        self.submissions: dict[str, tuple[int, float]] = {}

    def load_quiz(self, quiz: Quiz) -> None:
        self.quiz = quiz

    def add_player(self, player: Player) -> None:
        self.players[player.player_id] = player

    def remove_player(self, player_id: str) -> None:
        self.players.pop(player_id, None)

    def get_current_question(self) -> Question | None:
        pass

    def submit_answer(
        self, player_id: str, answer_index: int, timestamp: float
    ) -> None:
        pass

    def validate_answer(self, answer_index: int) -> bool:
        pass

    def calculate_score(self, timestamp: float) -> int:
        pass

    def update_player_score(self, player_id: str, points: int) -> None:
        pass

    def generate_leaderboard(self, delta: bool = False) -> list[dict]:
        pass

    def lock_answers(self) -> None:
        pass

    def unlock_answers(self) -> None:
        pass

    def _reset_submissions(self) -> None:
        pass

    def _all_players_answered(self) -> bool:
        pass

    def _apply_scores(self) -> None:
        pass
