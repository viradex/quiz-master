"""
game_server.py

Contains the main game server for the application, sitting between the PyQt logic, game logic, and
remote game clients.
"""

import errno
import socket
import threading
import time
from collections.abc import Callable

from PyQt6.QtCore import QObject, pyqtSignal

from core.app.enums import AddPlayerResult, ServerStartingError
from core.config.constants import CLIENT_PING_INTERVAL, PORT, RESPONSE_TIMEOUT
from core.services.network.connected_client import ConnectedClient
from core.services.network.player_registry import PlayerRegistry
from core.services.network.types import ClientMessageType, ServerMessageType
from models.player import Player


class GameServer(QObject):
    """
    Manages the game server, communicating with multiple clients simultaneously and listening for messages from
    each, while also managing the TCP server, player management, heartbeats, watchdog, and disconnects. Enforces
    strict validation from clients, as theoretically any external client with the server IP address can connect
    to the server, even if it isn't the official client. Poor validation can crash the server, therefore it is
    important that every bit of data from the client is untrusted. This includes, for example, the time taken
    to submit an answer, which the client can easily modify themselves if the server only relied on that, which
    is why the server calculates it itself. Even an honest client can be buggy or send corrupt data. In other
    words, the server should be treated as the single source of truth and should **never trust the client**;
    the server is authoritative!

    This class communicates with the logic via signals, ensuring decoupling and preventing the class from knowing
    about the logic/UI of the rest of the application. The game server also does not manage or know about the
    actual quiz or game rules, nor does it manage it. The logic can and should communicate with this class by
    using public API methods. Inherits `QObject` to allow support for `pyqtSignal`.

    This class uses threads to allow multiple blocking processes to run simultaneously.

    Attributes:
        started: A `pyqtSignal` that emits when the server successfully starts and begins listening for
            incoming requests and connections. No arguments are provided.

        start_failed: A `pyqtSignal` that emits when the server fails to start a TCP server. The error that
            caused the starting procedure to fail is provided as an argument to identify the issue, as a
            ServerStartingError enum, for better type checking than a regular string.

        player_joined: A `pyqtSignal` that emits when a player joins the server. The new player's nickname
            is provided as an argument, as a string as that represents the nickname in characters.

        player_left: A `pyqtSignal` that emits when a player leaves the server. The player's nickname is
            provided as an argument, as a string as that represents the nickname in characters.

        rtt_updated: A `pyqtSignal` that emits when the RTT (round-trip time) of a client has an updated value.
            The new round-trip time calculated, along with the player ID as the first argument, is provided
            as a float as the second argument in milliseconds. A float is used to allow for decimal precision.

        answer_submitted: A `pyqtSignal` that emits when a player submits an answer during an ongoing game.
            The signal is emitted only if there is a game going on, but it can be emitted during any stage of
            the game, since the GameClient is unaware of the concept of different 'game stages'. The first
            argument is a string containing the player ID of the player who submitted the answer, being a string
            as it can flexibly store IDs and can store many characters to make them more unique. The second
            argument is the answer index selected, as a zero-based index. An integer is used as it naturally
            corresponds to a position in an iterable as a whole number. The final argument is the time that
            the player submitted the answer at, calculated on the server-side when the request is received,
            as a server-side monotonic time. This is not the time taken. A float is used as the monotonic time
            returns a float and allows for greater accuracy.
    """

    started = pyqtSignal()
    start_failed = pyqtSignal(ServerStartingError)

    # Player ID, nickname
    player_joined = pyqtSignal(str, str)
    player_left = pyqtSignal(str, str)

    # Player ID, round-trip time in milliseconds
    rtt_updated = pyqtSignal(str, float)

    # Player ID, answer index, time submitted (monotonic server-side)
    answer_submitted = pyqtSignal(str, int, float)

    def __init__(self) -> None:
        super().__init__()

        # Server information required for starting the server. The IP address
        # '0.0.0.0' listens to all available network interfaces (a wildcard).
        self.host_ip: str = "0.0.0.0"
        self.port: int = PORT

        # Whether the server is currently running
        self.is_running: bool = False

        # Whether the quiz game has started or not. The server knows no further state than this.
        self.game_started: bool = False

        # TCP socket
        self.server_socket: socket.socket | None = None

        # Delegates managing players in a thread-safe manner
        self.registry = PlayerRegistry()

        # Handlers for incoming client messages, that are redirected to a handler
        # method. Instead of using 'if' statements, this allows the dispatch table
        # to look cleaner and be easily extendable.
        self.handlers: dict[
            ClientMessageType, Callable[[ConnectedClient, dict], None]
        ] = {
            ClientMessageType.PONG: self._handle_pong,
            ClientMessageType.JOIN_LOBBY: self._handle_join_lobby,
            ClientMessageType.LEAVE_LOBBY: self._handle_leave_lobby,
            ClientMessageType.ANSWER_SUBMIT: self._handle_answer_submit,
        }

    def get_player(self, player_id: str) -> Player | None:
        """
        Retrieves a Player instance from the registry, while abstracting away the registry for the rest of
        the application.

        Arguments:
            player_id: A string describing the ID of the player to retrieve. A string is used as it can
                flexibly store IDs and can store many characters to make them more unique.

        Returns:
            The Player instance identified by the player ID, or None if the player could not be found.
        """
        session = self.registry.get(player_id)
        if session is None:
            return None

        return session.player

    def get_total_players(self) -> int:
        """
        Calculates the total number of players currently connected to the server and registered as a valid
        player, not just a client connection.

        Returns:
            The total number of players connected to the server, as an integer. An integer is used to allow
            for simpler calculations, and because the number of players is a whole number.
        """
        return len(self.registry.get_all())

    def get_client_address(self, client_id: str) -> tuple[str, int] | None:
        """
        Retrieves the address that the client connected from, including the IP address of the client, and
        the ephemeral TCP port of the client (the temporary port number assigned for the connection of the
        client specifically).

        Arguments:
            client_id: A string describing the ID of the client to get the address from. A string is used
                as it can flexibly store IDs and can store many characters to make them more unique.

        Returns:
            A tuple containing the client IP address as the first value, as a string, and the ephemeral TCP
            port as the second value, as an integer. None is returned standalone if the client could not be
            found based on the ID.
        """
        session = self.registry.get(client_id)
        if session is None:
            return None

        return session.client.ip_address, session.client.port

    def get_client_hostname(self, client_id: str) -> str | None:
        """
        Retrieves the hostname of the specified client, retrieved by performing a reverse DNS lookup prior
        to the running of this method. The hostname is retrieved asynchronously before, but if this method
        is called within the short window when the hostname has not been resolved, None is returned instead.

        Arguments:
            client_id: A string describing the ID of the client to get the hostname of. A string is used
                as it can flexibly store IDs and can store many characters to make them more unique.

        Returns:
            The hostname of the client if it was able to be resolved, and was already found prior to running
            the method, as a string since the string can represent the vast array of characters the hostname
            could contain well, or None if the hostname was not found.
        """
        session = self.registry.get(client_id)
        if session is None:
            return None

        return session.client.hostname

    def get_client_rtt(self, client_id: str) -> float | None:
        """
        Retrieves the RTT (round-trip time) of the specified client, if it has already been calculated. The
        most recently measured round-trip time is returned, in milliseconds with decimal precision.

        Arguments:
            client_id: A string describing the ID of the client to get the RTT of. A string is used as it
                can flexibly store IDs and can store many characters to make them more unique.

        Returns:
            The round-trip time of the client that was last calculated in milliseconds, as a float to represent
            the decimal precision of the round-trip time, or None if the RTT has not yet been calculated.
        """
        session = self.registry.get(client_id)
        if session is None:
            return None

        return session.client.rtt_ms

    def start(self) -> None:
        """
        Attempts to start the TCP server and allow clients to begin connecting to it and for the server to
        listen to oncoming messages. Runs the logic in a background thread to prevent freezing the UI while
        waiting for the server to start and waiting for clients to connect.

        Returns:
            None.
        """
        # Usually this wouldn't be in its own function due to only starting
        # a thread, but it provides a cleaner API.
        threading.Thread(target=self._start_and_listen, daemon=True).start()

    def stop(self, reason: str = "Server closed") -> None:
        """
        Stops the server cleanly, by attempting to notify all clients that the server is shutting down for
        the reason provided, before closing all client connections, clearing the player registry, and
        shutting down the server's own TCP socket. Also stops any and all background loops. If this method
        is called without the socket existing, nothing happens.

        Arguments:
            reason: The reason for the server closing, which is broadcast to all clients as the kick reason
                before they are disconnected. A string is used to allow variety in the message sent. Defaults
                to "Server closed".

        Returns:
            None.
        """
        if self.server_socket is None:
            return

        # Get all sessions and store them in memory, then clear the sessions
        sessions = self.registry.get_all().values()
        self.registry.clear()

        # The self._broadcast() method cannot be used for informing all clients
        # of the shutdown, since it itself relies on the player registry, which
        # has been cleared at this point. Even if the clear() method for the
        # registry was placed after the broadcast, some clients may be destroyed
        # before the broadcast can reach the client, causing an inconsistent state.
        # Manually sending the messages and doing a TCP half-close is better.
        for session in sessions:
            try:
                # Set a kick to inform client that the server is shutting down
                session.client.send(
                    {"type": ServerMessageType.KICK, "data": {"reason": reason}}
                )

                # Performs a TCP half-close. SHUT_WR means the server will no longer
                # send any data, but the client can still receive any requests sent.
                session.client.socket.shutdown(socket.SHUT_WR)
            except OSError:
                pass

        # Reset all server state flags
        self.is_running = False
        self.game_started = False

        # Close TCP socket and reset
        self.server_socket.close()
        self.server_socket = None

    def _start_and_listen(self) -> None:
        """
        Internal method. Attempts to start the TCP server, and, if successful, allows clients to begin connecting
        to it. If the starting procedure fails, emits the start failed signal with the reason of failure. Also
        starts the client watchdog and latency checker loops as background threads for when clients begin to
        join.

        This method should be run in a background thread to prevent freezing the main GUI loop, as some of
        its function calls are blocking.

        Returns:
            None.
        """
        try:
            # Start server using TCP
            self.server_socket = socket.create_server((self.host_ip, self.port))
        except OverflowError:
            # Port out of range
            self.start_failed.emit(ServerStartingError.INVALID_PORT)
            return
        except OSError as e:
            if e.errno == errno.EADDRINUSE:
                # Port in use (by an external application or the same program running the server)
                self.start_failed.emit(ServerStartingError.IN_USE)
            elif e.errno == errno.EACCES:
                # Permission denied (e.g. reserved ports 0-1023)
                self.start_failed.emit(ServerStartingError.PERMISSION)
            elif e.errno == errno.EADDRNOTAVAIL:
                # Invalid IP (e.g. non-local IP)
                self.start_failed.emit(ServerStartingError.INVALID_IP)
            elif e.errno == errno.EINVAL:
                # Invalid arguments
                self.start_failed.emit(ServerStartingError.INVALID)
            else:
                # Unknown error
                print(f"Error starting server: {e}")
                self.start_failed.emit(ServerStartingError.UNKNOWN)

            return

        # Inform of server start and set flag
        self.is_running = True
        self.started.emit()

        # Start global watchdog and client latency loop checks as background threads
        threading.Thread(target=self._client_latency_loop, daemon=True).start()
        threading.Thread(target=self._client_watchdog_loop, daemon=True).start()

        # Begin listening for client connections and accepting them
        self._accept_clients()

    def _accept_clients(self) -> None:
        """
        Internal method. Waits for a client to connect to the server, and if and when they do, immediately
        accepts the connection with a new socket representing the client connection. The server then handles
        the new client connection by initializing it and then listening for oncoming messages. The loop stops
        running when the server's is running flag is set to False.

        This method should be run in a background thread to prevent freezing the main GUI loop, as its `accept()`
        calls are blocking.

        Returns:
            None.
        """
        while self.is_running:
            try:
                client, addr = self.server_socket.accept()
            except OSError:
                break

            # Handle each client concurrently in their own thread
            threading.Thread(
                target=self._handle_client, args=(client, addr), daemon=True
            ).start()

    def _client_latency_loop(self) -> None:
        """
        Internal method. Periodically sends `PING` messages to each client to ensure they are still responsive.
        The time the ping was sent is recorded, so that if the client does not respond within a certain
        frame, the watchdog can kick them. The round-trip time of the client is sent to the client along with
        the `PING` message so that they can display the value on their UI, for example. If the server fails to
        send the message, the client is already presumed dead and disconnected from the server.

        This method should be run in a background thread to prevent freezing the main GUI loop, as its `sleep()`
        calls are blocking.

        Returns:
            None.
        """
        while self.is_running:
            # Wait rather than constantly sending PINGs
            time.sleep(CLIENT_PING_INTERVAL)

            for session in self.registry.get_all().values():
                client = session.client

                try:
                    # Using perf_counter() is preferable to monotonic()
                    # for precise elapsed durations.
                    client.last_ping_sent = time.perf_counter()

                    # Send PING and expect a PONG to be returned
                    client.send(
                        {"type": ServerMessageType.PING, "data": {"rtt": client.rtt_ms}}
                    )
                except OSError:
                    # If the server cannot send a message, the client is already presumed dead
                    self._kick_client(client, "Failed to ping client")

    def _client_watchdog_loop(self) -> None:
        """
        Internal method. Checks if the client has responded recently with any message (not just a `PONG`).
        Every second, the watchdog checks all clients to see if they have responded within the maximum response
        timeout. If they have not, they are immediately presumed dead and disconnected from the server.

        This method should be run in a background thread to prevent freezing the main GUI loop, as its `sleep()`
        calls are blocking.

        Returns:
            None.
        """
        while self.is_running:
            # Prevent constant checking
            time.sleep(1)

            for session in self.registry.get_all().values():
                client = session.client

                # If the difference between current time and the last seen time
                # exceeds the maximum response timeout, the client is presumed
                # dead and disconnected.
                if time.monotonic() - client.last_seen > RESPONSE_TIMEOUT:
                    self._kick_client(client, "Client timeout")

    def _broadcast(self, msg: dict) -> None:
        """
        Internal method. Sends a message to every connected player in the registry. If the server fails to
        send the message to a client, that client is immediately disconnected.

        Arguments:
            msg: The dictionary to send to the clients. A dictionary is used as it can store multiple values
                in one data type, and be easily serialized and deserialized into JSON and back.

        Returns:
            None.
        """
        sessions = self.registry.get_all().values()

        for session in sessions:
            client = session.client

            try:
                client.send(msg)
            except OSError:
                # Don't kick here: _kick_client() -> _send_and_disconnect() -> _remove_client() -> _broadcast()
                # Due to it eventually calling _remove_client() which calls _broacast() again.
                continue

    def kick_player(self, player_id: str, reason: str) -> None:
        """
        Kicks a player from the server based on the player ID, sending a kick message to the client with the
        provided reason before disconnecting them. This method only works if the player is stored in the registry.

        Typically, when wanting to kick the player from the server directly, using `_kick_client()` directly
        is a better option, especially if you have the `ConnectedClient`, as it avoids a lookup and works even
        if the player is not yet registered in the player registry.

        Arguments:
            player_id: A string describing the ID of the player to kick. A string is used as it can flexibly
                store IDs and can store many characters to make them more unique.

            reason: The reason for the client being kicked, which is sent to the client before they are
                disconnected. A string is used to allow variety in the message sent.

        Returns:
            None.
        """
        session = self.registry.get(player_id)
        if session:
            self._kick_client(session.client, reason)

    def _remove_client(self, player_id: str) -> None:
        """
        Internal method. Removes a client from the server, without notifying the player that they are being
        kicked, nor does it provide a reason. Emits a signal notifying the logic that a player has left, and
        removes the player from the registry. All other players are notified that the player has been removed,
        and the client's socket is closed.

        Arguments:
            player_id: A string describing the ID of the player to remove. A string is used as it can flexibly
                store IDs and can store many characters to make them more unique.

        Returns:
            None.
        """
        session = self.registry.get(player_id)
        if session is None:
            return

        player = session.player

        # Notify logic that the player left
        self.player_left.emit(player.player_id, player.nickname)
        self.registry.remove(player_id)

        # Inform all clients that the player has been removed
        self._broadcast(
            {
                "type": ServerMessageType.PLAYER_LEFT,
                "data": {"nickname": player.nickname},
            }
        )

        # Closes the TCP connection
        session.client.close()

    def _resolve_hostname(self, client: ConnectedClient) -> None:
        """
        Internal method. Performs a reverse DNS lookup on the provided client's IP address to get the hostname.
        The hostname found is then set on the ConnectedClient in the `hostname` property, as a string. If the
        hostname could not be retrieved, None is set instead.

        This method should be run in a background thread to prevent freezing the main GUI loop, as the hostname
        lookup can block.

        Arguments:
            client: The ConnectedClient to resolve the hostname of. The client's `hostname` attribute is mutated
                and set to the hostname that is found in this method.

        Returns:
            None.
        """
        try:
            # Perform reverse DNS lookup
            client_host = socket.gethostbyaddr(client.ip_address)

            # Hostname is stored in first value of tuple
            client.hostname = client_host[0]
        except (OSError, socket.herror, socket.gaierror):
            client.hostname = None

    def _handle_client(self, sock: socket.socket, addr: tuple[str, int]) -> None:
        """
        Internal method. Handles communication between the server and a single client, by first initializing
        the ConnectedClient with a random ID and the socket, which represents an active connection in the server
        but not an actual Player yet.

        The server constantly listens for incoming messages from the client, and handles the states appropriately.
        If the client sends invalid data such as invalid JSON data or a message too large, the server will
        immediately disconnect the client as it can no longer be trusted. If the connection is detected to be a
        dead connection, the receive loop ends as well. When the server by changing its flag state, the client
        is removed automatically.

        This method should be run in a background thread to prevent freezing the main GUI loop, as its `recv()`
        calls are blocking.

        Arguments:
            sock: The client TCP socket, to wrap in the ConnectedClient and use to listen for messages from
                the specific client.

            addr: A tuple containing the IP address in the first field, as a string, and the ephemeral TCP
                port as the second value, as an integer. A tuple is used as that is the data type returned
                when accepting a client connection to the server.

        Returns:
            None.
        """
        # Create a ConnectedClient to represent a connection to the server, wrapping the raw socket
        client = ConnectedClient(ConnectedClient.generate_random_id(), sock, addr)

        # Resolve the hostname of the client in the background, as it can be blocking
        threading.Thread(
            target=self._resolve_hostname, args=(client,), daemon=True
        ).start()

        try:
            while self.is_running:
                # Repeatedly tries receiving a message from the client
                msg = client.recv()

                # Connection is dead
                if msg is None:
                    break

                # Any message from client means connection is still alive, so the
                # watchdog is aware the client is still alive. Delegates any messages
                # from the client to the dedicated handler.
                client.update_last_seen()
                self._handle_message(client, msg)
        except (ValueError, TypeError) as e:
            # Invalid JSON or UTF-8 received, message too large, or not a dictionary
            self._error_disconnection(client, f"Protocol violation: {e}")
        finally:
            # When the server is shut down, the client disconnects, the client
            # sends invalid data, or whatever, always end up removing the client.
            self._remove_client(client.client_id)

    def _handle_message(self, client: ConnectedClient, msg: dict) -> None:
        """
        Internal method. Acts as the central message dispatcher by identifying messages sent by the specific
        client to the server based on the message type provided. Based on the message type, a certain handler
        is called to delegate the specific message to.

        The message type passed should be the dictionary directly provided by the client. The root 'type' key
        is used to identify the type of message, and if it is missing, the server immediately disconnects the
        client as a safeguard. If the message type could not be recognized, the client is also disconnected.
        If all message type checks pass, the entire message, including the 'type' key, is passed onto the
        specific handler for that particular message type. No other data fields are validated.

        Arguments:
            client: The ConnectedClient that sent the message, which can be used to identify the player and,
                for example, respond specifically to the client that sent the message.

            msg: The message passed directly from the message given by the server, including the mandatory
                'type' key and optional 'data' key that contains any and all data needed for the request or
                message. A dictionary is used as it allows the JSON to be easily converted, and can store
                multiple keyed values together.

        Returns:
            None.
        """
        msg_type = msg.get("type")

        # No message type means a protocol violation, as the server cannot delegate it
        if msg_type is None:
            self._error_disconnection(client, "Message type missing")
            return

        handler = self.handlers.get(msg_type)

        # Message type does not have a respective handler, meaning it is of an unknown type
        if handler is None:
            self._error_disconnection(client, "Unknown message type")
            return

        try:
            handler(client, msg)
        except KeyError:
            # If the handler tries accessing data that does not exist, assume
            # server sent invalid data. This should be largely prevented by
            # _get_data_fields(), however, so this is here largely as a defensive
            # check.
            self._error_disconnection(client, "Missing fields in data")
            return

    def _get_data_fields(
        self,
        client: ConnectedClient,
        msg: dict,
        field_names: tuple[str, ...],
        empty_allowed: bool = False,
    ) -> dict | None:
        """
        Internal method. Used as a helper to get certain field names from the full message provided by the
        client. The message provided should be the full, unmodified dictionary from the client, including
        the mandatory 'type' and 'data' keys. It is assumed that, if this method is being called, the 'data'
        key is meant to be provided by the client. Otherwise, the client will be unfairly disconnected.

        The field names requested are searched for within the 'data' key dictionary, unless none are provided.
        If the 'data' key is not a dictionary, it is treated as a protocol violation and the client is
        disconnected. Otherwise, the field names are retrieved and returned as a dictionary after being validated.
        If the field names are empty, the entire 'data' raw dictionary is provided from the client without being
        validated. If a field name was not provided in the 'data' dictionary, the client is disconnected, unless
        `empty_allowed` is set to True, in which case it will be set to None if the key could not be found.

        Arguments:
            client: The ConnectedClient that sent the message, to allow disconnecting the client in case of
                a protocol violation.

            msg: The message passed directly from the message given by the client, including the 'type' key and
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
        # isn't a dictionary, it is treated as a protocol violation and the
        # client is disconnected.
        if not isinstance(data, dict):
            self._error_disconnection(client, "Invalid message data")
            return None

        # If no field names were directly specified, returns whole data dictionary
        if not field_names:
            return data

        fields = {}

        for field_name in field_names:
            field = data.get(field_name)

            # Only treats it as a protocol violation if empty values are disallowed
            if not empty_allowed and field is None:
                self._error_disconnection(
                    client, f"Missing required field: {field_name}"
                )
                return None

            # Makes new fields dictionary rather than returning data dictionary
            # to allow values not provided to be set to None if empty_allowed.
            fields[field_name] = field

        return fields

    def _handle_pong(self, client: ConnectedClient, msg: dict) -> None:
        """
        Internal method. A handler method for handling the `PONG` message type from the client.

        Calculates the time between the time the `PING` was sent from the server and the `PONG` was responded
        by the client as the round-trip time to display on the server UI, and to send to the client on the
        next `PING` for it to display on its own UI. If the client hasn't had a `PING` sent when sending a
        `PONG`, the round-trip time is not calculated. This method calculates round-trip time, not latency
        (which is one-way time).

        Arguments:
            client: The ConnectedClient that sent the message, to allow managing the client and sending messages
                directly to that specific client, as well as modifying it in the player registry.

            msg: The message passed directly from the message given by the client, including the 'type' key and
                'data' key. A dictionary is used as that is what is directly provided by the message handler.
                The message is unused in this handler, however, as the client should provide no extra data for
                this message type.

        Returns:
            None.
        """
        # Prevents running calculations if server hasn't sent a PING yet
        if client.last_ping_sent is None:
            return

        # Save last ping sent and reset
        sent_time = client.last_ping_sent
        client.last_ping_sent = None

        # Calculate round trip time and convert to milliseconds. Most games
        # display RTT, not one-way latency time, so do not divide by 2 unless
        # that is wanted.
        rtt = time.perf_counter() - sent_time
        client.rtt_ms = rtt * 1000

        # Informs server UI of updates
        self.rtt_updated.emit(client.client_id, client.rtt_ms)

    def _handle_join_lobby(self, client: ConnectedClient, msg: dict) -> None:
        """
        Internal method. A handler method for handling the `JOIN_LOBBY` message type from the client.

        Handles the client joining the lobby and becoming a valid player within the server and game, and also
        allowing it to be stored in the player registry. The details of the player joining are heavily validated,
        but if all checks pass, the player is added and all clients (including the one added) is notified of their
        joining. The client that joined is sent the current player list to display on its UI.

        Arguments:
            client: The ConnectedClient that sent the message, to allow managing the client and sending messages
                directly to that specific client, as well as modifying it in the player registry.

            msg: The message passed directly from the message given by the client, including the 'type' key and
                'data' key. A dictionary is used as that is what is directly provided by the message handler.

        Returns:
            None.
        """
        data_fields = self._get_data_fields(client, msg, ("nickname",))
        if data_fields is None:
            return

        nickname = data_fields.get("nickname")

        if not isinstance(nickname, str):
            self._error_disconnection(client, "The nickname is not a string")
            return

        # Prevent client from sending JOIN_LOBBY more than once
        if self.registry.has_id(client.client_id):
            self._client_invalid_action(client, "Cannot join again")
            return

        # Disconnect player if they join during an ongoing game
        if self.game_started:
            self._kick_client(client, "Game has already started")
            return

        # Attempt to add player to the registry, and get the reason if it fails
        nickname = nickname.strip()
        reason = self.registry.add(nickname, client)

        # Disconnect player if any validation checks fail
        if reason is AddPlayerResult.LOBBY_FULL:
            self._kick_client(client, "Server is full")
            return
        elif reason is AddPlayerResult.DUPLICATE_NICKNAME:
            self._kick_client(client, f'The nickname "{nickname}" is already in use')
            return
        elif reason is AddPlayerResult.EMPTY_NICKNAME:
            self._kick_client(client, "The nickname is empty")
            return
        elif reason is AddPlayerResult.LONG_NICKNAME:
            self._kick_client(client, "The nickname is too long")
            return

        # The Big Harsh is like Jupiter, and Jupiter can't fit in the server, obviously ;)
        if nickname == "The Big Harsh":
            self._kick_client(client, "The player does not fit in the server")
            return

        # Inform server logic of player joining
        self.player_joined.emit(client.client_id, nickname)

        # Inform clients of player join, including the one that just connected
        self._broadcast(
            {
                "type": ServerMessageType.PLAYER_JOINED,
                "data": {"nickname": nickname},
            }
        )

        # Get list of players for client player list UI
        sessions = self.registry.get_all().values()
        player_list = [s.player.nickname for s in sessions]

        # Inform client of current lobby state
        client.send(
            {
                "type": ServerMessageType.CONNECTION_SUCCESSFUL,
                "data": {"player_list": player_list},
            }
        )

    def _handle_leave_lobby(self, client: ConnectedClient, msg: dict) -> None:
        """
        Internal method. A handler method for handling the `LEAVE_LOBBY` message type from the client.

        Simply removes and disconnects the player from the server, and notifies all other clients and the
        server UI logic of their removal.

        Arguments:
            client: The ConnectedClient that sent the message, to allow managing the client and sending messages
                directly to that specific client, as well as modifying it in the player registry.

            msg: The message passed directly from the message given by the client, including the 'type' key and
                'data' key. A dictionary is used as that is what is directly provided by the message handler.
                The message is unused in this handler, however, as the client should provide no extra data for
                this message type.

        Returns:
            None.
        """
        self._remove_client(client.client_id)

    def _handle_answer_submit(self, client: ConnectedClient, msg: dict) -> None:
        """
        Internal method. A handler method for handling the `ANSWER_SUBMIT` message type from the client.

        Simply removes and disconnects the player from the server, and notifies all other clients and the
        server UI logic of their removal.

        Arguments:
            client: The ConnectedClient that sent the message, to allow managing the client and sending messages
                directly to that specific client, as well as modifying it in the player registry.

            msg: The message passed directly from the message given by the client, including the 'type' key and
                'data' key. A dictionary is used as that is what is directly provided by the message handler.

        Returns:
            None.
        """
        data_fields = self._get_data_fields(client, msg, ("selected_index",))
        if data_fields is None:
            return

        selected_index = data_fields.get("selected_index")

        # Use type() rather than isinstance() since bool is a subclass of int
        if type(selected_index) is not int:
            self._error_disconnection(client, "The selected answer is not an integer")
            return

        # Prevent sending an answer submission when the game isn't running
        if not self.game_started:
            self._client_invalid_action(
                client, "Cannot submit an answer when the game is not running"
            )
            return

        # Record the time the message was received for points calculations.
        # Don't ask for the time from the client, since the client can lie and
        # say it answered in 0.1 seconds, for example. The server is the only
        # source of truth!
        received_time = time.monotonic()

        # Informs logic and game logic of the answer submission
        self.answer_submitted.emit(client.client_id, selected_index, received_time)

    def send_countdown_start(self, duration: int) -> None:
        """
        Broadcasts the `COUNTDOWN_STARTED` message type to all clients, with the duration of the countdown
        provided. The duration is not validated before sending.

        Arguments:
            duration: A positive integer for the duration in seconds that the countdown should last for. An
                integer is used as it represents whole numbers well, as the duration does not need decimal
                precision.

        Returns:
            None.
        """
        self._broadcast(
            {
                "type": ServerMessageType.COUNTDOWN_STARTED,
                "data": {"duration": duration},
            }
        )

    def send_question_data(self, question_data: dict) -> None:
        """
        Broadcasts the `QUESTION_DATA` message type to all clients, with the question information provided.
        The question data is not validated.

        Arguments:
            question_data: A dictionary containing all the information needed for the client to display
                question data to the UI. A dictionary is used to store multiple values and allow easier
                conversion to the data transfer object payload.

        Returns:
            None.
        """
        self._broadcast(
            {"type": ServerMessageType.QUESTION_DATA, "data": question_data}
        )

    def send_question_results(self, player_id: str, results_data: dict) -> None:
        """
        Sends the `RESULTS` message type to an individual client, with the results data provided. The results
        data is not validated.

        Arguments:
            player_id: A string describing the ID of the player to send the results data to. A string is used
                as it can flexibly store IDs and can store many characters to make them more unique.

            results_data: A dictionary containing all the information needed for the client to display
                results data to the UI. A dictionary is used to store multiple values and allow easier
                conversion to the data transfer object payload.

        Returns:
            None.
        """
        session = self.registry.get(player_id)

        if session:
            session.client.send(
                {"type": ServerMessageType.RESULTS, "data": results_data}
            )

    def send_final_results(self, player_id: str, results_data: dict) -> None:
        """
        Sends the `FINAL_RESULTS` message type to an individual client, with the final results data provided.
        The final results data is not validated.

        Once the data is sent, the client is disconnected from the server as no further information is needed to
        be sent from the server or received from the client, as the game is over. Resets the current game flag
        to be False.

        Arguments:
            player_id: A string describing the ID of the player to send the final results data to. A string
                is used as it can flexibly store IDs and can store many characters to make them more unique.

            results_data: A dictionary containing all the information needed for the client to display final
                results data to the UI. A dictionary is used to store multiple values and allow easier
                conversion to the data transfer object payload.

        Returns:
            None.
        """
        session = self.registry.get(player_id)

        if session:
            session.client.send(
                {"type": ServerMessageType.FINAL_RESULTS, "data": results_data}
            )

            try:
                # Performs a TCP half-close. SHUT_WR means the server will no longer
                # send any data, but the client can still receive any requests sent.
                session.client.socket.shutdown(socket.SHUT_WR)
            except OSError:
                pass

        # Game has concluded
        self.game_started = False

    def send_invalid_action(self, player_id: str, reason: str) -> None:
        """
        Sends the `INVALID_ACTION` message type to an individual client, with the reason provided.

        The invalid action should be used when the client performs something that isn't valid in the current
        state of the server, but is not a protocol violation as it follows all the message rules. In this
        case, the client is not disconnected, but warned.

        Typically, when wanting to warn the player from the server directly, using `_client_invalid_action()`
        directly is a better option, especially if you have the `ConnectedClient`, as it avoids a lookup.

        Arguments:
            player_id: A string describing the ID of the player to send the invalid action warning to. A string
                is used as it can flexibly store IDs and can store many characters to make them more unique.

            reason: The reason for the client's action being disallowed, which is sent to the client. A string
                is used to allow variety in the message sent.

        Returns:
            None.
        """
        session = self.registry.get(player_id)
        if session:
            self._client_invalid_action(session.client, reason)

    def _client_invalid_action(self, client: ConnectedClient, reason: str) -> None:
        """
        Internal method. Directly sends an `INVALID_ACTION` to the ConnectedClient instance provided. If the
        ConnectedClient is unknown, but the player/client ID is known, use `send_invalid_action()` instead.

        The invalid action should be used when the client performs something that isn't valid in the current
        state of the server, but is not a protocol violation as it follows all the message rules. In this
        case, the client is not disconnected, but warned.

        Arguments:
            client: The ConnectedClient that performed the invalid action, to allow sending the message to that
                specific client only.

            reason: The reason for the client's action being disallowed, which is sent to the client. A string
                is used to allow variety in the message sent.

        Returns:
            None.
        """
        client.send(
            {"type": ServerMessageType.INVALID_ACTION, "data": {"reason": reason}}
        )

    def _kick_client(self, client: ConnectedClient, reason: str) -> None:
        """
        Internal method. Directly sends an `KICK` to the ConnectedClient instance provided. If the ConnectedClient
        is unknown, but the player/client ID is known, use `kick_player()` instead.

        The message is sent to the client before the client is disconnected by the server.

        Arguments:
            client: The ConnectedClient to kick, to allow sending the message and disconnecting that specific
                client only.

            reason: The reason for the client's being kicked, which is sent to the client. A string is used to
                allow variety in the message sent.

        Returns:
            None.
        """
        self._send_and_disconnect(
            client,
            {"type": ServerMessageType.KICK, "data": {"reason": reason}},
        )

    def _error_disconnection(self, client: ConnectedClient, reason: str) -> None:
        """
        Internal method. Directly sends an `ERROR` to the ConnectedClient instance provided. The `ERROR` message
        type should not be sent from anywhere other than the GameServer, as it is reserved for protocol errors
        only.

        The message is sent to the client before the client is disconnected by the server.

        Arguments:
            client: The ConnectedClient to disconnect, to allow sending the message and disconnecting that
                specific client only.

            reason: The reason for the client's being disconnected, which is sent to the client. A string is
                used to allow variety in the message sent.

        Returns:
            None.
        """
        self._send_and_disconnect(
            client,
            {"type": ServerMessageType.ERROR, "data": {"reason": reason}},
        )

    def _send_and_disconnect(self, client: ConnectedClient, msg: dict) -> None:
        """
        Internal method. Sends a message to the ConnectedClient instance provided, before disconnecting them
        from the server. A TCP half-close is performed to allow the message to be sent, before the TCP socket
        is closed. The message provided is not validated for the 'type' and 'data' keys before being sent.

        Arguments:
            client: The ConnectedClient to send the message to and disconnect, to allow it to only happen to
                the specific client provided.

            msg: The message to send to the client, including the mandatory 'type' key and optional 'data' key.
                A dictionary is used as it can be easily serialized to go across the network and store multiple
                values.

        Returns:
            None.
        """
        try:
            # Sends the data, then performs a TCP half-close. SHUT_WR means the
            # server will no longer send any data, but the client can still
            # receive any requests sent.
            client.send(msg)
            client.socket.shutdown(socket.SHUT_WR)
        except OSError:
            pass

        # Removes the client from the server if it exists in the registry
        if self.registry.get(client.client_id) is not None:
            self._remove_client(client.client_id)

        # Close the client TCP connection
        client.close()
