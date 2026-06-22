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
    """Manages the networking relating to the game client."""

    # Define signals for communicating from service to logic
    starting = pyqtSignal()
    start_fail = pyqtSignal(str)
    start_success = pyqtSignal()

    player_joined = pyqtSignal(str)
    player_left = pyqtSignal(str)

    def __init__(self):
        """Initialize client attributes and handlers for client messages."""
        super().__init__()

        self.host_ip = "0.0.0.0"  # listens to all network interfaces
        self.port = PORT
        self.is_running = False

        self.server_socket: socket.socket = None
        self.quiz_manager = QuizManager()
        self.player_registry = PlayerRegistry()

        self.handlers: dict[ServerMessageType, function] = {
            ClientMessageType.PING: self.handle_ping,
            ClientMessageType.JOIN_LOBBY: self.handle_join_lobby,
            ClientMessageType.LEAVE_LOBBY: self.handle_leave_lobby,
        }

    def get_id_from_nickname(self, nickname: str) -> str:
        """Get player nickname from ID."""
        return self.player_registry.get_id_by_nickname(nickname)

    def get_player_address(self, player_id: str) -> tuple[str, int] | None:
        """Get IP address and port of a certain player."""
        client = self.player_registry.get_player(player_id)

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

        self.broadcast(
            {"type": ServerMessageType.KICK, "data": {"reason": "Server closed"}}
        )

        connected_players = self.player_registry.get_players().values()
        self.player_registry.clear_players()

        # Close all client sockets, unless they are invalid
        for client in connected_players:
            try:
                client.close()
            except OSError:
                continue

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

            connected_players = self.player_registry.get_players().values()

            # If the client is somehow still connected, send kick request
            for client in connected_players:
                if time.monotonic() - client.last_seen > RESPONSE_TIMEOUT:
                    self._kick(client, "Client timeout")

    def broadcast(self, msg: dict) -> None:
        """Broadcast message to all connected players."""
        connected_players = self.player_registry.get_players().values()

        for client in connected_players:
            try:
                client.send(msg)
            except OSError:
                self._kick(client, "Failed to broadcast")

    def kick_player(self, player_id: str, reason: str) -> None:
        """Kicks a player from the server, and sends a `KICK` request if they are in the registry."""
        client = self.player_registry.get_player(player_id)

        if client:
            self._kick(client, reason)

    def remove_client(self, player_id: str) -> None:
        """Removes a client from the server. Unlike `kick_player()`, this does not send a request to the player."""
        client = self.player_registry.get_player(player_id)

        if client is None:
            return

        self.player_registry.remove_player(player_id)
        self.player_left.emit(client.nickname)

        # Inform all clients other than the one that left
        self.broadcast(
            {
                "type": ServerMessageType.PLAYER_LEFT,
                "data": {"nickname": client.nickname},
            }
        )

        client.close()

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
            self._error(client, "Message type missing")
            return

        handler = self.handlers.get(msg_type)

        # Message type does not have a respective handler
        if handler is None:
            print(f"The msg_type {msg_type} did not match any types (server)")
            self._error(client, "Unknown message type")
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
            self._error(client, "Missing player nickname")
            return

        client.nickname = nickname
        status, player = self.player_registry.add_player(nickname, client)

        # Validation checks before adding new player
        # Provided by registry; registry does not add player if any of these conditions are True
        if status == "lobby_full":
            self._kick(client, "Server is full")
            return
        elif status == "dupe_nickname":
            self._kick(client, f'The nickname "{nickname}" is already in use')
            return
        elif status == "long_nickname":
            self._kick(client, "The nickname is too long")
            return
        elif status == "dupe_id":
            self._kick(client, "The player ID generated matches an existing ID")
            return

        client.player = player
        self.player_joined.emit(nickname)

        # Inform clients of player join, and inform own client of their ID
        self.broadcast(
            {
                "type": ServerMessageType.PLAYER_JOINED,
                "data": {"nickname": nickname},
            }
        )

        # Get list of players for client player list UI
        connected_players = self.player_registry.get_players().values()
        player_list = [c.nickname for c in connected_players]

        client.send(
            {
                "type": ServerMessageType.CONNECTION_SUCCESSFUL,
                "data": {"player_id": client.player_id, "player_list": player_list},
            }
        )

    def handle_leave_lobby(self, client: ConnectedClient, msg: dict) -> None:
        """Handles the `LEAVE_LOBBY` message type."""
        self.remove_client(client.player_id)

    def _send_and_disconnect(self, client: ConnectedClient, msg: dict) -> None:
        """Sends a message to a client and disconnects them immediately afterwards."""
        try:
            client.send(msg)
        finally:
            if client.player is not None:
                self.remove_client(client.player_id)

            client.close()

    def _error(self, client: ConnectedClient, reason: str) -> None:
        """Sends an `ERROR` message type to the client, then disconnects them."""
        self._send_and_disconnect(
            client,
            {"type": ServerMessageType.ERROR, "data": {"reason": reason}},
        )

    def _kick(self, client: ConnectedClient, reason: str) -> None:
        """Sends an `KICK` message type to the client, then disconnects them."""
        self._send_and_disconnect(
            client,
            {
                "type": ServerMessageType.KICK,
                "data": {"reason": reason},
            },
        )
