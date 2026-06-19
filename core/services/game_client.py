import socket
import threading
import secrets
from PyQt6.QtCore import QObject, pyqtSignal

from core.services.network.transport import JSONSocket
from core.services.network.types import ClientMessageType, ServerMessageType
from utils.networking import is_valid_ipv4
from core.config.constants import PORT, MAX_NICKNAME_LENGTH


class GameClient(QObject):
    connecting = pyqtSignal()
    connection_fail = pyqtSignal()
    connection_success = pyqtSignal()

    disconnecting = pyqtSignal(str)
    kick = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.server_ip = ""
        self.port = PORT
        self.is_connected = False
        self.jsock = JSONSocket()

        self.client_socket = None
        self.player_id = None
        self.nickname = None
        self.connection_status = None
        self.last_ping_time = None

    def set_ip(self, ip):
        if not is_valid_ipv4(ip):
            raise ValueError(f"IP '{ip}' is not a valid IPv4 address")

        self.server_ip = ip

    def set_nickname(self, nickname):
        if not nickname or len(nickname) > MAX_NICKNAME_LENGTH:
            raise ValueError(
                f"Nickname '{nickname}' exceeds length range: min 1 char, max {MAX_NICKNAME_LENGTH} chars"
            )

        self.nickname = nickname

    def set_random_player_id(self):
        player_token = secrets.token_hex(4)
        self.player_id = player_token

    def connect(self):
        if not self.server_ip or not self.nickname:
            raise ValueError("Server IP and nickname must have values")

        self.connecting.emit()
        print(f"Connecting to {self.server_ip}:{self.port}...")

        threading.Thread(target=self._connect_and_listen, daemon=True).start()

    def disconnect_client(self, msg=""):
        self.jsock.send(
            {"type": ClientMessageType.LEAVE_LOBBY, "data": {"reason": msg}}
        )
        self.disconnecting.emit(msg)
        self.client_socket.close()

    def listen(self):
        while True:
            msg = self.jsock.recv()

            if msg is None:
                break

            self.handle_message(msg)

    def _connect_and_listen(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.server_ip, self.port))

            self.jsock.set_socket(self.client_socket)
        except ConnectionRefusedError:
            print("Failed to connect!")
            self.connection_fail.emit()
            return

        print("Connected successfully!")
        self.is_connected = True

        self.send_join()
        self.listen()

    def handle_message(self, msg):
        if "type" not in msg:
            print(f"'type' key was not present in message, received: {msg}")
            self.disconnect_client(
                "Message type was not present in client-server network communication message"
            )
            return

        msg_type = msg["type"]

        if msg_type == ServerMessageType.CONNECTION_SUCCESSFUL:
            self.handle_connection_successful(msg)
        elif msg_type == ServerMessageType.KICK:
            self.handle_kick(msg)
        else:
            print(f"The msg_type {msg_type} did not match any types (client)")
            self.disconnect_client("Unknown message type")
            return

    def handle_connection_successful(self, msg):
        self.connection_success.emit()

    def handle_kick(self, msg):
        try:
            reason = msg["data"]["reason"]
        except KeyError:
            print(f"Invalid data in message, received: {msg}")
            self.disconnect_client("Invalid data in message")
            return

        self.kick.emit(reason)
        self.client_socket.close()

    def send_join(self):
        self.jsock.send(
            {
                "type": ClientMessageType.JOIN_LOBBY,
                "data": {"player_id": self.player_id, "nickname": self.nickname},
            }
        )
