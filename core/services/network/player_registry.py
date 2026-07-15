import threading

from core.app.enums import AddPlayerResult
from core.services.network.connected_client import ConnectedClient
from models.player import Player
from models.session import Session

from core.config.constants import MAX_PLAYERS, MAX_NICKNAME_LENGTH


class PlayerRegistry:
    """Stores and manages connected players."""

    def __init__(self) -> None:
        self.sessions: dict[str, Session] = {}
        self.max_players = MAX_PLAYERS

        # When doing data manipulation relating to self.sessions, you must use self.lock
        # to prevent race conditions. To avoid deadlocks, make a private 'unlocked' version
        # when needed and call that in the method which already holds the lock.
        self.lock = threading.Lock()

    def add(self, nickname: str, client: ConnectedClient) -> AddPlayerResult:
        """Add a client/player to the registry."""
        nickname = nickname.strip()

        with self.lock:
            # Lobby full if player was added
            if len(self.sessions) + 1 > self.max_players:
                return AddPlayerResult.LOBBY_FULL

            # Must use unlocked version of has_nickname() to avoid deadlock
            if self._has_nickname_unlocked(nickname):
                return AddPlayerResult.DUPLICATE_NICKNAME

            if not nickname:
                return AddPlayerResult.EMPTY_NICKNAME

            if len(nickname) > MAX_NICKNAME_LENGTH:
                return AddPlayerResult.LONG_NICKNAME

            # Create player
            player_id = client.player_id
            player = Player(player_id, nickname)

            # Save session
            self.sessions[player_id] = Session(player, client)
            return AddPlayerResult.OK

    def remove(self, player_id: str) -> bool:
        """Remove a client/player from the registry. Returns True if the player existed."""
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

    def get_all(self) -> dict[str, Session]:
        """Retrieve all clients from the registry as a dictionary, with player ID as the key."""
        with self.lock:
            return self.sessions.copy()

    def has_id(self, player_id: str) -> bool:
        """Whether the registry contains a matching player ID."""
        with self.lock:
            return player_id in self.sessions

    def has_nickname(self, nickname: str) -> bool:
        """Whether the registry contains a matching player nickname in players."""
        with self.lock:
            return self._has_nickname_unlocked(nickname)

    def _has_nickname_unlocked(self, nickname: str) -> bool:
        """Unlocked version of `has_nickname()`. Only call this method if `self.lock` has been aquired."""
        for session in self.sessions.values():
            if session.player.nickname == nickname:
                return True

        return False
