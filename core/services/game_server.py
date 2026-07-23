import errno
import socket
import threading
import time
from collections.abc import Callable

from PyQt6.QtCore import QObject, pyqtSignal

from core.app.enums import AddPlayerResult, ServerStartingError
from core.services.network.connected_client import ConnectedClient
from core.services.network.player_registry import PlayerRegistry
from core.services.network.types import ClientMessageType, ServerMessageType
from models.player import Player

from core.config.constants import PORT, CLIENT_PING_INTERVAL, RESPONSE_TIMEOUT


class GameServer(QObject):
    """Manages the networking relating to the game server."""

    start_failed = pyqtSignal(ServerStartingError)
    started = pyqtSignal()

    # Player ID, nickname
    player_joined = pyqtSignal(str, str)
    player_left = pyqtSignal(str, str)

    latency_updated = pyqtSignal(str, float)

    # Player ID, answer index, time submitted (monotonic server-side)
    answer_submitted = pyqtSignal(str, int, float)

    def __init__(self) -> None:
        """Initialize server attributes and handlers for client messages."""
        super().__init__()

        # Listens to all network interfaces
        self.host_ip = "0.0.0.0"
        self.port = PORT
        self.is_running = False
        self.game_started = False

        self.server_socket: socket.socket = None
        self.registry = PlayerRegistry()

        # Handlers for incoming client messages
        self.handlers: dict[
            ClientMessageType, Callable[[ConnectedClient, dict], None]
        ] = {
            ClientMessageType.PONG: self.handle_pong,
            ClientMessageType.JOIN_LOBBY: self.handle_join_lobby,
            ClientMessageType.LEAVE_LOBBY: self.handle_leave_lobby,
            ClientMessageType.ANSWER_SUBMIT: self.handle_answer_submit,
        }

    def get_player_address(self, player_id: str) -> tuple[str, int] | None:
        """Get IP address and port of a certain player."""
        session = self.registry.get(player_id)

        if session is not None:
            return session.client.socket.getpeername()

        # Player does not exist
        return None

    def get_client_latency(self, client_id: str) -> float | None:
        """Get the latency of the client in milliseconds."""
        session = self.registry.get(client_id)
        if session is None:
            return None

        return session.client.rtt_ms

    def get_player(self, player_id: str) -> Player | None:
        """Get the player instance from the registry."""
        session = self.registry.get(player_id)

        if session is not None:
            return session.player

        # Player does not exist
        return None

    def get_total_players(self) -> int:
        """Gets the number of players connected to the server."""
        return len(self.registry.get_all())

    def start(self) -> None:
        """Starts the server and accepts clients."""
        # Usually this wouldn't be in it's own function due to only starting a thread,
        # but it provides a cleaner API
        threading.Thread(target=self._start_and_listen, daemon=True).start()

    def stop(self, reason: str = "Server closed") -> None:
        """Stops the server cleanly, notifying and disconnecting all clients."""
        if self.server_socket is None:
            return

        # Get all sessions and store them in memory, then clear the sessions
        sessions = self.registry.get_all().values()
        self.registry.clear()

        # NOTE You can't use self.broadcast() here since it tries to get the
        # old sessions which have been cleared. Putting this logic above the registry deletion
        # code will cause some clients to not be disconnected due to threading
        for session in sessions:
            try:
                session.client.send(
                    {"type": ServerMessageType.KICK, "data": {"reason": reason}}
                )

                # Informs client that server has no more data to send,
                # but they can still receive data
                session.client.socket.shutdown(socket.SHUT_WR)
            except OSError:
                pass

        self.is_running = False
        self.game_started = False

        self.server_socket.close()
        self.server_socket = None

    def _start_and_listen(self) -> None:
        """Starts the server and listens for incoming clients."""
        try:
            # TCP protocol
            self.server_socket = socket.create_server((self.host_ip, self.port))
        except OSError as e:
            if e.errno == errno.EADDRINUSE:
                # Port in use
                self.start_failed.emit(ServerStartingError.IN_USE)

            elif e.errno == errno.EACCES:
                # Permission denied (e.g. reserved ports)
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

        self.is_running = True
        self.started.emit()

        # Start global watchdog and accept clients
        threading.Thread(target=self._client_latency_loop, daemon=True).start()
        threading.Thread(target=self._client_watchdog_loop, daemon=True).start()
        self.accept_clients()

    def _client_latency_loop(self) -> None:
        """Sends pings to clients to measure latency."""
        while self.is_running:
            time.sleep(CLIENT_PING_INTERVAL)

            for session in self.registry.get_all().values():
                try:
                    # Use perf counter rather than monotonic for accurate timing
                    client = session.client
                    client.last_ping_sent = time.perf_counter()

                    # Use -1 rather than None since client won't accept a None value
                    rtt = -1 if client.rtt_ms is None else client.rtt_ms
                    client.send({"type": ServerMessageType.PING, "data": {"rtt": rtt}})
                except OSError:
                    self._kick_client(session.client, "Failed to ping client")

    def _client_watchdog_loop(self) -> None:
        """
        Starts watchdog (disconnects client if no response from them is detected).
        Checks last response time from clients. If a client exceeds response timeout, disconnects them.
        """
        while self.is_running:
            # Prevent constant checking
            time.sleep(1)

            sessions = self.registry.get_all().values()

            for session in sessions:
                # If difference between now and last ping time exceeds response timeout, disconnect client
                if time.monotonic() - session.client.last_seen > RESPONSE_TIMEOUT:
                    # If the client is somehow still connected, send kick request
                    self._kick_client(session.client, "Client timeout")

    def accept_clients(self) -> None:
        """Accept incoming clients and delegate them to an individual threaded handler."""
        while self.is_running:
            try:
                client, addr = self.server_socket.accept()
            except OSError:
                break

            # Handle each client concurrently in their own thread
            threading.Thread(
                target=self.handle_client, args=(client, addr), daemon=True
            ).start()

    def broadcast(self, msg: dict) -> None:
        """Broadcast message to all connected players."""
        sessions = self.registry.get_all().values()

        for session in sessions:
            try:
                session.client.send(msg)
            except OSError:
                self._kick_client(session.client, "Failed to broadcast")

    def kick_player(self, player_id: str, reason: str) -> None:
        """Kicks a player from the server based on player ID, and sends a `KICK` message if they are in the registry."""
        session = self.registry.get(player_id)
        if session:
            self._kick_client(session.client, reason)

    def remove_client(self, player_id: str) -> None:
        """Removes a client from the server. Unlike `kick_player()`, this does not send a message to the player."""
        session = self.registry.get(player_id)

        if session is None:
            return

        self.player_left.emit(session.player.player_id, session.player.nickname)
        self.registry.remove(player_id)

        # Inform all clients other than the one that left
        self.broadcast(
            {
                "type": ServerMessageType.PLAYER_LEFT,
                "data": {"nickname": session.player.nickname},
            }
        )

        session.client.close()

    def handle_client(self, sock: socket.socket, addr: tuple[str, int]) -> None:
        """Handles an individual client by assigning a player ID and ConnectedClient.
        Receives requests from the server and handles messages.
        """
        client = ConnectedClient(ConnectedClient.generate_random_id(), sock)

        try:
            while self.is_running:
                # Receive a message when EOL is received
                msg = client.recv()

                # Blank message means TCP cleanly disconnected
                if msg is None:
                    break

                client.update_last_seen()
                self.handle_message(client, msg)
        except OSError:
            pass
        except ValueError as e:
            # Invalid JSON received or message too large
            self._kick_error(client, f"Protocol violation: {e}")
        finally:
            self.remove_client(client.client_id)

    def handle_message(self, client: ConnectedClient, msg: dict) -> None:
        """Handle a message from a client by delegating it to a respective handler."""
        msg_type = msg.get("type")

        # No message type; server cannot delegate it
        if msg_type is None:
            self._kick_error(client, "Message type missing")
            return

        handler = self.handlers.get(msg_type)

        # Message type does not have a respective handler
        if handler is None:
            self._kick_error(client, "Unknown message type")
            return

        handler(client, msg)

    def get_data_fields(
        self, client: ConnectedClient, msg: dict, field_names: list[str]
    ) -> dict | None:
        """Get fields from the 'data' of a message from the client, validating it.
        If `field_names` is empty, returns the data dictionary itself."""
        data = msg.get("data")

        if not isinstance(data, dict):
            self._kick_error(client, "Invalid message data from client")
            return None

        if not field_names:
            return data

        fields = {}

        for field_name in field_names:
            field = data.get(field_name)

            if field is None:
                self._kick_error(
                    client, f"Missing required field from client: {field_name}"
                )
                return None

            fields[field_name] = field

        return fields

    def handle_pong(self, client: ConnectedClient, msg: dict) -> None:
        """Handles the `PONG` message type and calculates client round trip time."""
        if client.last_ping_sent is None:
            return

        # Save last ping sent and reset
        sent_time = client.last_ping_sent
        client.last_ping_sent = None

        # Calculate round trip time and convert to milliseconds
        # Most games display RTT, not one-way time, so do not divide by 2 unless that is wanted
        rtt = time.perf_counter() - sent_time
        client.rtt_ms = rtt * 1000

        self.latency_updated.emit(client.client_id, client.rtt_ms)

    def handle_join_lobby(self, client: ConnectedClient, msg: dict) -> None:
        """Handles the `JOIN_LOBBY` message type. Validates player data and adds them."""
        data_fields = self.get_data_fields(client, msg, ["nickname"])
        if data_fields is None:
            return

        nickname = data_fields.get("nickname")

        if not isinstance(nickname, str):
            self._kick_error(client, "The nickname is not a string")
            return

        # Client sent join request after already joining
        if self.registry.has_id(client.client_id):
            self._invalid_action_client(client, "Cannot join again")
            return

        if self.game_started:
            self._kick_client(client, "Game has already started")
            return

        reason = self.registry.add(nickname, client)

        # Validation checks before adding new player
        if reason == AddPlayerResult.LOBBY_FULL:
            self._kick_client(client, "Server is full")
            return
        elif reason == AddPlayerResult.DUPLICATE_NICKNAME:
            self._kick_client(client, f'The nickname "{nickname}" is already in use')
            return
        elif reason == AddPlayerResult.EMPTY_NICKNAME:
            self._kick_client(client, "The nickname is empty")
            return
        elif reason == AddPlayerResult.LONG_NICKNAME:
            self._kick_client(client, "The nickname is too long")
            return

        # The Big Harsh is like Jupiter ;)
        # and Jupiter can't fit in the server, obviously
        if nickname.lower() == "the big harsh":
            self._kick_client(client, "The player does not fit in the server")
            return

        self.player_joined.emit(client.client_id, nickname)

        # Inform clients of player join
        self.broadcast(
            {
                "type": ServerMessageType.PLAYER_JOINED,
                "data": {"nickname": nickname},
            }
        )

        # Get list of players for client player list UI
        sessions = self.registry.get_all().values()
        player_list = [s.player.nickname for s in sessions]

        # Inform client of player ID and current lobby state
        client.send(
            {
                "type": ServerMessageType.CONNECTION_SUCCESSFUL,
                "data": {"player_id": client.client_id, "player_list": player_list},
            }
        )

    def handle_leave_lobby(self, client: ConnectedClient, msg: dict) -> None:
        """Handles the `LEAVE_LOBBY` message type."""
        self.remove_client(client.client_id)

    def handle_answer_submit(self, client: ConnectedClient, msg: dict) -> None:
        """Handles the `ANSWER_SUBMIT` message type. Also records the time the data was received."""
        data_fields = self.get_data_fields(client, msg, ["selected_index"])
        if data_fields is None:
            return

        selected_index = data_fields.get("selected_index")

        if not isinstance(selected_index, int):
            self._kick_error(client, "The selected answer is not an integer")
            return

        if not self.game_started:
            self._invalid_action_client(
                client, "Cannot submit an answer when a game is not running"
            )
            return

        # Record the time the message was received for points calculations
        # Don't trust client ;)
        received_time = time.monotonic()
        self.answer_submitted.emit(client.client_id, selected_index, received_time)

    def send_countdown_start(self, duration: int) -> None:
        """Sends a `COUNTDOWN_STARTED` message to all clients."""
        self.broadcast(
            {
                "type": ServerMessageType.COUNTDOWN_STARTED,
                "data": {"duration": duration},
            }
        )

    def send_question_data(self, question_info: dict) -> None:
        """Sends a `QUESTION_DATA` message to all clients."""
        self.broadcast({"type": ServerMessageType.QUESTION_DATA, "data": question_info})

    def send_question_results(self, player_id: str, results_data: dict) -> None:
        """Sends a `RESULTS` message to an individual client."""
        session = self.registry.get(player_id)

        if session:
            session.client.send(
                {"type": ServerMessageType.RESULTS, "data": results_data}
            )

    def send_final_results(self, player_id: str, results_data: dict) -> None:
        """Sends a `FINAL_RESULTS` message to an individual client."""
        session = self.registry.get(player_id)

        if session:
            session.client.send(
                {"type": ServerMessageType.FINAL_RESULTS, "data": results_data}
            )

        self.remove_client(player_id)
        self.game_started = False

    def send_invalid_action(self, player_id: str, reason: str) -> None:
        """Sends a `INVALID_ACTION` message to certain clients."""
        session = self.registry.get(player_id)

        if session:
            self._invalid_action_client(session.client, reason)

    def _invalid_action_client(self, client: ConnectedClient, reason: str) -> None:
        """Sends an `INVALID_ACTION` message to the client directly. This does not disconnect them."""
        client.send(
            {"type": ServerMessageType.INVALID_ACTION, "data": {"reason": reason}}
        )

    def _send_and_disconnect(self, client: ConnectedClient, msg: dict) -> None:
        """Sends a message to a client and disconnects them immediately afterwards."""
        try:
            client.send(msg)
            client.socket.shutdown(socket.SHUT_WR)
        except OSError:
            pass

        if self.registry.get(client.client_id) is not None:
            self.remove_client(client.client_id)

        client.close()

    def _kick_error(self, client: ConnectedClient, reason: str) -> None:
        """Sends an `ERROR` message type to the client, then disconnects them."""
        self._send_and_disconnect(
            client,
            {"type": ServerMessageType.ERROR, "data": {"reason": reason}},
        )

    def _kick_client(self, client: ConnectedClient, reason: str) -> None:
        """
        Sends an `KICK` message type to the client, then disconnects them. Should be used when
        the `ConnectedClient` is readily available. If only the player ID is known, use `kick_player()`.
        """
        self._send_and_disconnect(
            client,
            {
                "type": ServerMessageType.KICK,
                "data": {"reason": reason},
            },
        )
