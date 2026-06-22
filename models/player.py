class Player:
    """Represents a player in the system (for the game manager)."""

    def __init__(self, player_id: str, nickname: str) -> None:
        """Initialize a new player instance."""
        self.player_id = player_id
        self.nickname = nickname

        self.score = 0
        self.connected = True

        self.current_answer: int | None = None
        self.has_answered = False

    def update_score(self, points: int) -> int:
        """Increment player points by a certain amount. Returns new score."""
        self.score += points
        return self.score

    def submit_answer(self, answer_index: int) -> None:
        """Submit answer index and change answer state."""
        self.current_answer = answer_index
        self.has_answered = True

    def reset_for_question(self) -> None:
        """Reset values for new question."""
        self.current_answer = None
        self.has_answered = False
