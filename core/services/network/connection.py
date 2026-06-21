from dataclasses import dataclass
from core.services.network.transport import JSONSocket


@dataclass
class ClientConnection:
    socket: object
    jsock: JSONSocket
    addr: tuple
    player_id: str | None = None

    def send(self, msg):
        self.jsock.send(msg)
