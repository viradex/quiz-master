"""
player_registry.py

Manager and registry for all players and connected clients in the server, as sessions.
"""

import threading

from core.app.enums import AddPlayerResult
from core.config.constants import MAX_NICKNAME_LENGTH, MAX_PLAYERS
from core.services.network.connected_client import ConnectedClient
from models.player import Player
from models.session import Session


class PlayerRegistry:
    """
    A thread-safe registry for storing players and connected clients as Sessions, to keep track of all
    players and clients currently connected to the server. Provides methods to modify the registry while
    ensuring only one thread can update the registry at once, to prevent corruption.
    """

    def __init__(self) -> None:
        # Storage of each session, identified by player ID
        self.sessions: dict[str, Session] = {}

        # When doing data manipulation relating to self.sessions, you must use
        # self._lock to prevent race conditions. To avoid deadlocks, make a private
        # 'unlocked' version when needed and call that in the method which already
        # holds the lock.
        self._lock = threading.Lock()

    def add(self, nickname: str, client: ConnectedClient) -> AddPlayerResult:
        """
        Creates and adds a Session to the registry, which pairs the newly-created Player and the ConnectedClient
        passed. Performs validation checks before saving the player. The Player is created using the
        ConnectedClient's client ID.

        The following checks are performed:
        - Whether adding the player would exceed the maximum number of players allowed.
        - Whether the nickname already exists.
        - Whether the nickname is empty.
        - Whether the nickname exceeds the maximum number of characters.

        If any of these checks fail, the method is returned early with the specific error as an AddPlayerResult.
        Otherwise, an `OK` result is returned, if the operation was successful.

        Uses a threading lock to avoid corruption from multiple threads editing the registry at once, meaning
        it should not be run inside another method that holds the lock to avoid deadlocks.

        Arguments:
            nickname: The nickname to save the Player as. A string is used as a nickname is easily represented
                by a string.

            client: The already-created ConnectedClient to save alongside the created Player in the registry.

        Returns:
            Any error that occurred while adding the player to the registry if it failed, or `OK` if the
            player was successfully added to the registry.
        """
        nickname = nickname.strip()

        with self._lock:
            # Lobby full if player was added
            if len(self.sessions) + 1 > MAX_PLAYERS:
                return AddPlayerResult.LOBBY_FULL

            # Must use unlocked version of has_nickname() to avoid deadlock
            if self._has_nickname_unlocked(nickname):
                return AddPlayerResult.DUPLICATE_NICKNAME

            if not nickname:
                return AddPlayerResult.EMPTY_NICKNAME

            if len(nickname) > MAX_NICKNAME_LENGTH:
                return AddPlayerResult.LONG_NICKNAME

            # Create player
            player_id = client.client_id
            player = Player(player_id, nickname)

            # Save session
            self.sessions[player_id] = Session(player, client)
            return AddPlayerResult.OK

    def remove(self, player_id: str) -> bool:
        """
        Removes a Session from the registry, identified by the player/client ID.

        Uses a threading lock to avoid corruption from multiple threads editing the registry at once, meaning
        it should not be run inside another method that holds the lock to avoid deadlocks.

        Arguments:
            player_id: A string describing the ID that is linked to the Session to remove. A string is used
                as it can flexibly store IDs and can store many characters to make them more unique.

        Returns:
            A boolean specifying if removal was successful. True is returned if the session was found and removed,
            else, returns False if the session could not be found by ID.
        """
        with self._lock:
            # Gives None if session was not found, to avoid KeyError
            session = self.sessions.pop(player_id, None)

        # Returns True if session was found
        return session is not None

    def clear(self) -> None:
        """
        Clears the registry by removing all Session instances, including their ConnectedClient and Player
        instances.

        Uses a threading lock to avoid corruption from multiple threads editing the registry at once, meaning
        it should not be run inside another method that holds the lock to avoid deadlocks.

        Returns:
            None.
        """
        with self._lock:
            self.sessions.clear()

    def get(self, player_id: str) -> Session | None:
        """
        Retrieves a Session from the registry, identified by the player ID. The Session contains both the
        ConnectedClient and the Player.

        Uses a threading lock to avoid corruption from multiple threads editing the registry at once, meaning
        it should not be run inside another method that holds the lock to avoid deadlocks.

        Arguments:
            player_id: A string describing the ID that is linked to the Session to retrieve. A string is used
                as it can flexibly store IDs and can store many characters to make them more unique.

        Returns:
            The Session object if it was found in the registry, or None if the Session could not be found from
            the player ID.
        """
        with self._lock:
            return self.sessions.get(player_id)

    def get_all(self) -> dict[str, Session]:
        """
        Retrieves all Sessions from the registry as a dictionary with the player ID as the key. The Session
        contains both the ConnectedClient and the Player. A copy of the registry is returned.

        Uses a threading lock to avoid corruption from multiple threads editing the registry at once, meaning
        it should not be run inside another method that holds the lock to avoid deadlocks.

        Returns:
            A dictionary containing all the Session objects identified by the player IDs, as a copy of the
            registry.
        """
        with self._lock:
            return self.sessions.copy()

    def has_id(self, player_id: str) -> bool:
        """
        Whether the registry already contains the player ID provided. This should be used before adding a new
        Session to the registry to avoid ID duplication and overwriting an existing entry, if it exists. Does
        not search the properties of Player and/or ConnectedClient.

        Uses a threading lock to avoid corruption from multiple threads editing the registry at once, meaning
        it should not be run inside another method that holds the lock to avoid deadlocks.

        Arguments:
            player_id: A string describing the ID to search the registry for. A string is used as it can
                flexibly store IDs and can store many characters to make them more unique.

        Returns:
            A boolean stating if the ID exists or not. Returns True if the ID was found in the registry as a key,
            else, returns False.
        """
        with self._lock:
            return player_id in self.sessions

    def has_nickname(self, nickname: str) -> bool:
        """
        Whether the registry already contains the nickname provided. This checks the nicknames stored in the
        Player objects of each Session in the registry.

        Uses a threading lock to avoid corruption from multiple threads editing the registry at once, meaning
        it should not be run inside another method that holds the lock to avoid deadlocks.

        Arguments:
            nickname: A string describing the nickname to search the registry for. A string is used as it can
                flexibly store nicknames.

        Returns:
            A boolean stating if the nickname exists or not. Returns True if the nickname was found in a Player
            instance in the registry, else, returns False.
        """
        with self._lock:
            return self._has_nickname_unlocked(nickname)

    def _has_nickname_unlocked(self, nickname: str) -> bool:
        """
        Internal method. Whether the registry already contains the nickname provided. This can be used before
        adding a new Session to the registry to avoid nickname duplication, if it exists. This checks the
        nicknames stored in the Player objects of each Session in the registry.

        This is an unlocked version of `has_nickname()`, to avoid deadlocks. **Only call this method if
        `self._lock` has been acquired!**

        Arguments:
            nickname: A string describing the nickname to search the registry for. A string is used as it can
                flexibly store nicknames.

        Returns:
            A boolean stating if the nickname exists or not. Returns True if the nickname was found in a Player
            instance in the registry, else, returns False.
        """
        for session in self.sessions.values():
            if session.player.nickname == nickname:
                return True

        return False
