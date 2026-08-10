"""
app_context.py

Provides a container for all main core objects for the application's logic.
"""

from core.game.game_controller import GameController
from core.services.game_client import GameClient
from core.services.game_server import GameServer
from data.quiz_repo import QuizRepository


class Services:
    """
    Acts as a dependency service container for all the core objects of the application's core. This class
    serves as a central location for the GameClient, GameServer, GameController, and QuizRepository without
    creating and/or passing multiple of these objects around.

    Typically, only one of this class should be created for the entire application.
    """

    def __init__(self) -> None:
        # Handles communication as a game client
        self.client = GameClient()

        # Handles communication as a game server
        self.server = GameServer()

        # Controls quiz game logic
        self.controller = GameController()

        # Provides access to quiz data
        self.quiz_repo = QuizRepository()
