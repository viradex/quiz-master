import socket
import threading
import secrets
from PyQt6.QtCore import QObject, pyqtSignal

from core.services.network.transport import JSONSocket
from utils.networking import is_valid_ipv4
from core.config.constants import PORT, MAX_NICKNAME_LENGTH


class GameClient(QObject):
    connecting = pyqtSignal()
    connection_fail = pyqtSignal()
    connection_success = pyqtSignal()

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
        if self.server_ip is None or self.nickname is None:
            raise ValueError("Server IP and nickname must have values")

        self.connecting.emit()
        print(f"Connecting to {self.server_ip}:{self.port}...")

        thread = threading.Thread(target=self._connect_and_listen, daemon=True)
        thread.start()

    def listen(self):
        while True:
            msg = self.jsock.recv()

            if msg is None:
                break

            # TODO temp
            print(msg)

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

        self.connection_success.emit()
        self.listen()
