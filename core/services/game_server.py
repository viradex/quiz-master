import socket
import threading
from PyQt6.QtCore import QObject, pyqtSignal

from core.services.network.transport import JSONSocket
from core.services.quiz_manager import QuizManager
from core.config.constants import PORT, MAX_PLAYERS


class GameServer(QObject):
    starting = pyqtSignal()
    start_fail = pyqtSignal(str)
    start_success = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.host_ip = "0.0.0.0"  # listens to all network interfaces
        self.port = PORT
        self.is_running = False
        self.jsock = JSONSocket()

        self.server_socket = None
        self.connected_clients = {}
        self.quiz_manager = QuizManager()
        self.max_players = MAX_PLAYERS

    def start(self):
        self.starting.emit()
        print(f"Starting server on {self.host_ip}:{self.port}...")

        thread = threading.Thread(target=self._start_and_listen, daemon=True)
        thread.start()

    def _start_and_listen(self):
        try:
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
