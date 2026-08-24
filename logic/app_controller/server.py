"""
server.py

Contains global application logic relating to the server part of the application.
"""

from typing import TYPE_CHECKING

from PyQt6.QtGui import QCloseEvent

from core.app.screen_ids import Screen
from core.game.game_controller import GameController
from core.services.app_context import Services
from core.services.game_server import GameServer
from data.quiz_repo import QuizRepository
from models.payloads import QuestionPayload
from ui.components.dialog import confirm_warning

# Needed to avoid circular imports
if TYPE_CHECKING:
    from ui.main_window import MainWindow


class ServerAppController:
    """
    Contains global server-side logic, which is directly connected to MainWindow. Like other regular
    logic classes, this class has access to all the Services. Unlike other logic classes, however, it
    does not have access to one specific screen. It can still navigate to a screen, though.

    Arguments:
        window: The MainWindow of the application, to allow access to its public interface methods.

        services: All the application Services, to allow access to various functions of the application
            in one single wrapper class.
    """

    def __init__(self, window: "MainWindow", services: Services) -> None:
        super().__init__()
        self.window: MainWindow = window
        self.game_server: GameServer = services.server
        self.controller: GameController = services.controller
        self.quiz_repo: QuizRepository = services.quiz_repo

        # Server PyQt signal connections
        self.game_server.player_joined.connect(self._on_player_joined)
        self.game_server.player_left.connect(self._on_player_left)

        # Game controller PyQt signal connections
        self.controller.started_countdown.connect(self._on_started_countdown)
        self.controller.started_question.connect(self._on_started_question)
        self.controller.no_players_found.connect(self._on_no_players_found)

    def _on_player_joined(self, player_id: str, nickname: str) -> None:
        """
        Internal method. Intended to be called when a player joins the server.

        If a game is not currently running, the player is added to the quiz game controller.

        Arguments:
            player_id: A string describing the ID of the player that just joined. A string is used as it can
                flexibly store IDs and can store many characters to make them more unique.

            nickname: The nickname of the player that joined. A string is used as a nickname is easily
                represented by a string.

        Returns:
            None.
        """
        player = self.game_server.get_player(player_id)
        if player is None:
            return

        # Adds player to game controller for when the game starts. The add_player()
        # method only adds a player if the game is not already running.
        self.controller.add_player(player)
        self.window.set_status(f"{nickname} joined the game", 5000)

    def _on_player_left(self, player_id: str, nickname: str) -> None:
        """
        Internal method. Intended to be called when a player leaves the server.

        The player that left is removed from the quiz game controller, and the quiz game if it is currently
        running at the time of the player leaving.

        Arguments:
            player_id: A string describing the ID of the player that just left. A string is used as it can
                flexibly store IDs and can store many characters to make them more unique.

            nickname: The nickname of the player that left. A string is used as a nickname is easily
                represented by a string.

        Returns:
            None.
        """
        self.controller.remove_player(player_id)
        self.window.set_status(f"{nickname} left the game", 5000)

    def _on_started_countdown(self, duration: int) -> None:
        """
        Internal method. Intended to be called when the countdown begins from the game controller.

        Broadcasts the message that the countdown has begun to all clients, then displays the countdown on the
        server's UI screen.

        Arguments:
            duration: A positive integer for the duration in seconds that the countdown should last for. An
                integer is used as it represents whole numbers well, as the duration does not need decimal
                precision.

        Returns:
            None.
        """
        # Send countdown duration to all clients, then display on server UI
        self.game_server.send_countdown_start(duration)
        self.window.go_to(Screen.COMMON_COUNTDOWN, {"duration": duration * 1000})

        self.window.set_status("Counting down...")

    def _on_started_question(self, question_info: QuestionPayload) -> None:
        """
        Internal method. Intended to be called when the question has begun from the game controller.

        The question data is broadcast to all clients, and the server UI displays the question data itself as well.

        Arguments:
            question_info: The QuestionPayload containing all the details needed to display the question to
                the UI. A specialized payload class is used as the QuestionPayload contains many fields which
                a dictionary would have more issues with, for example key names.

        Returns:
            None.
        """
        # Listens for a question started here rather than in countdown logic as
        # countdown logic is shared between the client and server, so adding a
        # listener there would have been messy.

        # The server can only send dictionaries, not data transfer objects
        self.game_server.send_question_data(question_info.to_dict())
        self.window.go_to(Screen.SERVER_MULTI_QUESTION, question_info)

        self.window.set_status("In question")

    def _on_no_players_found(self) -> None:
        """
        Internal method. Intended to be called when the number of players in the server dips below the required
        amount of players needed to play the quiz game.

        Stops the server, which disconnects all clients, and shows a warning to the server UI about the game
        ending prematurely. Returns to the main menu screen.

        Returns:
            None.
        """
        self.window.reset_status()
        self.window.set_status("Game ended prematurely", 5000)

        # Disconnect all clients and show warning to host
        self.game_server.stop("Game over")
        self.window.show_warning(
            "Quiz Ended Early",
            "There are not enough players to continue the quiz, so the game has ended prematurely.",
        )

        self.window.go_to(Screen.COMMON_MENU)

    def on_window_close(self, event: QCloseEvent) -> None:
        """
        Called by MainWindow when the window is about to be closed. For example, if the user presses the close
        button or Alt+F4 on Windows.

        Ensures the user wants to disconnect from the server through a warning modal box question. If the user
        accepts leaving, the close event is accepted. Otherwise, it is ignored. Only warns the user if the
        server is running and there is at least one player currently connected.

        Arguments:
            event: The close event to control whether the application can and should close or not.

        Returns:
            None.
        """
        # Only warn the user if the server is currently running and there are players currently connected
        if self.game_server.is_running and self.game_server.get_total_players() > 0:
            confirm = confirm_warning(
                self.window,
                "Confirm Closing",
                "Are you sure you want to close the server? All players in the server will be disconnected.",
            )

            if confirm:
                self.game_server.stop()
                event.accept()
            else:
                event.ignore()
