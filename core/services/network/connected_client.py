import time

from models.player import Player
from core.services.network.transport import JSONSocket


class ConnectedClient:
    def __init__(self, sock, player_id, player=None):
        self.socket = sock
        self.player_id = player_id
        self.jsock = JSONSocket(sock)

        self.player: Player = player
        self.last_seen = time.monotonic()

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
