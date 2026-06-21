import time

from models.player import Player
from core.services.network.transport import JSONSocket


class ConnectedClient:
    def __init__(self, sock, player=None):
        self.socket = sock
        self.jsock = JSONSocket(sock)

        self.player: Player = player

        self.last_seen = time.monotonic()

    @property
    def player_id(self):
        return self.player.player_id if self.player else None

    @property
    def nickname(self):
        return self.player.nickname if self.player else None

    def update_last_seen(self):
        self.last_seen = time.monotonic()

    def send(self, msg):
        self.jsock.send(msg)

    def recv(self):
        return self.jsock.recv()

    def close(self):
        try:
            self.socket.close()
        except OSError:
            pass
