import threading

from core.services.network.connected_client import ConnectedClient
from models.player import Player
from models.session import Session
from core.config.constants import MAX_PLAYERS, MAX_NICKNAME_LENGTH


class PlayerRegistry:
    """Stores and manages connected players."""

    def __init__(self):
        self.sessions: dict[str, Session] = {}
        self.max_players = MAX_PLAYERS

        self.lock = threading.Lock()

    def add(self, nickname: str, client: ConnectedClient) -> tuple[bool, str]:
        """
        Add a client/player to the registry.

        Return values:
            `(True, "")`
                Player was added successfully.

            `(False, "lobby_full")`
                Registry has reached the maximum player count.

            `(False, "dupe_nickname")`
                Nickname is already in use.

            `(False, "long_nickname")`
                Nickname exceeds maximum character length.

        Returns:
            Return format is a (success, reason) for values discussed above.
        """

        with self.lock:
            # Lobby full if player was added
            if len(self.sessions) + 1 > self.max_players:
                return (False, "lobby_full")

            if self.has_nickname(nickname):
                return (False, "dupe_nickname")

            if len(nickname) > MAX_NICKNAME_LENGTH:
                return (False, "long_nickname")

            # Save player
            player_id = client.player_id
            player = Player(player_id, nickname)

            self.sessions[player_id] = Session(player, client)
            return (True, "")

    def remove(self, player_id: str) -> bool:
        """Remove a client/player from the registry."""
        with self.lock:
            session = self.sessions.pop(player_id, None)

        return session is not None

    def clear(self) -> None:
        """Clear the registry."""
        with self.lock:
            self.sessions.clear()

    def get(self, player_id: str) -> Session | None:
        """Retrieve a client and player from the registry as a Session."""
        with self.lock:
            return self.sessions.get(player_id)

    def get_id_by_nickname(self, nickname: str) -> str | None:
        """Get player ID from the registry based on nickname."""
        for player_id, session in self.sessions.items():
            if session.player.nickname == nickname:
                return player_id

        return None

    def get_all(self) -> dict[str, Session]:
        """Retrieve all clients from the registry as a dictionary, with player ID as the key."""
        with self.lock:
            return self.sessions.copy()

    def has_id(self, player_id: str) -> bool:
        """Whether the registry contains a matching player ID."""
        return player_id in self.sessions

    def has_nickname(self, nickname: str) -> bool:
        """Whether the registry contains a matching player nickname in players."""
        for session in self.sessions.values():
            if session.player.nickname == nickname:
                return True

        return False
