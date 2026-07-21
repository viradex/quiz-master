import json
import socket

from core.config.constants import MAX_MESSAGE_SIZE


class JSONSocket:
    """Allows sending/receiving JSON messages over the network."""

    def __init__(self, sock: socket.socket | None = None) -> None:
        self.sock = sock

        # Networking data doesn't always arrive as complete strings, so use buffer
        self.buffer = b""

    def send(self, data: dict) -> None:
        """Sends a dictionary to the receiving end. The dictionary is serialized before sending."""
        self._validate_socket()

        # Add newline delimiter to signify separator, then encode and send
        try:
            msg = json.dumps(data) + "\n"
        except (TypeError, ValueError) as e:
            raise ValueError("Invalid JSON data") from e

        # sendall() to automatically send all bytes
        self.sock.sendall(msg.encode())

    def recv(self) -> dict | bool | None:
        """
        Receives any incoming message. The data is deserialized before returning.

        Raises a ValueError if the JSON is invalid or the message exceeds the maximum size as defined in `MAX_MESSAGE_SIZE`.

        Return values:
            `False`
                No message currently, though other end is still alive. Occurs when socket times out.

            `None`
                The connection has been closed.

            `dict`
                Deserialized data, if transport was successful.
        """
        self._validate_socket()

        # Keeps reading until reaching end of message
        while b"\n" not in self.buffer:
            try:
                chunk = self.sock.recv(4096)
            except socket.timeout:
                return False
            except OSError:
                return None

            # Connection closed
            if not chunk:
                return None

            self.buffer += chunk

            # Protects server against huge messages, which can cause intense CPU and memory usage
            if len(self.buffer) > MAX_MESSAGE_SIZE:
                raise ValueError("Message too large")

        # Retrieves first complete message, and saves remaining data in buffer
        line, self.buffer = self.buffer.split(b"\n", 1)

        try:
            return json.loads(line.decode())
        except json.JSONDecodeError as e:
            raise ValueError("Invalid JSON data") from e

    def set_socket(self, sock: socket.socket) -> None:
        """Set the socket to be used."""
        self.sock = sock

    def _validate_socket(self) -> None:
        """Ensures socket is set."""
        if self.sock is None:
            raise RuntimeError("Socket must be set before sending/receiving")
