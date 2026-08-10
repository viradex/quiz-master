"""
game_client.py

Contains the main game client for the application, sitting between the PyQt logic and remote
game server.
"""

import errno
import socket
import threading
import time
from collections.abc import Callable

from PyQt6.QtCore import QObject, pyqtSignal

from core.app.enums import ClientConnectionError
from core.config.constants import (
    CLIENT_CONNECTION_TIMEOUT,
    MAX_NICKNAME_LENGTH,
    PORT,
    RESPONSE_TIMEOUT,
)
from core.services.network.transport import JSONSocket
from core.services.network.types import ClientMessageType, ServerMessageType
from utils.networking import is_valid_ipv4


class GameClient(QObject):
    """
    Manages the game client, which communicates with the server on behalf of the player, managing networking
    and communication with the logic of the application. The client is largely reactive and relies on the current
    game state as well as other details provided from the server only as the only reliable source of truth.

    This class communicates with the logic via signals, ensuring decoupling and preventing the class from knowing
    about the logic/UI of the rest of the application. The logic can and should communicate with this class by
    using public API methods. Inherits `QObject` to allow support for `pyqtSignal`.

    This class uses threads to allow multiple blocking processes to run simultaneously.

    Attributes:
        connected: A `pyqtSignal` that emits when the client successfully connects to the server. The current
            lobby state, or player list, is provided as an argument, as a list of strings. A list is used as
            it groups the similar values together.

        connection_failed: A `pyqtSignal` that emits when the client fails to establish a TCP connection to
            the server. The error that caused the connection to fail is provided as an argument to identify
            the issue, as a ClientConnectionError enum, for better type checking than a regular string.

        player_joined: A `pyqtSignal` that emits when another player joins the server. The new player's
            nickname is provided as an argument, as a string as that represents the nickname in characters.

        player_left: A `pyqtSignal` that emits when another player leaves the server. The player's nickname
            is provided as an argument, as a string as that represents the nickname in characters.

        rtt_updated: A `pyqtSignal` that emits when the client receives an RTT (round-trip time) update
            from the server. The time taken to communicate to the server and back is provided as an argument
            stored as a float, representing the number of milliseconds taken, with decimal precision, or None
            if no time has been calculated yet.

        countdown_started: A `pyqtSignal` that emits when the server notifies that a question countdown has
            started, prior to sending the question data itself. The duration of the countdown in seconds
            is provided as an argument, and represented as an integer, as there is no need for decimal
            precision.

        question_received: A `pyqtSignal` that emits when the server notifies that a question has begun,
            and is now accepting answer submissions. The data required to display the question to the UI
            is provided as an argument as a dictionary, which can be converted into a QuestionPayload.

        results_received: A `pyqtSignal` that emits when the server notifies that a question has ended,
            and is no longer accepting answer submissions. The data required to display the question
            results to the UI is provided as an argument as a dictionary, which can be converted into a
            ClientResultsPayload.

        final_results_received: A `pyqtSignal` that emits when the server notifies that the quiz game has
            ended, and will no longer send any data, meaning the client can safely disconnect from the
            server. The data required to display the final results to the UI is provided as an argument
            as a dictionary, which can be converted into a ClientFinalResultsPayload.

        kicked: A `pyqtSignal` that emits when the server deliberately kicks and disconnects the current
            client from the server, or the client decides to disconnect from the server but does not consider
            it to be a severe error (for example, a timeout). The reason is provided as an argument as a
            string since it can represent a long amount of varied characters.

        error_occurred: A `pyqtSignal` that emits when the server deliberately kicks and disconnects the
            client from the server, or the client disconnects from the server. This can happen due to a
            protocol error on either the client-side or server-side. The first argument provided is the
            reason for the error, and the second argument is the side that terminated the connection (not
            the side that the error occurred on), which can be either "client" or "server" as a string.

        invalid_action_occurred: A `pyqtSignal` that emits when the server detects the client sending
            information at an incorrect time, or providing incorrect data, but one that does not warrant
            a disconnection. For example, if the client attempts to submit an answer after the timer has
            ended. The reason is provided as an argument as a string since it can represent a long amount
            of varied characters.
    """

    # Player list
    connected = pyqtSignal(list)
    connection_failed = pyqtSignal(ClientConnectionError)

    # Player name (for both)
    player_joined = pyqtSignal(str)
    player_left = pyqtSignal(str)

    # Round-trip time time in milliseconds, or None
    # The object type is used to allow both a float and None
    rtt_updated = pyqtSignal(object)

    # Countdown duration (seconds)
    countdown_started = pyqtSignal(int)

    # Question payload
    question_received = pyqtSignal(dict)

    # Results payload
    results_received = pyqtSignal(dict)

    # Final results payload
    final_results_received = pyqtSignal(dict)

    # Reason (for all below)
    # The error_occurred second argument is either 'client' or 'server
    kicked = pyqtSignal(str)
    error_occurred = pyqtSignal(str, str)
    invalid_action_occurred = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()

        # Server information required for establishing a connection
        self.server_ip: str = ""
        self.port: int = PORT

        # Connection state flag, for connection-based loops
        self.is_connected: bool = False

        # Allows sending and receiving messages through a dictionary interface
        self.jsock = JSONSocket()

        # TCP socket
        self.client_socket: socket.socket | None = None

        # Nickname (from client)
        self.nickname: str | None = None

        # Last monotonic time the client detected a message from the server, for watchdog
        self.last_server_message_time: float | None = None

        # Handlers for incoming server messages, that are redirected to a handler
        # method. Instead of using 'if' statements, this allows the dispatch table
        # to look cleaner and be easily extendable.
        self.handlers: dict[ServerMessageType, Callable[[dict], None]] = {
            ServerMessageType.PING: self._handle_ping,
            ServerMessageType.CONNECTION_SUCCESSFUL: self._handle_connection_successful,
            ServerMessageType.PLAYER_JOINED: self._handle_player_joined,
            ServerMessageType.PLAYER_LEFT: self._handle_player_left,
            ServerMessageType.COUNTDOWN_STARTED: self._handle_countdown_started,
            ServerMessageType.QUESTION_DATA: self._handle_question_data,
            ServerMessageType.RESULTS: self._handle_results,
            ServerMessageType.FINAL_RESULTS: self._handle_final_results,
            ServerMessageType.KICK: self._handle_kick,
            ServerMessageType.ERROR: self._handle_error,
            ServerMessageType.INVALID_ACTION: self._handle_invalid_action,
        }

    def set_ip_address(self, ip: str) -> None:
        """
        Sets the IP address of the server to connect to. The IP address must be a valid IPv4 address. The
        'localhost' address is permitted. Does not connect to the server.

        Arguments:
            ip: The IP to set the server IP to for when the client wishes to connect to the server. A string
                is used as it can represent an IPv4 address well.

        Returns:
            None.

        Raises:
            ValueError: If the IP address was not a valid IPv4 address.
        """
        if not is_valid_ipv4(ip, allow_localhost=True):
            raise ValueError(f"IP '{ip}' is not a valid IPv4 address")

        self.server_ip = ip

    def set_nickname(self, nickname: str) -> None:
        """
        Sets the player nickname to connect with. The nickname provided must not be empty, and not exceed
        the maximum number of characters permitted.

        Arguments:
            nickname: The nickname to represent the player with when connecting to the server. A string is
                used as it can easily represent a nickname of any characters, including emojis.

        Returns:
            None.

        Raises:
            ValueError: If the nickname is empty or exceeds the maximum number of characters permitted for
                the nickname.
        """
        if not nickname or len(nickname) > MAX_NICKNAME_LENGTH:
            raise ValueError(
                f"Nickname '{nickname}' must not be empty or exceed {MAX_NICKNAME_LENGTH} characters"
            )

        self.nickname = nickname

    def get_server_address(self) -> tuple[str, int] | None:
        """
        Gets the server IP and port that the client is currently connected to, or None if the client is
        currently not connected to any server yet.

        Returns:
            A tuple containing the IP address of the server, and the port that it is connected to, in that
            order. If the client is not connected to a server yet, None is returned instead. Otherwise, the IP
            address is a string and the port is an integer.
        """
        if self.client_socket is None:
            return None
        else:
            return self.client_socket.getpeername()

    def connect(self) -> None:
        """
        Attempts a connection to the remote server as specified in the server IP and constant port. Requires
        the server IP and nickname to have already been set via `set_ip_address()` and `set_nickname()`,
        respectively. The client then attempts a connection, and if successful, begins listening for messages
        from the server.

        Returns:
            None.

        Raises:
            ValueError: If the server IP and/or the nickname were not set prior to running this method.
        """
        if not self.server_ip or not self.nickname:
            raise ValueError("Both the server IP and nickname must have values")

        # Run in separate thread to avoid freezing UI
        threading.Thread(target=self._connect_and_listen, daemon=True).start()

    def disconnect_client(self) -> None:
        """
        Performs a clean disconnection from the server, by attempting to notify the server that the player
        is leaving before closing the TCP connection. Also stops background loops and resets the socket.
        If this method is called without the socket existing, nothing happens.

        Returns:
            None.
        """
        # This method is called disconnect_client() rather than just disconnect()
        # due to QObject already having a disconnect() method.
        if self.client_socket is None:
            return

        try:
            # Attempts to tell the server it is leaving, if possible
            self.jsock.send({"type": ClientMessageType.LEAVE_LOBBY})
        except OSError:
            pass

        # Stops background loops
        self.is_connected = False

        # Close TCP socket and reset
        self.client_socket.close()
        self.client_socket = None

    def _connect_and_listen(self) -> None:
        """
        Internal method. Attempts to establish a connection to the remote TCP server using the provided
        server IP and constant port, and, if successful, begins listening from oncoming messages and starts
        the server watchdog in dedicated background threads. If the connection fails, emits the connection
        failed signal with the reason of failure.

        This method should be run in a background thread to prevent freezing the main GUI loop, as some of
        its function calls are blocking.

        Returns:
            None.
        """
        try:
            # Connect to the server using TCP
            self.client_socket = socket.create_connection(
                (self.server_ip, self.port), timeout=CLIENT_CONNECTION_TIMEOUT
            )

            # Add a timeout to ensure the message listening loop can periodically
            # check if the is_connected flag is still True.
            self.client_socket.settimeout(1.0)

            # Allows JSONSocket's send() and recv() to work now
            self.jsock.set_socket(self.client_socket)
        except ConnectionRefusedError:
            # Server was reachable but nothing accepted the connection on the port
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
                # Connection was forcibly reset
                self.connection_failed.emit(ClientConnectionError.CONNECTION_RESET)
            elif e.errno == errno.ECONNABORTED:
                # Connection aborted
                self.connection_failed.emit(ClientConnectionError.CONNECTION_ABORTED)
            elif e.errno == errno.EACCES:
                # OS refused connection
                self.connection_failed.emit(ClientConnectionError.PERMISSION)
            else:
                # Unknown error
                print(f"Error connecting client: {e}")
                self.connection_failed.emit(ClientConnectionError.UNKNOWN)

            return

        self.is_connected = True

        # Start listening for server messages and monitor server availability
        threading.Thread(target=self._listen, daemon=True).start()

        # Inform server of join
        self.jsock.send(
            {"type": ClientMessageType.JOIN_LOBBY, "data": {"nickname": self.nickname}}
        )

        # Reset last server ping time
        self.last_server_message_time = time.monotonic()

        # Continuously check server connection health, and if the server stops
        # responding, disconnects client.
        threading.Thread(target=self._watchdog_loop, daemon=True).start()

    def _listen(self) -> None:
        """
        Internal method. Constantly listens for incoming messages from the server, and handles the states
        appropriately. If the server sends invalid data such as invalid JSON data or a message too large,
        the client will immediately disconnect for safety. If the connection is detected to be a dead
        connection, the receive loop ends as well. If the connection times out, the loop continues.

        This method should be run in a background thread to prevent freezing the main GUI loop, as its `recv()`
        calls are blocking.

        Returns:
            None.
        """
        while self.is_connected:
            try:
                # Repeatedly tries receiving a message from the server
                msg = self.jsock.recv()
            except (ValueError, TypeError) as e:
                # Invalid JSON or UTF-8 received, message too large, or not a dictionary
                self.error_occurred.emit(f"Invalid message: {e}", "client")
                self.disconnect_client()
                break

            # Connection is dead
            # Do not show any sort of disconnection screen here, otherwise the
            # client will show it when manually disconnecting.
            if msg is None:
                break

            # Timeout received
            if msg is False:
                continue

            # Any message from server means connection is still alive.
            # Use time.monotonic() rather than time.time() to avoid daylight
            # savings time and NTP changes, which can confuse the client.
            self.last_server_message_time = time.monotonic()
            self._handle_message(msg)

    def _watchdog_loop(self) -> None:
        """
        Internal method. Every second, if the client is currently connected, checks the time since the server
        last sent a message to the server compared to the current time. If the duration exceeds the maximum
        time before the server is considered 'dead', the client assumes the server has stopped responding and
        disconnects the client through a timeout.

        This method should be run in a background thread to prevent freezing the main GUI loop, as some of
        its function calls are blocking.

        Returns:
            None.
        """
        while self.is_connected:
            # Prevent constant checking
            time.sleep(1)

            # If difference between now and last ping time exceeds response timeout, disconnect client
            if (
                self.last_server_message_time is not None
                and time.monotonic() - self.last_server_message_time > RESPONSE_TIMEOUT
            ):
                self._timeout()
                break

    def _timeout(self) -> None:
        """
        Internal method. Disconnects the client from the server without explicitly notifying the server, when
        the server has not responded within a certain timeframe. Intended to be called from the watchdog itself.
        Notifies the client of the disconnection through a "kick" message. Does nothing if the socket is not set.

        Returns:
            None.
        """
        if self.client_socket is None:
            return

        # Stops background loops
        self.is_connected = False

        try:
            self.client_socket.close()
        except OSError:
            pass

        self.client_socket = None

        # Use a kick to show the disconnection screen, even though the server
        # didn't really kick the client; the client kicked itself.
        self.kicked.emit("Connection timed out")

    def _handle_message(self, msg: dict) -> None:
        """
        Internal method. Acts as the central message dispatcher by identifying messages sent by the server to
        this client based on the message type provided. Based on the message type, a certain handler is called
        to delegate the specific message to.

        The message type passed should be the dictionary directly provided by the server. The root 'type' key
        is used to identify the type of message, and if it is missing, the client immediately disconnects as
        a safeguard. If the message type could not be recognized, it is simply ignored to allow for forward
        compatibility. If all message type checks pass, the entire message, including the 'type' key, is
        passed onto the specific handler for that particular message type. No other data fields are validated.

        Arguments:
            msg: The message passed directly from the message given by the server, including the mandatory
                'type' key and optional 'data' key that contains any and all data needed for the request or
                message. A dictionary is used as it allows the JSON to be easily converted, and can store
                multiple keyed values together.

        Returns:
            None.
        """
        msg_type = msg.get("type")

        # No message type means a protocol violation, as the client cannot delegate it
        if msg_type is None:
            self.error_occurred.emit("Missing message type in data", "client")
            self.disconnect_client()
            return

        handler = self.handlers.get(msg_type)

        # Message type does not have a respective handler, meaning it is of an
        # unknown type. Unknown message types are ignored for forward compatibility.
        if handler is None:
            return

        try:
            handler(msg)
        except KeyError:
            # If the handler tries accessing data that does not exist, assume
            # server sent invalid data. This should be largely prevented by
            # _get_data_fields(), however, so this is here largely as a defensive
            # check.
            self.error_occurred.emit("Missing fields in data", "client")
            self.disconnect_client()
            return

    def _get_data_fields(
        self, msg: dict, field_names: tuple[str, ...], empty_allowed: bool = False
    ) -> dict | None:
        """
        Internal method. Used as a helper to get certain field names from the full message provided by the
        server. The message provided should be the full, unmodified dictionary from the server, including
        the mandatory 'type' and 'data' keys. It is assumed that, if this method is being called, the 'data'
        key is meant to be provided by the server. Otherwise, the client will be unfairly disconnected.

        The field names requested are searched for within the 'data' key dictionary, unless none are provided.
        If the 'data' key is not a dictionary, it is treated as a protocol violation and the client is
        disconnected. Otherwise, the field names are retrieved and returned as a dictionary after being validated.
        If the field names are empty, the entire 'data' raw dictionary is provided from the server without being
        validated. If a field name was not provided in the 'data' dictionary, the client is disconnected, unless
        `empty_allowed` is set to True, in which case it will be set to None if the key could not be found.

        Arguments:
            msg: The message passed directly from the message given by the server, including the 'type' key and
                'data' key. The 'data' key is expected to exist in this message. A dictionary is used as that
                is what is directly provided by the message handler.

            field_names: A tuple of any length containing strings describing the names of keys within the root
                'type' key of the message dictionary that are expected and wanted to be extracted. If the tuple
                provided is empty (useful for more complex payloads, or payloads that will be turned into a
                data transfer object), the entire data segment of the dictionary is returned without any
                validation of the values within. The strings must match the casing and spelling of the expected
                keys provided by the server exactly. A tuple is used as it signifies immutability, and a string
                is used as that is the same type for the keys of the data dictionary.

            empty_allowed: Whether empty, or None, values are allowed for the keys in the 'data' dictionary. In
                other words, if this is set to True, validation is skipped on all keys provided in `field_names`,
                and if the key does not exist, it is set to None and returned. Defaults to False, where strict
                validation is enabled and missing keys and/or keys set to None are treated as a protocol
                violation.

        Returns:
            The dictionary containing all the data requested from `field_names`, with each data being identified
            by a key of the same name as provided in the fields requested. If the message provided did not pass
            validation checks, None is returned.
        """
        data = msg.get("data")

        # Requires data to be a dictionary, even if it's just one value. If it
        # isn't a dictionary, it is treated as a protocol violation on part of
        # the server and the client is disconnected for safety.
        if not isinstance(data, dict):
            self.error_occurred.emit("Invalid message data from server", "client")
            self.disconnect_client()
            return None

        # If no field names were directly specified, returns whole data dictionary
        if not field_names:
            return data

        fields = {}

        for field_name in field_names:
            field = data.get(field_name)

            # Only treats it as a protocol violation if empty values are disallowed
            if not empty_allowed and field is None:
                self.error_occurred.emit(
                    f"Missing required field: {field_name}", "client"
                )
                self.disconnect_client()
                return None

            # Makes new fields dictionary rather than returning data dictionary
            # to allow values not provided to be set to None if empty_allowed.
            fields[field_name] = field

        return fields

    def _handle_ping(self, msg: dict) -> None:
        """
        Internal method. A handler method for handling the `PING` message type from the server.

        Retrieves the RTT (round-trip time) from the message and emits it as a signal, then return-sends a
        `PONG` to the server to notify that the client is still alive.

        Arguments:
            msg: The message passed directly from the message given by the server, including the 'type' key and
                'data' key. A dictionary is used as that is what is directly provided by the message handler.

        Returns:
            None.
        """
        # Allows the RTT to be None, meaning no value calculated yet
        data_fields = self._get_data_fields(msg, ("rtt",), empty_allowed=True)
        if data_fields is None:
            return

        # Informs UI of new RTT
        rtt = data_fields.get("rtt")
        self.rtt_updated.emit(rtt)

        try:
            # Attempts to send a PONG to notify the server that the client is alive
            self.jsock.send({"type": ClientMessageType.PONG})
        except OSError:
            self.error_occurred.emit("Failed to respond to server ping", "client")
            self.disconnect_client()

    def _handle_connection_successful(self, msg: dict) -> None:
        """
        Internal method. A handler method for handling the `CONNECTION_SUCCESSFUL` message type from the server.

        Retrieves the current player list at the time of joining, including the current player in the player
        list, to display in the UI.

        Arguments:
            msg: The message passed directly from the message given by the server, including the 'type' key and
                'data' key. A dictionary is used as that is what is directly provided by the message handler.

        Returns:
            None.
        """
        data_fields = self._get_data_fields(msg, ("player_list",))
        if data_fields is None:
            return

        # Informs UI of current player list at time of joining for a starting value
        player_list = data_fields.get("player_list")
        self.connected.emit(player_list)

    def _handle_player_joined(self, msg: dict) -> None:
        """
        Internal method. A handler method for handling the `PLAYER_JOINED` message type from the server.

        Retrieves the nickname of the player that joined, to allow displaying it in the lobby screen UI.

        Arguments:
            msg: The message passed directly from the message given by the server, including the 'type' key and
                'data' key. A dictionary is used as that is what is directly provided by the message handler.

        Returns:
            None.
        """
        data_fields = self._get_data_fields(msg, ("nickname",))
        if data_fields is None:
            return

        # Informs UI of nickname of the player who joined
        nickname = data_fields.get("nickname")
        self.player_joined.emit(nickname)

    def _handle_player_left(self, msg: dict) -> None:
        """
        Internal method. A handler method for handling the `PLAYER_LEFT` message type from the server.

        Retrieves the nickname of the player that left, to allow removing it from the lobby screen UI.

        Arguments:
            msg: The message passed directly from the message given by the server, including the 'type' key and
                'data' key. A dictionary is used as that is what is directly provided by the message handler.

        Returns:
            None.
        """
        data_fields = self._get_data_fields(msg, ("nickname",))
        if data_fields is None:
            return

        # Informs UI of nickname of the player who left
        nickname = data_fields.get("nickname")
        self.player_left.emit(nickname)

    def _handle_countdown_started(self, msg: dict) -> None:
        """
        Internal method. A handler method for handling the `COUNTDOWN_STARTED` message type from the server.

        Retrieves the duration of the countdown in seconds and informs the UI to begin a countdown, which is
        typically prior to a question starting.

        Arguments:
            msg: The message passed directly from the message given by the server, including the 'type' key and
                'data' key. A dictionary is used as that is what is directly provided by the message handler.

        Returns:
            None.
        """
        data_fields = self._get_data_fields(msg, ("duration",))
        if data_fields is None:
            return

        # Informs UI that countdown has begun, while giving duration in seconds
        duration = data_fields.get("duration")
        self.countdown_started.emit(duration)

    def _handle_question_data(self, msg: dict) -> None:
        """
        Internal method. A handler method for handling the `QUESTION_DATA` message type from the server.

        Retrieves the question data required to display the question to the UI. The message data does not have
        its required fields extracted here, as it is converted into a specialized payload object further on.

        Arguments:
            msg: The message passed directly from the message given by the server, including the 'type' key and
                'data' key. A dictionary is used as that is what is directly provided by the message handler.

        Returns:
            None.
        """
        # Get entire 'data' key from message dictionary rather than only some values
        data = self._get_data_fields(msg, ())
        if data is None:
            return

        # Informs UI of raw question data as dictionary
        self.question_received.emit(data)

    def _handle_results(self, msg: dict) -> None:
        """
        Internal method. A handler method for handling the `RESULTS` message type from the server.

        Retrieves the question results data required to display the results to the UI. The message data does
        not have its required fields extracted here, as it is converted into a specialized payload object
        further on.

        Arguments:
            msg: The message passed directly from the message given by the server, including the 'type' key and
                'data' key. A dictionary is used as that is what is directly provided by the message handler.

        Returns:
            None.
        """
        # Get entire 'data' key from message dictionary rather than only some values
        data = self._get_data_fields(msg, ())
        if data is None:
            return

        # Informs UI of raw results data as dictionary
        self.results_received.emit(data)

    def _handle_final_results(self, msg: dict) -> None:
        """
        Internal method. A handler method for handling the `FINAL_RESULTS` message type from the server.

        Retrieves the final results data required to display the final results to the UI. The message data does
        not have its required fields extracted here, as it is converted into a specialized payload object
        further on.

        After obtaining the data, the client manually disconnects from the server as the game is over, and the
        server nor the client need to transfer any further information. Without a manual disconnection, the server
        would kick the player when the game finishes.

        Arguments:
            msg: The message passed directly from the message given by the server, including the 'type' key and
                'data' key. A dictionary is used as that is what is directly provided by the message handler.

        Returns:
            None.
        """
        # Get entire 'data' key from message dictionary rather than only some values
        data = self._get_data_fields(msg, ())
        if data is None:
            return

        # Informs UI of raw final results data as dictionary, then closes client
        self.final_results_received.emit(data)
        self.disconnect_client()

    def _handle_kick(self, msg: dict) -> None:
        """
        Internal method. A handler method for handling the `KICK` message type from the server.

        Retrieves the reason for the kick that the server provided, and informs the UI of the kick. Disconnects
        from the server manually afterwards, though the server typically already does this. A kick is typically
        done for regular issues that the client can encounter, such as joining when the lobby is full.

        Arguments:
            msg: The message passed directly from the message given by the server, including the 'type' key and
                'data' key. A dictionary is used as that is what is directly provided by the message handler.

        Returns:
            None.
        """
        data_fields = self._get_data_fields(msg, ("reason",))
        if data_fields is None:
            return

        # Informs UI of kick with reason
        reason = data_fields.get("reason")
        self.kicked.emit(reason)

        # Disconnects client if, for some reason, the server hasn't disconnected the client yet
        self.disconnect_client()

    def _handle_error(self, msg: dict) -> None:
        """
        Internal method. A handler method for handling the `ERROR` message type from the server.

        Retrieves the reason for the error disconnection that the server provided, and informs the UI of the
        disconnection. Disconnects from the server manually afterwards, though the server typically already does this.
        An error is a sign of a protocol violation by the client and should not happen in regular usage.

        Arguments:
            msg: The message passed directly from the message given by the server, including the 'type' key and
                'data' key. A dictionary is used as that is what is directly provided by the message handler.

        Returns:
            None.
        """
        data_fields = self._get_data_fields(msg, ("reason",))
        if data_fields is None:
            return

        # Informs UI of error disconnection with reason
        reason = data_fields.get("reason")
        self.error_occurred.emit(reason, "server")

        # Disconnects client if, for some reason, the server hasn't disconnected the client yet
        self.disconnect_client()

    def _handle_invalid_action(self, msg: dict) -> None:
        """
        Internal method. A handler method for handling the `INVALID_ACTION` message type from the server.

        Retrieves the reason for the invalid reason that the server provided, and informs the UI of this. The
        invalid action does not disconnect the client from the server, which is the key distinction between this
        and `ERROR`. This typically happens if the request is valid according to the protocol, but is no longer
        valid at this time (e.g. submitting an answer too late).

        Arguments:
            msg: The message passed directly from the message given by the server, including the 'type' key and
                'data' key. A dictionary is used as that is what is directly provided by the message handler.

        Returns:
            None.
        """
        data_fields = self._get_data_fields(msg, ("reason",))
        if data_fields is None:
            return

        # Informs UI of invalid action with reason
        reason = data_fields.get("reason")
        self.invalid_action_occurred.emit(reason)

    def send_answer_submit(self, index: int) -> None:
        """
        Sends an `ANSWER_SUBMIT` message type to the server, with the chosen answer index as a part of the
        data. The index is not validated before sending.

        This should be sent when the client wishes to submit an answer while a question is ongoing. Submitting
        an answer after the valid time will be rejected by the server, but this method does not enforce timing.

        Arguments:
            index: A zero-based integer index for the answer that the player wishes to submit for the current
                question, respective to the answer options. An integer is used as that is used for indexes in
                iterables, for example.

        Returns:
            None.
        """
        self.jsock.send(
            {"type": ClientMessageType.ANSWER_SUBMIT, "data": {"selected_index": index}}
        )
