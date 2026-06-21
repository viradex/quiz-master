import socket
import threading
import secrets
import time
from PyQt6.QtCore import QObject, pyqtSignal

from core.services.network.connected_client import ConnectedClient
from core.services.network.player_registry import PlayerRegistry
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
        self.quiz_manager = QuizManager()
        self.player_registry = PlayerRegistry()

        self.handlers = {
            ClientMessageType.PING: self.handle_ping,
            ClientMessageType.JOIN_LOBBY: self.handle_join_lobby,
            ClientMessageType.LEAVE_LOBBY: self.handle_leave_lobby,
            ClientMessageType.PLAYER_LIST: self.handle_player_list,
        }

    def get_id_from_nickname(self, nickname):
        return self.player_registry.get_id_by_nickname(nickname)

    def get_player_address(self, player_id):
        client = self.player_registry.get_player(player_id)

        if client:
            return client.socket.getpeername()

        return None

    def create_random_player_id(self):
        return secrets.token_hex(4)

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

        connected_players = self.player_registry.get_players().values()
        self.player_registry.clear_players()

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

            connected_players = self.player_registry.get_players().values()

            for client in connected_players:
                if time.monotonic() - client.last_seen > RESPONSE_TIMEOUT:
                    self._kick(client, "Client timeout")

    def broadcast(self, msg):
        connected_players = self.player_registry.get_players().values()

        for client in connected_players:
            try:
                client.send(msg)
            except OSError:
                self._kick(client, "Failed to broadcast")

    def kick_player(self, player_id, reason):
        client = self.player_registry.get_player(player_id)

        if client:
            self._kick(client, reason)

    def remove_client(self, player_id):
        client = self.player_registry.get_player(player_id)

        if client is None:
            return

        self.player_registry.remove_player(player_id)
        self.player_left.emit(client.nickname)

        self.broadcast(
            {
                "type": ServerMessageType.PLAYER_LEFT,
                "data": {"nickname": client.nickname},
            }
        )

        client.close()

    def handle_client(self, sock, addr):
        client = ConnectedClient(sock, self.create_random_player_id())

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
            self.remove_client(client.player_id)

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
            nickname = msg["data"]["nickname"]
        except KeyError:
            print(f"Invalid data in message, received: {msg}")
            self._error(client, "Missing player nickname")
            return

        status, player = self.player_registry.add_player(nickname, client)

        if status == "lobby_full":
            self._kick(client, "Server is full")
            return
        elif status == "dupe_nickname":
            self._kick(client, f'The nickname "{nickname}" is already in use')
            return
        elif status == "dupe_id":
            self._kick(client, "The player ID generated matches an existing ID")
            return

        print(f"Player {nickname} with ID {client.player_id} joined!")

        client.player = player
        self.player_joined.emit(nickname)

        self.broadcast(
            {
                "type": ServerMessageType.PLAYER_JOINED,
                "data": {"nickname": nickname},
            }
        )

        client.send(
            {
                "type": ServerMessageType.CONNECTION_SUCCESSFUL,
                "data": {"player_id": client.player_id},
            }
        )

    def handle_leave_lobby(self, client, msg):
        self.remove_client(client.player_id)

    def handle_player_list(self, client, msg):
        connected_players = self.player_registry.get_players().values()

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
