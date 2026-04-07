class GameState:
    """Class to manage the state of the quiz game."""

    def __init__(self):
        """Initialize the class to manage the state of the quiz game."""

        self.players: dict[str, int] = {}  # name -> score
        self.answers: dict[str, str] = {}  # name -> answer

        self.current_question: str = None

    def add_player(self, name: str) -> None:
        """Add player and set their score to 0."""
        self.players[name] = 0

    def submit_answer(self, name, answer) -> None:
        """Submit the player's answer, if they haven't already."""
        if name not in self.answers:
            self.answers[name] = answer

    def all_answered(self, eligible_players: list[str]) -> bool:
        """True if all eligible players (players who are playing the quiz) have answered."""
        return len(self.answers) >= len(eligible_players)

    def clear_answers(self) -> None:
        """Remove all answers."""
        self.answers.clear()

    def calculate_scores(self) -> None:
        """Add a point to the user if they correctly answered."""
        correct = self.current_question["answer_index"]

        for player, answer in self.answers.items():
            if answer == correct:
                self.players[player] += 1
