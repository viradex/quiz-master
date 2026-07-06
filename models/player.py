from dataclasses import dataclass


@dataclass
class Player:
    """Represents a player in the system (for the quiz manager)."""

    player_id: str
    nickname: str

    total_points: int = 0
    total_correct: int = 0

    question_points: int = 0
    is_correct: bool = False
    selected_answer: int | None = None
    time_taken: float | None = None
    submitted: bool = False

    def update_total_score(self, points: int) -> None:
        """Updates the per-question points and total points."""
        self.question_points = points
        self.total_points += points

    def update_correctness(self, is_correct: bool) -> None:
        """Updates the per-question correctness and total correct."""
        self.is_correct = is_correct
        self.total_correct += is_correct

    def calculate_accuracy(self, total_questions: int) -> float:
        """Calculates the total accuracy so far as a percentage 0.0-1.0."""
        return self.total_correct / total_questions if total_questions > 0 else 0

    def submit_answer(
        self, points: int, selected_answer: int, time_taken: float, is_correct: bool
    ) -> None:
        """Submit an answer on behalf of this player, saving data related to it."""
        self.update_total_score(points)
        self.update_correctness(is_correct)

        self.selected_answer = selected_answer
        self.time_taken = time_taken
        self.submitted = True

    def submit_forced_answer(self) -> None:
        """Submit a forced answer on behalf of this player. For example, if they did not answer in time."""
        self.question_points = 0
        self.is_correct = False
        self.selected_answer = None
        self.time_taken = None
        self.submitted = True

    def reset_for_question(self) -> None:
        """Reset non-permanent data fields for the next question."""
        self.question_points = 0
        self.is_correct = False
        self.selected_answer = None
        self.time_taken = None
        self.submitted = False
