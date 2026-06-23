import time
import socket

from models.player import Player
from core.services.network.transport import JSONSocket


class ConnectedClient:
    """Represents a connected client in the server. Contains a Player instance."""

    def __init__(
        self, sock: socket.socket, player_id: str, player: Player | None = None
    ) -> None:
        """Initializes a ConnectedClient with an optional Player instance."""
        self.socket = sock
        self.player_id = player_id
        self.jsock = JSONSocket(sock)

        self.player: Player | None = player
        self.nickname: str | None = None

        self.last_seen = time.monotonic()

    def update_last_seen(self) -> None:
        """Update time since client was last seen."""
        self.last_seen = time.monotonic()

    def send(self, msg: dict) -> None:
        """Send a message to the client."""
        self.jsock.send(msg)

    def recv(self) -> None:
        """Receive a message from the client."""
        return self.jsock.recv()

    def close(self) -> None:
        """Close the client socket."""
        try:
            self.socket.close()
        except OSError:
            pass
