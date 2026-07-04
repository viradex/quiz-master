from dataclasses import dataclass


@dataclass
class Player:
    """Represents a player in the system (for the game manager)."""

    player_id: str
    nickname: str
    total_points: int = 0

    question_points: int = 0
    selected_answer: int | None = None
    is_correct: bool = False
    submitted: bool = False

    def update_total_score(self, points: int) -> None:
        self.question_points = points
        self.total_points += points

    def submit_answer(self, points: int, selected_answer: int, is_correct) -> None:
        self.update_total_score(points)
        self.selected_answer = selected_answer
        self.is_correct = is_correct
        self.submitted = True

    def submit_forced_answer(self) -> None:
        self.question_points = 0
        self.selected_answer = None
        self.is_correct = False
        self.submitted = True

    def reset_for_question(self) -> None:
        self.question_points = 0
        self.selected_answer = None
        self.is_correct = False
        self.submitted = False
