import socket
import threading
from PyQt6.QtCore import QObject, pyqtSignal

from core.services.network.transport import JSONSocket
from core.services.network.types import ClientMessageType, ServerMessageType
from core.game.quiz_manager import QuizManager
from models.player import Player
from core.config.constants import PORT, MAX_PLAYERS


class GameServer(QObject):
    starting = pyqtSignal()
    start_fail = pyqtSignal(str)
    start_success = pyqtSignal()

    player_joined = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.host_ip = "0.0.0.0"  # listens to all network interfaces
        self.port = PORT
        self.is_running = False

        self.server_socket = None
        self.connected_clients = {}
        self.quiz_manager = QuizManager()
        self.max_players = MAX_PLAYERS

    def start(self):
        self.starting.emit()
        print(f"Starting server on {self.host_ip}:{self.port}...")

        threading.Thread(target=self._start_and_listen, daemon=True).start()

    def stop(self):
        if self.server_socket is None:
            raise ValueError("Server cannot be stopped without active socket")

        for player in list(self.connected_clients.values()):
            player.client_socket.close()

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

    def broadcast(self, msg):
        for client in self.connected_clients.values():
            try:
                client.jsock.send(msg)
            except OSError:
                pass

    def _send_and_disconnect(self, client, jsock, msg):
        try:
            jsock.send(msg)
        finally:
            client.close()

    def _error(self, client, jsock, reason):
        self._send_and_disconnect(
            client, jsock, {"type": ServerMessageType.ERROR, "data": {"reason": reason}}
        )

    def _kick(self, client, jsock, reason):
        self._send_and_disconnect(
            client,
            jsock,
            {
                "type": (ServerMessageType.KICK),
                "data": {"reason": reason},
            },
        )

    def handle_client(self, client, addr):
        jsock = JSONSocket(client)

        try:
            while self.is_running:
                msg = jsock.recv()

                if msg is None:
                    print(f"Client {addr} disconnected")
                    break

                self.handle_message(client, jsock, msg)
        except OSError:
            pass
        finally:
            for player_id, player in list(self.connected_clients.items()):
                if player.client_socket == client:
                    del self.connected_clients[player_id]
                    break

            client.close()

    def handle_message(self, client, jsock, msg):
        if "type" not in msg:
            print(f"'type' key was not present in message, received: {msg}")
            self._error(
                client,
                jsock,
                "Message type was not present in client-server network communication message",
            )
            return

        msg_type = msg["type"]

        if msg_type == ClientMessageType.JOIN_LOBBY:
            self.handle_join_lobby(client, jsock, msg)
        else:
            print(f"The msg_type {msg_type} did not match any types (server)")
            self._error(client, jsock, "Unknown message type")
            return

    def handle_join_lobby(self, client, jsock, msg):
        try:
            player_id = msg["data"]["player_id"]
            nickname = msg["data"]["nickname"]
        except KeyError:
            print(f"Invalid data in message, received: {msg}")
            self._error(client, jsock, "Invalid data in message")
            return

        if len(self.connected_clients) + 1 > self.max_players:
            print(f"Player {nickname} with ID {player_id} cannot connect (server full)")
            self._kick(client, jsock, "Server is full")
            return

        for connected_client in self.connected_clients.values():
            if connected_client.nickname == nickname:
                print(f"Player with nickname {nickname} already exists")
                self._kick(
                    client,
                    jsock,
                    f'The nickname "{nickname}" is already in use.',
                )
                return
            elif connected_client.player_id == player_id:
                print(f"Player with ID {player_id} already exists")
                self._kick(client, jsock, "The player ID matches an existing ID")
                return

        print(f"Player {nickname} with ID {player_id} joined!")
        self.broadcast(
            {"type": ServerMessageType.PLAYER_JOINED, "data": {"nickname": nickname}}
        )

        self.connected_clients[player_id] = Player(player_id, nickname, client, jsock)
        jsock.send({"type": ServerMessageType.CONNECTION_SUCCESSFUL})
        self.player_joined.emit(nickname)
