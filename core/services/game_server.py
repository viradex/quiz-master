import socket
import threading
import time
from PyQt6.QtCore import QObject, pyqtSignal

from core.services.network.connected_client import ConnectedClient
from core.services.network.types import ClientMessageType, ServerMessageType
from core.game.quiz_manager import QuizManager
from models.player import Player
from core.config.constants import PORT, MAX_PLAYERS, RESPONSE_TIMEOUT


class GameServer(QObject):
    starting = pyqtSignal()
    start_fail = pyqtSignal(str)
    start_success = pyqtSignal()

    player_joined = pyqtSignal(str)
    player_left = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.host_ip = "0.0.0.0"  # listens to all network interfaces
        self.port = PORT
        self.is_running = False

        self.server_socket = None
        self.connected_players: dict[str, ConnectedClient] = {}
        self.quiz_manager = QuizManager()
        self.max_players = MAX_PLAYERS

        # ALWAYS USE "with self.lock" to avoid deadlocks
        self.lock = threading.Lock()

        self.handlers = {
            ClientMessageType.PING: self.handle_ping,
            ClientMessageType.JOIN_LOBBY: self.handle_join_lobby,
            ClientMessageType.LEAVE_LOBBY: self.handle_leave_lobby,
            ClientMessageType.PLAYER_LIST: self.handle_player_list,
        }

    def get_id_from_nickname(self, nickname):
        with self.lock:
            connected_players = list(self.connected_players.items())

        for player_id, client in connected_players:
            if client.nickname == nickname:
                return player_id

        return None

    def get_player_address(self, player_id):
        with self.lock:
            client = self.connected_players.get(player_id)

        if client:
            return client.socket.getpeername()

        return None

    def start(self):
        self.starting.emit()
        print(f"Starting server on {self.host_ip}:{self.port}...")

        threading.Thread(target=self._start_and_listen, daemon=True).start()

    def stop(self):
        if self.server_socket is None:
            raise ValueError("Server cannot be stopped without active socket")

        self.broadcast(
            {"type": ServerMessageType.KICK, "data": {"reason": "Server closed"}}
        )

        with self.lock:
            connected_players = list(self.connected_players.values())
            self.connected_players.clear()

        for client in connected_players:
            try:
                client.close()
            except OSError:
                continue

        self.is_running = False
        self.server_socket.close()

    def _start_and_listen(self):
        try:
            # TCP protocol
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((self.host_ip, self.port))
        except OSError as e:
            print("Failed to start!")

            # Address in use
            if e.errno == 10048:
                self.start_fail.emit("in_use")
                return
            else:
                # technically, start_fail could be emitted,
                # but it would be pointless due to the 'raise'
                raise

        print("Started successfully!")
        self.is_running = True

        self.start_success.emit()
        self.server_socket.listen()

        self.start_client_watchdog()
        self.accept_clients()

    def accept_clients(self):
        while self.is_running:
            try:
                client, addr = self.server_socket.accept()
            except OSError:
                break

            threading.Thread(
                target=self.handle_client, args=(client, addr), daemon=True
            ).start()

    def start_client_watchdog(self):
        threading.Thread(target=self._client_watchdog_loop, daemon=True).start()

    def _client_watchdog_loop(self):
        while self.is_running:
            time.sleep(1)

            with self.lock:
                connected_players = list(self.connected_players.values())

            for client in connected_players:
                if time.monotonic() - client.last_seen > RESPONSE_TIMEOUT:
                    self._kick(client, "Client timeout")

    def broadcast(self, msg):
        with self.lock:
            connected_players = list(self.connected_players.values())

        for client in connected_players:
            try:
                client.send(msg)
            except OSError:
                self._kick(client, "Failed to broadcast")

    def kick_player(self, player_id, reason):
        with self.lock:
            client = self.connected_players.get(player_id)

        if client:
            self._kick(client, reason)

    def remove_client(self, player_id):
        with self.lock:
            client = self.connected_players.pop(player_id, None)

        if client is None:
            return

        self.player_left.emit(client.nickname)

        self.broadcast(
            {
                "type": ServerMessageType.PLAYER_LEFT,
                "data": {"nickname": client.nickname},
            }
        )

        client.close()

    def handle_client(self, sock, addr):
        client = ConnectedClient(sock)

        try:
            while self.is_running:
                msg = client.recv()

                if msg is None:
                    print(f"Client {addr[0]}:{addr[1]} disconnected")
                    break

                self.handle_message(client, msg)
        except OSError:
            pass
        finally:
            if client.player:
                self.remove_client(client.player_id)
            else:
                client.close()

    def handle_message(self, client, msg):
        msg_type = msg.get("type")

        if msg_type is None:
            print(f"'type' key was not present in message, received: {msg}")
            self._error(client, "Message type missing")
            return

        handler = self.handlers.get(msg_type)

        if handler is None:
            print(f"The msg_type {msg_type} did not match any types (server)")
            self._error(client, "Unknown message type")
            return

        client.update_last_seen()
        handler(client, msg)

    def handle_ping(self, client, msg):
        # print(f"Received ping from {connection.addr[0]}:{connection.addr[1]}")
        client.send({"type": ServerMessageType.PONG})

    def handle_join_lobby(self, client, msg):
        try:
            player_id = msg["data"]["player_id"]
            nickname = msg["data"]["nickname"]
        except KeyError:
            print(f"Invalid data in message, received: {msg}")
            self._error(client, "Missing player ID/nickname")
            return

        kick_reason = None
        invalid_action = None

        with self.lock:
            if len(self.connected_players) + 1 > self.max_players:
                print(
                    f"Player {nickname} with ID {player_id} cannot connect (server full)"
                )
                self._kick(client, "Server is full")
                return

            for existing in self.connected_players.values():
                if existing.nickname == nickname:
                    print(f"Player with nickname {nickname} already exists")
                    kick_reason = f'The nickname "{nickname}" is already in use'
                    return

                elif existing.player_id == player_id:
                    print(f"Player with ID {player_id} already exists")
                    invalid_action = "Duplicate ID entered"
                    kick_reason = "The player ID matches an existing ID"
                    return

            if kick_reason is None:
                player = Player(player_id, nickname)
                client.player = player
                self.connected_players[player_id] = client

        if invalid_action:
            client.send(
                {
                    "type": ServerMessageType.INVALID_ACTION,
                    "data": {"reason": invalid_action},
                }
            )

        if kick_reason:
            self._kick(client, kick_reason)
            return

        print(f"Player {nickname} with ID {player_id} joined!")
        self.broadcast(
            {
                "type": ServerMessageType.PLAYER_JOINED,
                "data": {"nickname": nickname},
            }
        )

        client.send({"type": ServerMessageType.CONNECTION_SUCCESSFUL})
        self.player_joined.emit(nickname)

    def handle_leave_lobby(self, client, msg):
        if client.player:
            self.remove_client(client.player_id)
        else:
            client.close()

    def handle_player_list(self, client, msg):
        with self.lock:
            connected_players = list(self.connected_players.values())

        player_list = [c.nickname for c in connected_players]

        client.send(
            {
                "type": ServerMessageType.PLAYER_LIST,
                "data": {"player_list": player_list},
            }
        )

    def _send_and_disconnect(self, client, msg):
        try:
            client.send(msg)
        finally:
            if client.player is not None:
                self.remove_client(client.player_id)

            client.close()

    def _error(self, client, reason):
        self._send_and_disconnect(
            client,
            {"type": ServerMessageType.ERROR, "data": {"reason": reason}},
        )

    def _kick(self, client, reason):
        self._send_and_disconnect(
            client,
            {
                "type": ServerMessageType.KICK,
                "data": {"reason": reason},
            },
        )
