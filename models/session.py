from dataclasses import dataclass

from core.services.network.connected_client import ConnectedClient
from models.player import Player


@dataclass
class Session:
    """Wrapper class that contains a player (Player) and client (ConnectedClient)."""

    player: Player
    client: ConnectedClient
