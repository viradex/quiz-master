"""
leaderboard.py

A model that represents a leaderboard in the quiz game, allowing managing a collection of players
and their ranks.
"""

from models.player import Player


class Leaderboard:
    """
    A leaderboard model for managing a collection of players and providing functionality for leaderboard
    related actions, such as ranking, tracking score changes, and generating leaderboard data. Acts as a
    central manager for all leaderboard-related operations and data in the quiz game.
    """

    def __init__(self) -> None:
        # Maps player ID to the Player object; a dictionary is used for fast lookup
        self.players: dict[str, Player] = {}

        # List of players that are ordered by leaderboard ranking; a list is used as it is sorted
        self.sorted_players: list[Player] = []

        # Stores each player's previous points before the latest updates for delta calculations
        self.previous_points: dict[str, int] = {}

    def add_player(self, player: Player) -> None:
        """
        Adds a player to the leaderboard. Does not add them to the sorted collection.

        Arguments:
            player: The Player to add to the leaderboard. A Player object is used as it allows using its helper
                properties and methods.

        Returns:
            None.
        """
        self.players[player.player_id] = player

    def remove_player(self, player_id: str) -> bool:
        """
        Removes a player from the leaderboard. Clears all references to the player ID from the main storage
        of players, the sorted players collection, and previous points collection. If the player ID did not
        exist, the removal is not done.

        Arguments:
            player_id: A string describing the ID of the Player instance to remove. A string is used as it
                can flexibly store IDs and can store many characters to make them more unique.

        Returns:
            A boolean specifying if removal was successful. True is returned if the player was found and removed,
            else, returns False if the player could not be found by ID.
        """
        # Gives None if not found, to avoid KeyError
        player = self.players.pop(player_id, None)
        self.previous_points.pop(player_id, None)

        # Removes all occurrences of the ID in the sorted players, though in
        # normal operation there should only ever be one.
        self.sorted_players = [
            p for p in self.sorted_players if p.player_id != player_id
        ]

        # Returns True if player was found
        return player is not None

    def sort_players(self) -> None:
        """
        Sorts players into leaderboard order. The sorting criteria is as follows:

        1. Highest score first
        2. Alphabetical nickname as a tiebreaker

        Returns:
            None.
        """
        # Use negative score to mimic reverse=True
        self.sorted_players = sorted(
            self.players.values(), key=lambda p: (-p.total_points, p.nickname)
        )

    def snapshot_points(self) -> None:
        """
        Saves all current scores saved in the leaderboard to a separate data storage, for calculating the
        delta. This should be run before updating scores for the next question, and should be set before
        running `get_score_changes()`.

        Returns:
            None.
        """
        for player_id, player in self.players.items():
            self.previous_points[player_id] = player.total_points

    def get_player_rank(self, player_id: str) -> int | None:
        """
        Gets the position, or rank, of the specified player by player ID, if they exist. This can be used for
        numbering in leaderboards or ordinals.

        Arguments:
            player_id: A string describing the ID of the Player instance to locate. A string is used as it
                can flexibly store IDs and can store many characters to make them more unique.

        Returns:
            The rank of the player as an integer, starting from 1 for first place and extending until the
            end of the leaderboard. Returns None if the player could not be found. An integer is used as
            opposed to a string as the integer can be used in conditionals and arithmetic.
        """
        # Get player index and add 1 to it, as index is zero-based
        index = self._get_player_index(player_id)
        return None if index is None else index + 1

    def is_on_podium(self, player_id: str) -> bool | None:
        """
        Checks if the player provided is on the podium, meaning the first three ranks of the leaderboard.

        Arguments:
            player_id: A string describing the ID of the Player instance to locate. A string is used as it
                can flexibly store IDs and can store many characters to make them more unique.

        Returns:
            Whether the player is on the podium or not. Returns True if the player is, else, returns False.
            Returns None if the player could not be found.
        """
        player_rank = self.get_player_rank(player_id)
        if player_rank is None:
            return None

        return player_rank <= 3

    def is_first(self, player_id: str) -> bool | None:
        """
        Checks if the player provided is at first place.

        Arguments:
            player_id: A string describing the ID of the Player instance to locate. A string is used as it
                can flexibly store IDs and can store many characters to make them more unique.

        Returns:
            Whether the player is at first place. Returns True if the player is, else, returns False. Returns
            None if the player could not be found.
        """
        player_rank = self.get_player_rank(player_id)
        if player_rank is None:
            return None

        return player_rank == 1

    def is_last(self, player_id: str) -> bool | None:
        """
        Checks if the player provided is at last place.

        Arguments:
            player_id: A string describing the ID of the Player instance to locate. A string is used as it
                can flexibly store IDs and can store many characters to make them more unique.

        Returns:
            Whether the player is at last place. Returns True if the player is, else, returns False. Returns
            None if the player could not be found.
        """
        player_rank = self.get_player_rank(player_id)
        if player_rank is None:
            return None

        return player_rank == len(self.players)

    def get_players(self, limit: int | None = None) -> list[Player]:
        """
        Gets all the sorted players from the leaderboard, or optionally specify a limit to only get the top
        `limit` players.

        Arguments:
            limit: The maximum number of players to get from the leaderboard, starting from the top. For
                example, specifying '5' would get all players who ranked 1st to 5th place. Setting this to
                None gets all the players in the leaderboard. Default is None, where it gets all the players.

        Returns:
            A copy of the sorted list of players, or a subsection of it if the `limit` was specified. A list is
            returned as lists can be sorted.
        """
        if limit is None:
            return self.sorted_players.copy()
        else:
            return self.sorted_players[:limit]

    def get_points_behind(self, player_id: str) -> tuple[str | None, int | None]:
        """
        Gets the nickname of the player immediately ahead, and the number of points needed to catch up to them.
        If the player could not be found, both values returned are None. If the player is first, the nickname
        is None, and the points is 0. Otherwise, the player nickname and points behind are returned.

        Arguments:
            player_id: A string describing the ID of the Player instance to locate. A string is used as it
                can flexibly store IDs and can store many characters to make them more unique.

        Returns:
            The values discussed above, as a tuple where the first value is the nickname of the player in front,
            or None if the current player could not be found or the player is in first place. The second value
            of the tuple is the number of points as an integer, or None if the current player could not be found,
            or 0 if the player is in first place. A tuple is returned for easier deconstruction.
        """

        index = self._get_player_index(player_id)

        # If player could not be found
        if index is None:
            return None, None

        # If player is first
        if index == 0:
            return None, 0

        current_player_points = self.players[player_id].total_points

        # Get the player one position ahead
        player_ahead_points = self.sorted_players[index - 1].total_points
        player_ahead_nickname = self.sorted_players[index - 1].nickname

        # Calculate difference in points and return that as well as nickname
        return player_ahead_nickname, player_ahead_points - current_player_points

    def get_adjacent_players(
        self, player_id: str, radius: int = 1
    ) -> list[Player] | None:
        """
        Gets a subsection of the leaderboard around the specified player within a certain radius. The method
        automatically adjusts the window so that the returned leaderboard ensures the player remains as close
        to the center as possible, while also ensuring to fill as many slots as possible and ensure it does not
        exceed list boundaries. This method is useful for showing a player the localized rankings around them.

        For example, with `radius=1`:

        - (nothing) <-- start - 1 = -1 (out of range! therefore move down to start + 2)
        - Player 0  <-- start here (0)
        - Player 1  <-- start + 1 = 1
        - Player 2  <-- start + 2 = 2 (due to out of range above)

        Arguments:
            player_id: A string describing the ID of the Player instance to get values around. A string is used
                as it can flexibly store IDs and can store many characters to make them more unique.

            radius: The radius around the player specified to get values for. For example, specifying a value of
                '1' provides three values in total: the player itself, the player above, and the player below.
                An integer is used as it makes it simpler to use in calculating the window size.

        Returns:
            The sorted list of players that are adjacent to the player provided, or None if the player could
            not be found. A list is returned as lists can be sorted.
        """
        index = self._get_player_index(player_id)
        if index is None:
            return None

        length = len(self.sorted_players)
        window = radius * 2 + 1

        # Gets starting index, ensuring it never goes below 0
        start = max(0, index - radius)
        end = start + window

        # If end extends beyond end of list, move to start
        if end > length:
            end = length
            start = max(0, end - window)

        # Return spliced list from start to end
        return self.sorted_players[start:end]

    def get_points_delta(self) -> dict[str, int]:
        """
        Gets the points delta for every player by comparing their current score with their previous score saved
        from `snapshot_points()`.

        Returns:
            A dictionary mapping player IDs to the amount of points gained between the previous score and current
            score. A dictionary is used as it can group the related values together and categorize them by ID.
        """
        score_changes = {}

        for player_id, previous_score in self.previous_points.items():
            # Gets difference between total score and previous total score
            score_delta = self.players[player_id].total_points - previous_score
            score_changes[player_id] = score_delta

        return score_changes

    def get_leaderboard(
        self, players: list[Player], delta: dict[str, int] | None = None
    ) -> list[dict]:
        """
        Converts a list of sorted players into a structured list of dictionaries for displaying leaderboard
        data on the UI, or sending as JSON data. Each entry in the leaderboard list is a dictionary containing
        the player ID, player nickname, rank, and total points so far.

        If the delta information is provided, the gained points is also provided in the dictionary. Typically,
        the delta information is provided for question results, but not provided for final results.

        Arguments:
            players: The sorted list of players to get leaderboard data for. A list is used as it groups the
                similar values together, and is also the value returned by `get_players()`.

            delta: An optional dictionary containing delta information for the difference in points between the
                current state and previous state. If this dictionary is provided, delta information will be
                included in the leaderboard data. Otherwise, if set to None or left as its default of None, the
                delta value will not be included in the return value. A dictionary is used to group the player
                ID together with its score, and is also the value returned by `get_points_delta()`.

        Returns:
            A list containing dictionaries describing each leaderboard entry from the list of players specified.
            A list is provided as it groups the dictionary entries together.
        """
        leaderboard = []

        for player in players:
            # Get data from player instance
            player_data = {
                "player_id": player.player_id,
                "nickname": player.nickname,
                "rank": self.get_player_rank(player.player_id),
                "total": player.total_points,
            }

            # Only add gained key if delta is given
            if delta is not None:
                player_data["gained"] = delta[player.player_id]

            leaderboard.append(player_data)

        return leaderboard

    def get_global_leaderboard(self, include_delta: bool = False) -> list[dict]:
        """
        Generates complete leaderboard data for all players that are currently stored in the leaderboard.
        Retrieves all sorted players, and optionally calculates deltas, before retrieving the entire
        leaderboard data. Acts as a convenience method for `get_leaderboard()` to get the entire leaderboard
        data instead, as well as for performing the delta calculations automatically.

        Arguments:
            include_delta: Whether to include delta information in the leaderboard entries or not. If True,
                gets the delta from when `snapshot_points()` was last called. Otherwise, does not include delta
                information.

        Returns:
            A list containing dictionaries describing each leaderboard entry from all the players stored in the
            leaderboard. A list is provided as it groups the dictionary entries together.
        """
        players = self.get_players()
        delta = self.get_points_delta() if include_delta else None

        return self.get_leaderboard(players, delta)

    def _get_player_index(self, player_id: str) -> int | None:
        """
        Internal method. Locates the position of the specified player on the sorted players list, returning its
        zero-based index on the list, if it exists. Prevents duplicating search logic across multiple methods.

        Arguments:
            player_id: A string describing the ID of the Player instance to locate. A string is used as it
                can flexibly store IDs and can store many characters to make them more unique.

        Returns:
            The index of the player as an integer, starting from 0 for first place and extending until the
            end of the leaderboard minus one. Returns None if the player could not be found. An integer is
            used as it can be used for indexing.
        """
        player = self.players.get(player_id)
        if player is None:
            return None

        try:
            return self.sorted_players.index(player)
        except ValueError:
            return None

    def clear(self) -> None:
        """
        Clears the registry by clearing all values within the players, sorted players, and previous points data
        structures, to reset it to its initial state and prepare it for a new game.

        Returns:
            None.
        """
        self.players.clear()
        self.sorted_players.clear()
        self.previous_points.clear()
