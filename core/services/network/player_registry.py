import threading

from core.services.network.connected_client import ConnectedClient
from models.player import Player
from core.config.constants import MAX_PLAYERS, MAX_NICKNAME_LENGTH


class PlayerRegistry:
    """Stores and manages connected players."""

    def __init__(self):
        # TODO the code really assumes that the player ID is always shared between
        # players and clients. Maybe do a dict with player ID -> tuple(ConnectedClient, Player)
        # or even make a new Session class if you really want
        self.players: dict[str, Player] = {}
        self.clients: dict[str, ConnectedClient] = {}
        self.max_players = MAX_PLAYERS

        self.lock = threading.Lock()

    def add_player(self, nickname: str, client: ConnectedClient) -> str:
        """
        Add a client/player to the registry.

        Return values:
            `ok`
                Player was added successfully.

            `lobby_full`
                Registry has reached the maximum player count.

            `dupe_nickname`
                Nickname is already in use.

            `long_nickname`
                Nickname exceeds maximum character length.

        Returns:
            Return format is a string for values discussed above.
        """

        with self.lock:
            # Lobby full if player was added
            if len(self.clients) + 1 > self.max_players:
                return "lobby_full"

            if self.has_nickname(nickname):
                return "dupe_nickname"

            if len(nickname) > MAX_NICKNAME_LENGTH:
                return "long_nickname"

            # Save player
            player_id = client.player_id
            player = Player(player_id, nickname)

            self.players[player_id] = player
            self.clients[player_id] = client

            return "ok"

    def remove_player(self, player_id: str) -> bool:
        """Remove a client/player from the registry."""
        with self.lock:
            self.players.pop(player_id, None)
            client = self.clients.pop(player_id, None)

        return client is not None

    def clear_all(self) -> None:
        """Clear the client and player registry."""
        with self.lock:
            self.clients.clear()
            self.players.clear()

    def get_client(self, player_id: str) -> ConnectedClient | None:
        """Retrieve a client from the registry as a ConnectedClient."""
        return self.clients.get(player_id)

    def get_player(self, player_id: str) -> Player | None:
        """Retrieve a player from the registry as a Player."""
        return self.players.get(player_id)

    def get_id_by_nickname(self, nickname: str) -> str | None:
        """Get player ID from the registry based on nickname."""
        for player_id, player in self.players.items():
            if player.nickname == nickname:
                return player_id

        return None

    def get_clients(self) -> dict[str, ConnectedClient]:
        """Retrieve all clients from the registry as a dictionary, with player ID as the key."""
        with self.lock:
            return self.clients.copy()

    def get_players(self) -> dict[str, Player]:
        """Retrieve all players from the registry as a dictionary, with player ID as the key."""
        with self.lock:
            return self.players.copy()

    def has_id(self, player_id: str) -> bool:
        """Whether the registry contains a matching player ID in clients."""
        return player_id in self.clients

    def has_nickname(self, nickname: str) -> bool:
        """Whether the registry contains a matching player nickname in players."""
        for player in self.players.values():
            if player.nickname == nickname:
                return True

        return False
