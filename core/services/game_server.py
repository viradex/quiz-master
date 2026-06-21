import socket
import threading
import time
from PyQt6.QtCore import QObject, pyqtSignal

from core.services.network.transport import JSONSocket
from core.services.network.connection import ClientConnection
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
        self.connected_players = {}
        self.quiz_manager = QuizManager()
        self.max_players = MAX_PLAYERS

        self.handlers = {
            ClientMessageType.PING: self.handle_ping,
            ClientMessageType.JOIN_LOBBY: self.handle_join_lobby,
        }

    def get_id_from_nickname(self, nickname):
        for player_id, player in self.connected_players.items():
            if player.nickname == nickname:
                return player_id

        return None

    def get_player_address(self, player_id):
        if player_id is not None:
            return self.connected_players[player_id].connection.addr

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

        for player in list(self.connected_players.values()):
            try:
                player.connection.socket.close()
            except OSError:
                continue

        self.is_running = False
        self.server_socket.close()
        self.connected_players.clear()

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

            for client in list(self.connected_players.values()):
                if time.monotonic() - client.last_seen > RESPONSE_TIMEOUT:
                    self._kick(client.connection, "Client timeout")

    def broadcast(self, msg):
        for player in self.connected_players.values():
            try:
                player.connection.send(msg)
            except OSError:
                pass

    def kick_player(self, player_id, reason):
        self._kick(self.connected_players[player_id].connection, reason)

    def remove_client(self, client):
        for player_id, player in list(self.connected_players.items()):
            if player.connection.socket == client:
                nickname = player.nickname
                self.player_left.emit(nickname)

                del self.connected_players[player_id]
                break

    def handle_client(self, client, addr):
        jsock = JSONSocket(client)
        connection = ClientConnection(client, jsock, addr)

        try:
            while self.is_running:
                msg = jsock.recv()

                if msg is None:
                    print(f"Client {addr[0]}:{addr[1]} disconnected")
                    break

                self.handle_message(connection, msg)
        except OSError:
            pass
        finally:
            self.remove_client(client)
            client.close()

    def handle_message(self, connection, msg):
        msg_type = msg.get("type")

        if msg_type is None:
            print(f"'type' key was not present in message, received: {msg}")
            self._error(connection, "Message type missing")
            return

        handler = self.handlers.get(msg_type)

        if handler is None:
            print(f"The msg_type {msg_type} did not match any types (server)")
            self._error(connection, "Unknown message type")
            return

        player = self.connected_players.get(connection.player_id)
        if player:
            player.last_seen = time.monotonic()

        handler(connection, msg)

    def handle_ping(self, connection, msg):
        # print(f"Received ping from {connection.addr[0]}:{connection.addr[1]}")
        connection.send({"type": ServerMessageType.PONG})

    def handle_join_lobby(self, connection, msg):
        try:
            player_id = msg["data"]["player_id"]
            nickname = msg["data"]["nickname"]
        except KeyError:
            print(f"Invalid data in message, received: {msg}")
            self._error(connection, "Missing player ID/nickname")
            return

        if len(self.connected_players) + 1 > self.max_players:
            print(f"Player {nickname} with ID {player_id} cannot connect (server full)")
            self._kick(connection, "Server is full")
            return

        for connected_client in self.connected_players.values():
            if connected_client.nickname == nickname:
                print(f"Player with nickname {nickname} already exists")
                self._kick(connection, f'The nickname "{nickname}" is already in use.')
                return

            elif connected_client.player_id == player_id:
                print(f"Player with ID {player_id} already exists")
                connection.send(
                    {
                        "type": ServerMessageType.INVALID_ACTION,
                        "data": {"reason": "Duplicate ID entered"},
                    }
                )

                self._kick(connection, "The player ID matches an existing ID")
                return

        print(f"Player {nickname} with ID {player_id} joined!")
        self.broadcast(
            {"type": ServerMessageType.PLAYER_JOINED, "data": {"nickname": nickname}}
        )

        self.connected_players[player_id] = Player(player_id, nickname, connection)
        self.connected_players[player_id].last_seen = time.monotonic()

        connection.player_id = player_id

        connection.send({"type": ServerMessageType.CONNECTION_SUCCESSFUL})
        self.player_joined.emit(nickname)

    def _send_and_disconnect(self, connection, msg):
        try:
            connection.send(msg)
        finally:
            connection.socket.close()

    def _error(self, connection, reason):
        self._send_and_disconnect(
            connection,
            {"type": ServerMessageType.ERROR, "data": {"reason": reason}},
        )

    def _kick(self, connection, reason):
        self._send_and_disconnect(
            connection,
            {
                "type": (ServerMessageType.KICK),
                "data": {"reason": reason},
            },
        )
