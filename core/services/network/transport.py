import json
import socket


class JSONSocket:
    """Allows sending/receiving JSON messages over the network."""

    def __init__(self, sock: socket.socket | None = None) -> None:
        """Initialize the JSONSocket instance."""
        self.sock = sock
        self.buffer = b""

    def _validate_socket(self) -> None:
        """Ensures socket is set."""
        if self.sock is None:
            raise ValueError("Socket must be set before sending/receiving")

    def send(self, data: dict) -> None:
        """Sends a dictionary to the receiving end. The dictionary is serialized before sending."""
        self._validate_socket()

        # Add newline delimiter to signify separator, then encode and send
        msg = json.dumps(data) + "\n"
        self.sock.sendall(msg.encode())

    def recv(self) -> dict | bool | None:
        """
        Receives any incoming message. The data is deserialized before returning.

        Return values:
            `False`
                No message currently, though other end is still alive. Occurs when socket times out.

            `None`
                The connection has been closed.

            `dict`
                Deserialized data, if transport was successful.

        Returns:
            Return format is discussed above.
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

        # Retrieves first complete message, and saves remaining data in buffer
        line, self.buffer = self.buffer.split(b"\n", 1)

        try:
            return json.loads(line.decode())
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON data")

    def set_socket(self, sock: socket.socket) -> None:
        """Set the socket to be used."""
        self.sock = sock
