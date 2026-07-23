import secrets
import socket
import threading
import time

from core.services.network.transport import JSONSocket


class ConnectedClient:
    """Represents a connected client in the server."""

    def __init__(self, client_id: str, sock: socket.socket) -> None:
        self.client_id = client_id
        self.socket = sock
        self.jsock = JSONSocket(sock)

        self.last_ping_sent: float | None = None
        self.rtt_ms: float | None = None

        self.last_seen = time.monotonic()
        self.lock = threading.Lock()

    @staticmethod
    def generate_random_id() -> str:
        """Generate a random ID. Static method; can be used when initializing a ConnectedClient."""
        return secrets.token_hex(4)

    def update_last_seen(self) -> None:
        """Update time since client was last seen."""
        self.last_seen = time.monotonic()

    def send(self, msg: dict) -> None:
        """Send a message to the client."""
        # Lock to prevent multiple concurrent sends overwriting each other
        with self.lock:
            self.jsock.send(msg)

    def recv(self) -> dict | bool | None:
        """Receive a message from the client."""
        return self.jsock.recv()

    def close(self) -> None:
        """Close the client socket."""
        try:
            self.socket.close()
        except OSError:
            pass
