import socket
import threading
import secrets
import time
from PyQt6.QtCore import QObject, pyqtSignal

from core.services.network.connected_client import ConnectedClient
from core.services.network.player_registry import PlayerRegistry
from core.services.network.types import ClientMessageType, ServerMessageType
from core.game.quiz_manager import QuizManager
from core.config.constants import PORT, RESPONSE_TIMEOUT


class GameServer(QObject):
    """Manages the networking relating to the game server."""

    # Define signals for communicating from service to logic
    starting = pyqtSignal()
    start_fail = pyqtSignal(str)
    start_success = pyqtSignal()

    player_joined = pyqtSignal(str)
    player_left = pyqtSignal(str)

    def __init__(self) -> None:
        """Initialize client attributes and handlers for client messages."""
        super().__init__()

        self.host_ip = "0.0.0.0"  # listens to all network interfaces
        self.port = PORT
        self.is_running = False
        self.game_started = False

        self.server_socket: socket.socket = None
        self.registry = PlayerRegistry()

        self.handlers: dict[ClientMessageType, function] = {
            ClientMessageType.PING: self.handle_ping,
            ClientMessageType.JOIN_LOBBY: self.handle_join_lobby,
            ClientMessageType.LEAVE_LOBBY: self.handle_leave_lobby,
        }

    def get_player_address(self, player_id: str) -> tuple[str, int] | None:
        """Get IP address and port of a certain player."""
        client = self.registry.get(player_id).client

        if client:
            return client.socket.getpeername()

        # Player does not exist
        return None

    def create_random_player_id(self) -> str:
        """Generate a random unique player ID."""
        return secrets.token_hex(4)

    def start(self) -> None:
        """Starts the server and accepts clients."""
        self.starting.emit()
        threading.Thread(target=self._start_and_listen, daemon=True).start()

    def stop(self) -> None:
        """Stops the server clearnly, notifying and disconnecting all clients."""
        if self.server_socket is None:
            raise ValueError("Server cannot be stopped without active socket")

        sessions = self.registry.get_all().values()
        self.registry.clear()

        for session in sessions:
            try:
                session.client.send(
                    {
                        "type": ServerMessageType.KICK,
                        "data": {"reason": "Server closed"},
                    }
                )

                # Informs client that server has no more data to send,
                # but they can still receive data
                session.client.socket.shutdown(socket.SHUT_WR)
            except OSError:
                pass

        self.is_running = False
        self.server_socket.close()

    def _start_and_listen(self) -> None:
        """Starts the server and listens for incoming clients."""
        try:
            # TCP protocol
            self.server_socket = socket.create_server((self.host_ip, self.port))
        except OSError as e:
            # Address in use
            if e.errno == 10048:
                self.start_fail.emit("in_use")
                return
            else:
                # technically, start_fail could be emitted,
                # but it would be pointless due to the 'raise'
                raise

        self.is_running = True

        self.start_success.emit()

        # Start global watchdog and accept clients
        self.start_client_watchdog()
        self.accept_clients()

    def accept_clients(self) -> None:
        """Accept incoming clients and delegate them to an individual threaded handler."""
        while self.is_running:
            try:
                client, addr = self.server_socket.accept()
            except OSError:
                break

            threading.Thread(
                target=self.handle_client, args=(client, addr), daemon=True
            ).start()

    def start_client_watchdog(self) -> None:
        """Starts watchdog (disconnects client if no response from them is detected)."""
        threading.Thread(target=self._client_watchdog_loop, daemon=True).start()

    def _client_watchdog_loop(self) -> None:
        """Checks last response time from clients. If a client exceeds response timeout, disconnects them."""
        while self.is_running:
            time.sleep(1)

            sessions = self.registry.get_all().values()

            # If the client is somehow still connected, send kick request
            for session in sessions:
                if time.monotonic() - session.client.last_seen > RESPONSE_TIMEOUT:
                    self._kick_client(session.client, "Client timeout")

    def broadcast(self, msg: dict) -> None:
        """Broadcast message to all connected players."""
        sessions = self.registry.get_all().values()

        for session in sessions:
            try:
                session.client.send(msg)
            except OSError:
                self._kick_client(session.client, "Failed to broadcast")

    def kick_player(self, player_id: str, reason: str) -> None:
        """Kicks a player from the server, and sends a `KICK` request if they are in the registry."""
        session = self.registry.get(player_id)

        if session:
            self._kick_client(session.client, reason)

    def remove_client(self, player_id: str) -> None:
        """Removes a client from the server. Unlike `kick_player()`, this does not send a request to the player."""
        session = self.registry.get(player_id)

        if session is None:
            return

        self.registry.remove(player_id)
        self.player_left.emit(session.player.nickname)

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
        client = ConnectedClient(sock, self.create_random_player_id())

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
        finally:
            self.remove_client(client.player_id)

    def handle_message(self, client: ConnectedClient, msg: dict) -> None:
        """Handle a message from a client by delegating it to a respective handler."""
        msg_type = msg.get("type")

        # No message type; server cannot delegate it
        if msg_type is None:
            print(f"'type' key was not present in message, received: {msg}")
            self._fail_and_disconnect(client, "Message type missing")
            return

        handler = self.handlers.get(msg_type)

        # Message type does not have a respective handler
        if handler is None:
            print(f"The msg_type {msg_type} did not match any types (server)")
            self._fail_and_disconnect(client, "Unknown message type")
            return

        handler(client, msg)

    def handle_ping(self, client: ConnectedClient, msg: dict) -> None:
        """Handles the `PONG` message type."""
        client.send({"type": ServerMessageType.PONG})

    def handle_join_lobby(self, client: ConnectedClient, msg: dict) -> None:
        """Handles the `JOIN_LOBBY` message type. Validates player data and adds them."""
        try:
            nickname = msg["data"]["nickname"]
        except KeyError:
            print(f"Invalid data in message, received: {msg}")
            self._fail_and_disconnect(client, "Missing player nickname")
            return

        if self.registry.has_id(client.player_id):
            client.send(
                {
                    "type": ServerMessageType.INVALID_ACTION,
                    "data": {"reason": "Cannot join twice"},
                }
            )

        if self.game_started:
            self._kick_client(client, "Game has already started")
            return

        success, reason = self.registry.add(nickname, client)

        # Validation checks before adding new player
        # Provided by registry; registry does not add player if any of these conditions are True
        if not success:
            if reason == "lobby_full":
                self._kick_client(client, "Server is full")
                return
            elif reason == "dupe_nickname":
                self._kick_client(
                    client, f'The nickname "{nickname}" is already in use'
                )
                return
            elif reason == "long_nickname":
                self._kick_client(client, "The nickname is too long")
                return
            else:
                # Should never happen
                self._kick_client(client, "Unknown error while adding player")
                return

        # The Big Harsh is like Jupiter ;)
        # and Jupiter can't fit in the server, obviously
        if nickname.lower() == "the big harsh":
            self._kick_client(client, "The player does not fit in the server")
            return

        self.player_joined.emit(nickname)

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
                "data": {"player_id": client.player_id, "player_list": player_list},
            }
        )

    def handle_leave_lobby(self, client: ConnectedClient, msg: dict) -> None:
        """Handles the `LEAVE_LOBBY` message type."""
        self.remove_client(client.player_id)

    def send_countdown_start(self, start_time: float, duration: int) -> None:
        self.broadcast(
            {
                "type": ServerMessageType.COUNTDOWN_STARTED,
                "data": {"start_time": start_time, "duration": duration},
            }
        )

    def _send_and_disconnect(self, client: ConnectedClient, msg: dict) -> None:
        """Sends a message to a client and disconnects them immediately afterwards."""
        try:
            client.send(msg)
        finally:
            if self.registry.get(client.player_id) is not None:
                self.remove_client(client.player_id)

            client.close()

    def _fail_and_disconnect(self, client: ConnectedClient, reason: str) -> None:
        """Sends an `ERROR` message type to the client, then disconnects them."""
        self._send_and_disconnect(
            client,
            {"type": ServerMessageType.ERROR, "data": {"reason": reason}},
        )

    def _kick_client(self, client: ConnectedClient, reason: str) -> None:
        """Sends an `KICK` message type to the client, then disconnects them."""
        self._send_and_disconnect(
            client,
            {
                "type": ServerMessageType.KICK,
                "data": {"reason": reason},
            },
        )
