import errno
import socket
import threading
import time
from collections.abc import Callable

from PyQt6.QtCore import QObject, pyqtSignal

from core.app.enums import ClientConnectionError
from core.services.network.transport import JSONSocket
from core.services.network.types import ClientMessageType, ServerMessageType

from utils.networking import is_valid_ipv4
from core.config.constants import (
    CLIENT_CONNECTION_TIMEOUT,
    CLIENT_PING_INTERVAL,
    MAX_NICKNAME_LENGTH,
    PORT,
    RESPONSE_TIMEOUT,
)


class GameClient(QObject):
    """Manages the networking relating to the game client."""

    connected = pyqtSignal(list)  # Player list
    connection_failed = pyqtSignal(ClientConnectionError)

    player_joined = pyqtSignal(str)  # Player name
    player_left = pyqtSignal(str)  # Player name

    countdown_started = pyqtSignal(int)  # Countdown duration (seconds)
    question_received = pyqtSignal(dict)  # Question payload
    results_received = pyqtSignal(dict)  # Results payload
    final_results_received = pyqtSignal(dict)  # Final results payload

    # Reason (for all below)
    kicked = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    invalid_action_occurred = pyqtSignal(str)

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
        self.last_server_response_time: float | None = None

        # Handlers for incoming server messages
        self.handlers: dict[ServerMessageType, Callable[[dict], None]] = {
            ServerMessageType.PONG: lambda *args: None,
            ServerMessageType.CONNECTION_SUCCESSFUL: self.handle_connection_successful,
            ServerMessageType.PLAYER_JOINED: self.handle_player_joined,
            ServerMessageType.PLAYER_LEFT: self.handle_player_left,
            ServerMessageType.COUNTDOWN_STARTED: self.handle_countdown_started,
            ServerMessageType.QUESTION_DATA: self.handle_question_data,
            ServerMessageType.RESULTS: self.handle_results,
            ServerMessageType.FINAL_RESULTS: self.handle_final_results,
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

    def get_server_address(self) -> tuple[str | None, int | None]:
        """Gets server IP and port that the client is connected to."""
        if self.client_socket is not None:
            return self.client_socket.getpeername()
        else:
            return None, None

    def connect(self) -> None:
        """Connects to the server set in `server_ip`."""
        if not self.server_ip or not self.nickname:
            raise ValueError("Server IP and nickname must have values")

        # Run in separate thread to avoid freezing UI
        threading.Thread(target=self._connect_and_listen, daemon=True).start()

    def disconnect_client(self) -> None:
        """Disconnect client from the server cleanly, notifying server and logic."""
        if self.client_socket is None:
            return

        try:
            self.jsock.send({"type": ClientMessageType.LEAVE_LOBBY})
        except OSError:
            pass

        self.is_connected = False

        self.client_socket.close()
        self.client_socket = None

    def time_out(self) -> None:
        """Disconnect the client due to a timeout from the watchdog."""
        self.is_connected = False

        try:
            self.client_socket.close()
        except OSError:
            pass

        self.kicked.emit("Connection timed out")

    def listen(self) -> None:
        """Listens for messages from the server."""
        while self.is_connected:
            try:
                msg = self.jsock.recv()
            except socket.timeout:
                continue
            except OSError:
                break
            except ValueError:
                # Invalid JSON data
                self.error_occurred.emit("Invalid message data from server")
                self.disconnect_client()
                break

            # Connection is dead
            if msg is None:
                break

            # No message currently (still alive)
            if msg is False:
                continue

            # Any message from server means connection is still alive
            self.last_server_response_time = time.monotonic()
            self.handle_message(msg)

    def _connect_and_listen(self) -> None:
        """Connects to the server using the host IP and port, and listens for oncoming requests."""
        try:
            # Connect to the server
            self.client_socket = socket.create_connection(
                (self.server_ip, self.port), timeout=CLIENT_CONNECTION_TIMEOUT
            )
            self.client_socket.settimeout(1.0)

            self.jsock.set_socket(self.client_socket)
        except ConnectionRefusedError:
            # Server refused connction
            self.connection_failed.emit(ClientConnectionError.CONNECTION_REFUSED)
            return
        except TimeoutError:
            # Could not connect to server within timeout
            self.connection_failed.emit(ClientConnectionError.TIMEOUT)
            return
        except OSError as e:
            if e.errno in (errno.EHOSTUNREACH, errno.ENETUNREACH):
                # Server is unreachable
                self.connection_failed.emit(ClientConnectionError.UNREACHABLE)

            elif e.errno == errno.EADDRNOTAVAIL:
                # Invalid IP (e.g. 0.0.0.0)
                self.connection_failed.emit(ClientConnectionError.INVALID)

            elif e.errno == errno.ECONNRESET:
                # Connection closed by server
                self.connection_failed.emit(ClientConnectionError.CONNECTION_RESET)

            elif e.errno == errno.ECONNABORTED:
                # Connection aborted
                self.connection_failed.emit(ClientConnectionError.CONNECTION_ABORTED)

            elif e.errno == errno.EACCES:
                # Permission denied
                self.connection_failed.emit(ClientConnectionError.PERMISSION)

            else:
                # Unknown error
                print(f"Error connecting client: {e}")
                self.connection_failed.emit(ClientConnectionError.UNKNOWN)

            return

        self.is_connected = True

        # Start listening for server pings and ensure connection remains through watchdog
        threading.Thread(target=self.listen, daemon=True).start()

        # Inform server of join and reset server ping time
        self.send_join()
        self.last_server_response_time = time.monotonic()

        threading.Thread(target=self._ping_loop, daemon=True).start()
        threading.Thread(target=self._watchdog_loop, daemon=True).start()

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
            # Prevent constant checking
            time.sleep(1)

            # If difference between now and last ping time exceeds response timeout, disconnect client
            if time.monotonic() - self.last_server_response_time > RESPONSE_TIMEOUT:
                self.time_out()
                break

    def handle_message(self, msg: dict) -> None:
        """Handles a message from the server by delegating it to a respective handler."""
        msg_type = msg.get("type")

        # No message type; client cannot delegate it
        if msg_type is None:
            self.error_occurred.emit("Missing message type in data")
            self.disconnect_client()
            return

        handler = self.handlers.get(msg_type)

        # Message type does not have a respective handler
        if handler is None:
            print(f"Unknown message type: {msg_type}")
            return

        try:
            handler(msg)
        except KeyError as e:
            # If the handler tries accessing data that does not exist, assume server sent invalid data
            self.error_occurred.emit("Missing fields in data")
            self.disconnect_client()

            print(f"Missing field: {e}")
            return

    def get_data_fields(self, msg: dict, field_names: list[str]) -> dict | None:
        """Get fields from the 'data' of a message from the server, validating it.
        If `field_names` is empty, returns the data dictionary itself."""
        data = msg.get("data")

        if not isinstance(data, dict):
            self.error_occurred.emit("Invalid message data from server")
            self.disconnect_client()
            return None

        if not field_names:
            return data

        fields = {}

        for field_name in field_names:
            field = data.get(field_name)

            if field is None:
                self.error_occurred.emit(
                    f"Missing required field from server: {field_name}"
                )
                self.disconnect_client()
                return None

            fields[field_name] = field

        return fields

    def handle_connection_successful(self, msg: dict) -> None:
        """Handles the `CONNECTION_SUCCESSFUL` message type. Sets player ID."""
        data_fields = self.get_data_fields(msg, ["player_id", "player_list"])
        if data_fields is None:
            return

        player_id = data_fields.get("player_id")
        player_list = data_fields.get("player_list")

        self.player_id = player_id
        self.connected.emit(player_list)

    def handle_player_joined(self, msg: dict) -> None:
        """Handles the `PLAYER_JOINED` message type."""
        data_fields = self.get_data_fields(msg, ["nickname"])
        if data_fields is None:
            return

        nickname = data_fields.get("nickname")
        self.player_joined.emit(nickname)

    def handle_player_left(self, msg: dict) -> None:
        """Handles the `PLAYER_LEFT` message type."""
        data_fields = self.get_data_fields(msg, ["nickname"])
        if data_fields is None:
            return

        nickname = data_fields.get("nickname")
        self.player_left.emit(nickname)

    def handle_countdown_started(self, msg: dict) -> None:
        """Handles the `COUNTDOWN_STARTED` message type."""
        data_fields = self.get_data_fields(msg, ["duration"])
        if data_fields is None:
            return

        duration = data_fields.get("duration")
        self.countdown_started.emit(duration)

    def handle_question_data(self, msg: dict) -> None:
        """Handles the `QUESTION_DATA` message type."""
        data = self.get_data_fields(msg, [])
        self.question_received.emit(data)

    def handle_results(self, msg: dict) -> None:
        """Handles the `RESULTS` message type."""
        data = self.get_data_fields(msg, [])
        self.results_received.emit(data)

    def handle_final_results(self, msg: dict) -> None:
        """Handles the `FINAL_RESULTS` message type. Disconnects the client from the server."""
        data = self.get_data_fields(msg, [])
        self.final_results_received.emit(data)

        self.disconnect_client()

    def handle_kick(self, msg: dict) -> None:
        """Handles the `KICK` message type. Disconnects the client."""
        data_fields = self.get_data_fields(msg, ["reason"])
        if data_fields is None:
            return

        reason = data_fields.get("reason")
        self.kicked.emit(reason)

        self.disconnect_client()

    def handle_error(self, msg: dict) -> None:
        """Handles the `ERROR` message type. Disconnects the client."""
        data_fields = self.get_data_fields(msg, ["reason"])
        if data_fields is None:
            return

        reason = data_fields.get("reason")
        self.error_occurred.emit(reason)

        self.disconnect_client()

    def handle_invalid_action(self, msg: dict) -> None:
        """Handles the `INVALID_ACTION` message type."""
        data_fields = self.get_data_fields(msg, ["reason"])
        if data_fields is None:
            return

        reason = data_fields.get("reason")
        self.invalid_action_occurred.emit(reason)

    def send_join(self) -> None:
        """Sends a `JOIN_LOBBY` message type. Sends nickname to server."""
        self.jsock.send(
            {"type": ClientMessageType.JOIN_LOBBY, "data": {"nickname": self.nickname}}
        )

    def send_answer_submit(self, index: int) -> None:
        """Sends a `ANSWER_SUBMIT` message type. Sends selected answer index to server."""
        self.jsock.send(
            {"type": ClientMessageType.ANSWER_SUBMIT, "data": {"selected_index": index}}
        )
