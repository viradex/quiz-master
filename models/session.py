"""
session.py

Allows representation of both a player and client connection simultaneously within the server's
registry.
"""

from dataclasses import dataclass

from core.services.network.connected_client import ConnectedClient
from models.player import Player


@dataclass
class Session:
    """
    Creates a wrapper class that represents a session of a client on the server, by storing both the
    Player and ConnectedClient together, for storing in the server's player registry. A Session is useful
    to prevent the Player and ConnectedClients storage becoming out of sync, and allows easy access to
    both instances from a single wrapper.

    Arguments:
        player: The Player to store within this Session.

        client: The ConnectedClient to store within this Session.
    """

    player: Player
    client: ConnectedClient
