import time
import socket
import threading

from core.services.network.transport import JSONSocket


class ConnectedClient:
    """Represents a connected client in the server."""

    def __init__(self, sock: socket.socket, player_id: str) -> None:
        """Initializes a ConnectedClient."""
        self.socket = sock
        self.player_id = player_id
        self.jsock = JSONSocket(sock)

        self.last_seen = time.monotonic()
        self.lock = threading.Lock()

    def update_last_seen(self) -> None:
        """Update time since client was last seen."""
        self.last_seen = time.monotonic()

    def send(self, msg: dict) -> None:
        """Send a message to the client."""
        with self.lock:
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
