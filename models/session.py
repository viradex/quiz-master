from dataclasses import dataclass

from models.player import Player
from core.services.network.connected_client import ConnectedClient


@dataclass
class Session:
    """Wrapper class that contains a player (Player) and client (ConnectedClient)."""

    player: Player
    client: ConnectedClient
