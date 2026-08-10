"""
client.py

Contains global application logic relating to the client part of the application.
"""

from typing import TYPE_CHECKING

from PyQt6.QtGui import QCloseEvent

from core.app.screen_ids import Screen
from core.services.app_context import Services
from core.services.game_client import GameClient
from models.payloads import QuestionPayload
from ui.components.dialog import confirm_warning

# Needed to avoid circular imports
if TYPE_CHECKING:
    from ui.main_window import MainWindow


class ClientAppController:
    """
    Contains global client-side logic, which is directly connected to MainWindow. Like other regular
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
        self.client: GameClient = services.client

        # Client PyQt signal connections
        self.client.countdown_started.connect(self._on_countdown_started)
        self.client.question_received.connect(self._on_question_received)
        self.client.kicked.connect(self._on_kicked)
        self.client.error_occurred.connect(self._on_error_occurred)
        self.client.invalid_action_occurred.connect(self._on_invalid_action_occurred)

    def _on_countdown_started(self, duration: int) -> None:
        """
        Internal method. Intended to be called when the question countdown has begun.

        The countdown screen is displayed with the duration configured.

        Arguments:
            duration: A positive integer for the duration in seconds that the countdown should last for. An
                integer is used as it represents whole numbers well, as the duration does not need decimal
                precision.

        Returns:
            None.
        """
        self.window.go_to(Screen.COMMON_COUNTDOWN, {"duration": duration * 1000})
        self.window.set_status("Counting down...")

    def _on_question_received(self, data: dict) -> None:
        """
        Internal method. Intended to be called when the question has begun and the question data has been
        received.

        The question screen is displayed with the data provided, which is turned into a QuestionPayload.

        Arguments:
            data: A dictionary containing all the information needed for to display question information.
                A dictionary is used to store multiple values and allow easier conversion to the data transfer
                object payload.

        Returns:
            None.
        """
        # Listens for a question received here rather than in countdown logic as
        # countdown logic is shared between the client and server, so adding a
        # listener there would have been messy.

        # Multi-question screen expects a QuestionPayload object
        self.window.go_to(Screen.CLIENT_MULTI_QUESTION, QuestionPayload.from_dict(data))
        self.window.set_status("Waiting for answer")

    def _on_kicked(self, reason: str) -> None:
        """
        Internal method. Intended to be called when the client has been kicked from the server.

        The disconnect screen is displayed with the reason given for the kick.

        Arguments:
            reason: The reason for the client being kicked. A string is used to allow variety in the message
                provided.

        Returns:
            None.
        """
        self.window.reset_status()
        self.window.set_status("Disconnected from server", 5000)

        self.window.go_to(Screen.CLIENT_DISCONNECT, {"reason": reason})

    def _on_error_occurred(self, reason: str, from_who: str) -> None:
        """
        Internal method. Intended to be called when the client has been kicked from the server due to a
        protocol error.

        The disconnect screen is displayed with the reason given for the disconnect, as well as an error modal
        window.

        Arguments:
            reason: The reason for the client being disconnected. A string is used to allow variety in the
                message provided.

            from_who: The side that terminated the connection (not the side that the error occurred on),
                which can be either "client" or "server" as a string. A string is used rather than a boolean
                as a string is more descriptive.

        Returns:
            None.

        Raises:
            ValueError: If the 'from_who' argument is not "client" or "server".
        """
        if from_who not in ("client", "server"):
            raise ValueError(f"Invalid 'from_who': {from_who}")

        self.window.reset_status()
        self.window.set_status("Disconnected from server (fatal error)", 5000)

        # Show error modal box since this is a more serious issue than a regular disconnection
        self.window.go_to(Screen.CLIENT_DISCONNECT, {"reason": reason})
        self.window.show_error(
            "Protocol Error",
            f"The connection was terminated by the {from_who} due to a fatal communication error.\n\nReason: {reason}",
        )

    def _on_invalid_action_occurred(self, reason: str) -> None:
        """
        Internal method. Intended to be called when the client has been warned about performing an invalid
        action on the server (when the request was valid, but not in the current state of the server).

        A warning modal box is shown over whatever the current screen is.

        Arguments:
            reason: The reason for the client being warned. A string is used to allow variety in the message
                provided.

        Returns:
            None.
        """
        self.window.set_status("Invalid action rejected by server", 5000)

        self.window.show_warning(
            "Invalid Action",
            f"The server rejected the request because it is not valid in the current state.\n\nReason: {reason}",
        )

    def on_window_close(self, event: QCloseEvent) -> None:
        """
        Called by MainWindow when the window is about to be closed. For example, if the user presses the close
        button or Alt+F4 on Windows.

        Ensures the user wants to disconnect from the server through a warning modal box question. If the user
        accepts leaving, the close event is accepted. Otherwise, it is ignored. Only warns the user if the
        client is connected.

        Arguments:
            event: The close event to control whether the application can and should close or not.

        Returns:
            None.
        """
        # Only warn the user if the client is currently connected to the server
        if self.client.is_connected:
            confirm = confirm_warning(
                self.window,
                "Confirm Leaving",
                "Are you sure you want to disconnect from the server?",
            )

            if confirm:
                self.client.disconnect_client()
                event.accept()
            else:
                event.ignore()
