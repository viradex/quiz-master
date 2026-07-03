from dataclasses import dataclass


@dataclass
class Player:
    """Represents a player in the system (for the game manager)."""

    player_id: str
    nickname: str
    total_points: int = 0

    delta_points: int = 0
    selected_answer: int | None = None
    is_correct: bool = False

    def update_total_score(self, points: int) -> None:
        self.delta_points = points
        self.total_points += points

    def submit_answer(self, points: int, selected_answer: int, is_correct) -> None:
        self.update_total_score(points)
        self.selected_answer = selected_answer
        self.is_correct = is_correct

    def reset_for_question(self) -> None:
        self.delta_points = 0
        self.selected_answer = None
        self.is_correct = False
