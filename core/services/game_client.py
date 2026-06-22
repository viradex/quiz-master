import socket
import threading
import time
from PyQt6.QtCore import QObject, pyqtSignal

from core.services.network.transport import JSONSocket
from core.services.network.types import ClientMessageType, ServerMessageType
from utils.networking import is_valid_ipv4
from core.config.constants import (
    PORT,
    MAX_NICKNAME_LENGTH,
    CLIENT_PING_INTERVAL,
    RESPONSE_TIMEOUT,
)


class GameClient(QObject):
    """Manages the networking relating to the game client."""

    # Define signals for communicating from service to logic
    connecting = pyqtSignal()
    connection_fail = pyqtSignal(str)
    connection_success = pyqtSignal(list)

    player_joined = pyqtSignal(str)
    player_left = pyqtSignal(str)
    player_list = pyqtSignal(list)

    disconnecting = pyqtSignal()

    kick = pyqtSignal(str)
    error = pyqtSignal(str)
    invalid_action = pyqtSignal(str)

    def __init__(self) -> None:
        """Initialize client attributes and handlers for server messages."""
        super().__init__()

        self.server_ip = ""
        self.port = PORT
        self.is_connected = False
        self.jsock = JSONSocket()

        self.client_socket: socket.socket | None = None
        self.player_id: str | None = None
        self.nickname: str | None = None
        self.last_ping_time: float | None = None

        self.handlers: dict[ServerMessageType, function] = {
            ServerMessageType.PONG: lambda *args: None,
            ServerMessageType.CONNECTION_SUCCESSFUL: self.handle_connection_successful,
            ServerMessageType.PLAYER_JOINED: self.handle_player_joined,
            ServerMessageType.PLAYER_LEFT: self.handle_player_left,
            ServerMessageType.KICK: self.handle_kick,
            ServerMessageType.ERROR: self.handle_error,
            ServerMessageType.INVALID_ACTION: self.handle_invalid_action,
        }

    def set_ip(self, ip: str) -> None:
        """Sets server IP to connect to. Must be a valid IPv4 address."""
        if not is_valid_ipv4(ip):
            raise ValueError(f"IP '{ip}' is not a valid IPv4 address")

        self.server_ip = ip

    def set_nickname(self, nickname: str) -> None:
        """Sets nickname. Must not be empty and cannot exceed maximum nickname length."""
        if not nickname or len(nickname) > MAX_NICKNAME_LENGTH:
            raise ValueError(
                f"Nickname '{nickname}' exceeds length range: min 1 char, max {MAX_NICKNAME_LENGTH} chars"
            )

        self.nickname = nickname

    def get_server_address(self) -> tuple[str, int]:
        """Gets server IP and port that the client is connected to."""
        return self.client_socket.getpeername()

    def connect(self) -> None:
        """Connects to the server set in `server_ip`."""
        if not self.server_ip or not self.nickname:
            raise ValueError("Server IP and nickname must have values")

        self.connecting.emit()

        # Run in separate thread to avoid freezing UI
        threading.Thread(target=self._connect_and_listen, daemon=True).start()

    def disconnect_client(self) -> None:
        """Disconnect client from the server cleanly, notifying server and logic."""
        if self.client_socket is None:
            raise ValueError("Client cannot be closed without active socket")

        try:
            self.jsock.send({"type": ClientMessageType.LEAVE_LOBBY})
        except OSError:
            pass

        self.disconnecting.emit()

        self.is_connected = False
        self.client_socket.close()

    def start_ping_loop(self) -> None:
        """Starts regular ping heartbeat loop."""
        threading.Thread(target=self._ping_loop, daemon=True).start()

    def start_watchdog(self) -> None:
        """Starts watchdog (disconnects client if no response from the server is detected)."""
        threading.Thread(target=self._watchdog_loop, daemon=True).start()

    def listen(self) -> None:
        """Listens for messages from the server."""
        while self.is_connected:
            try:
                msg = self.jsock.recv()
            except socket.timeout:
                continue
            except OSError:
                break

            # Connection is dead
            if msg is None:
                break

            # No message currently (still alive)
            if msg is False:
                continue

            # Any message from server means connection is still stable
            self.last_ping_time = time.monotonic()
            self.handle_message(msg)

    def _connect_and_listen(self) -> None:
        """Connects to the server using the host IP and port, and listens for oncoming requests."""
        try:
            # Connect to the server
            self.client_socket = socket.create_connection(
                (self.server_ip, self.port), timeout=5
            )
            self.client_socket.settimeout(1.0)

            self.jsock.set_socket(self.client_socket)
        except ConnectionRefusedError:
            # Server refused connction
            self.connection_fail.emit("refused")
            return
        except TimeoutError:
            # Could not connect to server within timeout
            self.connection_fail.emit("timeout")
            return
        except OSError as e:
            if e.errno == 10065:
                # Server is unreachable
                self.connection_fail.emit("unreachable")
                return
            else:
                # technically, start_fail could be emitted,
                # but it would be pointless due to the 'raise'
                raise

        self.is_connected = True

        # Inform server of join and reset server ping time
        self.send_join()
        self.last_ping_time = time.monotonic()

        # Start listening for server pings and ensure connection remains through watchdog
        threading.Thread(target=self.listen, daemon=True).start()
        self.start_ping_loop()
        self.start_watchdog()

    def _ping_loop(self) -> None:
        """Pings the server at a certain interval, to request a `PONG` and inform the server that the client is alive."""
        while self.is_connected:
            try:
                self.jsock.send({"type": ClientMessageType.PING})
            except OSError:
                break

            # Do not keep sending PINGs, wait for a few seconds
            time.sleep(CLIENT_PING_INTERVAL)

    def _watchdog_loop(self) -> None:
        """Checks last response time from server. If it exceeds response timeout, disconnect server."""
        while self.is_connected:
            time.sleep(1)

            if time.monotonic() - self.last_ping_time > RESPONSE_TIMEOUT:
                self.time_out()
                break

    def time_out(self) -> None:
        """Disconnect the client due to a timeout from the watchdog."""
        self.is_connected = False

        try:
            self.client_socket.close()
        except OSError:
            pass

        self.kick.emit("Connection timed out")

    def handle_message(self, msg: dict) -> None:
        """Handles a message from the server by delegating it to a respective handler."""
        msg_type = msg.get("type")

        # No message type; client cannot delegate it
        if msg_type is None:
            print(f"'type' key was not present in message, received: {msg}")
            return

        handler = self.handlers.get(msg_type)

        # Message type does not have a respective handler
        if handler is None:
            print(f"The msg_type {msg_type} did not match any types")
            return

        handler(msg)

    def handle_connection_successful(self, msg: dict) -> None:
        """Handles the `CONNECTION_SUCCESSFUL` message type. Sets player ID."""
        player_id = msg["data"]["player_id"]
        player_list = msg["data"]["player_list"]
        self.player_id = player_id

        self.connection_success.emit(player_list)

    def handle_player_joined(self, msg: dict) -> None:
        """Handles the `PLAYER_JOINED` message type."""
        nickname = msg["data"]["nickname"]
        self.player_joined.emit(nickname)

    def handle_player_left(self, msg: dict) -> None:
        """Handles the `PLAYER_LEFT` message type."""
        nickname = msg["data"]["nickname"]
        self.player_left.emit(nickname)

    def handle_kick(self, msg: dict) -> None:
        """Handles the `KICK` message type. Disconnects the client."""
        reason = msg["data"]["reason"]
        self.kick.emit(reason)

        self.disconnect_client()

    def handle_error(self, msg: dict) -> None:
        """Handles the `ERROR` message type. Disconnects the client."""
        reason = msg["data"]["reason"]
        self.error.emit(reason)

        self.disconnect_client()

    def handle_invalid_action(self, msg: dict) -> None:
        """Handles the `INVALID_ACTION` message type."""
        reason = msg["data"]["reason"]
        self.invalid_action.emit(reason)

    def send_join(self) -> None:
        """Sends a `JOIN_LOBBY` message type. Sends nickname to server."""
        self.jsock.send(
            {
                "type": ClientMessageType.JOIN_LOBBY,
                "data": {"nickname": self.nickname},
            }
        )
