from core.services.game_client import GameClient
from core.services.game_server import GameServer


class Services:
    """Contains app services."""

    def __init__(self) -> None:
        self.client = GameClient()
        self.server = GameServer()
