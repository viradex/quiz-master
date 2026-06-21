import threading

from core.services.network.connected_client import ConnectedClient
from models.player import Player
from core.config.constants import MAX_PLAYERS


class PlayerRegistry:
    """Stores and manages connected players."""

    def __init__(self):
        self.players: dict[str, ConnectedClient] = {}
        self.max_players = MAX_PLAYERS

        self.lock = threading.Lock()

    def add_player(
        self, nickname: str, client: ConnectedClient
    ) -> tuple[str, Player | None]:
        """
        Add a player to the registry.

        Return values:
            `("ok", player)`
                Player was added successfully.

            `("lobby_full", None)`
                Registry has reached the maximum player count.

            `("dupe_nickname", None)`
                Nickname is already in use.

            `("dupe_id", None)`
                Player ID already exists.

        Returns:
            Return format is `(status, data)` for values discussed above.
        """

        with self.lock:
            # Lobby full if player was added
            if len(self.players) + 1 > self.max_players:
                return ("lobby_full", None)

            for existing in self.players.values():
                # Nickname already exists
                if existing.nickname == nickname:
                    return ("dupe_nickname", None)

                # ID already exists
                elif existing.player_id == client.player_id:
                    return ("dupe_id", None)

            # Save player
            self.players[client.player_id] = client

        player = Player(client.player_id, nickname)
        return ("ok", player)

    def remove_player(self, player_id: str) -> bool:
        """Remove a player from the registry."""
        with self.lock:
            client = self.players.pop(player_id, None)

        return client is not None

    def clear_players(self) -> None:
        """Clear the player registry."""
        with self.lock:
            self.players.clear()

    def get_player(self, player_id: str) -> ConnectedClient | None:
        """Retrieve a player from the registry as a ConnectedClient."""
        with self.lock:
            return self.players.get(player_id)

    def get_id_by_nickname(self, nickname: str) -> str | None:
        """Get player ID from the registry based on nickname."""
        for player_id, client in self.get_players().items():
            if client.nickname == nickname:
                return player_id

        return None

    def get_players(self) -> dict[str, ConnectedClient]:
        """Retrieve all players from the registry as a dictionary, with player ID as the key."""
        with self.lock:
            return dict(self.players)

    def has_id(self, player_id: str) -> bool:
        """Whether the registry contains a matching player ID."""
        client = self.get_player(player_id)
        return client is not None

    def has_nickname(self, nickname: str) -> bool:
        """Whether the registry contains a matching player nickname."""
        for client in self.get_players().values():
            if client.nickname == nickname:
                return True

        return False
