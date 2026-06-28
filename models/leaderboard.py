from models.player import Player


class Leaderboard:
    """Represents the game leaderboard."""

    def __init__(self) -> None:
        self.players: dict[str, Player] = {}
        self.sorted_players: list[Player] = []
        self.previous_scores: dict[str, int] = {}

    def add_player(self, player: Player) -> None:
        """Add a player to the leaderboard."""
        self.players[player.player_id] = player

    def remove_player(self, player_id: str) -> bool:
        """Remove a player from the leaderboard. Returns a boolean value indicating if the player ID existed or not."""
        player = self.players.pop(player_id, None)
        self.previous_scores.pop(player_id, None)

        self.sorted_players = [
            p for p in self.sorted_players if p.player_id != player_id
        ]

        return player is not None

    def update_scores(self, player_scores: dict[str, int]) -> None:
        """Updates scores of all players specified."""
        for player_id, score in player_scores.items():
            self.players[player_id].score = score

    def snapshot_scores(self) -> None:
        """
        Saves all current scores saved in the leaderboard to `previous_scores`.
        This should be run before updating scores for the next question. Should be
        set before running `get_score_changes()` to accurately calculate the delta.

        Example:

            snapshot_scores()  # Snapshot old scores first
            update_scores()  # Then update with new scores
        """
        for player_id, player in self.players.items():
            self.previous_scores[player_id] = player.score

    def reset(self) -> None:
        """Clears all players from the leaderboard."""
        self.players.clear()
        self.sorted_players.clear()
        self.previous_scores.clear()

    def sort_players(self) -> None:
        """Sort players by score in descending order. If scores are tied, they
        are broken by alphabetically sorting the nicknames in ascending order."""
        self.sorted_players = list(self.players.values())

        # Use negative score to mimic reverse=True
        # score is priority, then nickname if scores are same
        self.sorted_players.sort(key=lambda p: (-p.score, p.nickname))

    def get_player_rank(self, player_id: str) -> int | None:
        """Get the position, or rank, of a given player ID, which can be used in numbering or ordinals."""
        try:
            index = self.sorted_players.index(self.players[player_id])
        except ValueError:
            return None

        return index + 1

    def get_top_players(self, limit: int = 5) -> list[Player]:
        """Return the top `limit` players from the leaderboard."""
        top_players = self.sorted_players[:limit]
        return top_players

    def get_adjacent_players(
        self, player_id: str, radius: int = 1
    ) -> list[Player] | None:
        """
        Gets the adjacent players around a specified player ID, within a certain `radius`.

        For example, with `radius=1`:

        - Player 0  <-- start - 1 = 0
        - Player 1  <-- start here (1)
        - Player 2  <-- start + 1 = 2

        Here, the starting is Player 1, and the radius extends by 1 player in each direction,
        returning all three players.

        Here's another example where the player is at a boundary (`radius=1`):

        - (nothing) <-- start - 1 = -1 (out of range! therefore move down to start + 2)
        - Player 0  <-- start here (0)
        - Player 1  <-- start + 1 = 1
        - Player 2  <-- start + 2 = 2 (due to out of range above)

        In summary, when the start or end exceeds a boundary as to cause an `IndexError`, it
        is moved down to ensure the "window" size remains the same.
        """
        try:
            index = self.sorted_players.index(self.players[player_id])
        except ValueError:
            return None

        length = len(self.sorted_players)

        # Get window of players
        # With radius=1, for example: [previous, current, next]
        start = index - radius
        end = index + radius

        # If start extends beyond start of list, move to end
        if start < 0:
            end += -start
            start = 0

        # If end extends beyond end of list, move to start
        if end >= length:
            start -= end - (length - 1)
            end = length - 1

        # Ensure indexes are valid if the list is smaller than the window
        start = max(0, start)
        end = min(length - 1, end)

        adjacent_players = self.sorted_players[start : end + 1]
        return adjacent_players

    def get_leaderboard(
        self, players: list[Player], delta: dict[str, int] | None = None
    ) -> list[dict[str, str | int]]:
        """Get leaderboard information from a list of players, optionally giving delta information
        to provide the points gained since last question (for the live leaderboard), or leaving
        it empty (for the final leaderboard)."""
        leaderboard = []

        for index, player in enumerate(players):
            player_data = {
                "id": player.player_id,
                "name": player.nickname,
                "place": index + 1,
                "total": player.score,
            }

            # Only add gained key if delta is given
            if delta is not None:
                player_data["gained"] = delta[player.player_id]

            leaderboard.append(player_data)

        return leaderboard

    def get_score_changes(self) -> dict[str, int]:
        """Get the delta (difference) between the current player score and previous score, for each player."""
        score_changes = {}

        for player_id, previous_score in self.previous_scores.items():
            score_delta = self.players[player_id].score - previous_score
            score_changes[player_id] = score_delta

        return score_changes
