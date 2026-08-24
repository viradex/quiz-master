"""
multi_question.py

The logic respective to the client multi-question screen.
"""

from core.app.screen_ids import Screen
from core.services.app_context import Services
from core.services.game_client import GameClient
from logic.base_logic import BaseLogic
from models.payloads import ClientResultsPayload
from ui.screens.client.multi_question import ClientMultiQuestionScreen


class ClientMultiQuestionLogic(BaseLogic):
    """
    Creates the multi-question logic class, inheriting BaseLogic. This logic is part of the 'client' category.

    This logic class is responsible for sending answer submissions to the client, as well as disconnecting
    the client if and when they wish to leave the server.

    Arguments:
        screen: The screen respective to this logic class, to allow listening to signals from it and invoking
            methods to modify the UI.

        services: All the application Services, to allow access to various functions of the application
            in one single wrapper class.
    """

    def __init__(self, screen: ClientMultiQuestionScreen, services: Services) -> None:
        super().__init__()
        self.screen: ClientMultiQuestionScreen = screen
        self.game_client: GameClient = services.client

        # Screen PyQt signal connections
        self.screen.answer_submitted.connect(self._on_answer_submitted)
        self.screen.left_server.connect(self._on_left_server)

        # Client PyQt signal connections
        self.game_client.results_received.connect(self._on_results_received)

    def _on_answer_submitted(self, index: int) -> None:
        """
        Internal method. Intended to be called when the user submits an answer to the question.

        Sends the selected answer index to the server, only if the screen was not in preview mode.

        Arguments:
            index: A zero-based integer index for the answer that the player wishes to submit for the current
                question, respective to the answer options. An integer is used as that is used for indexes in
                iterables, for example.

        Returns:
            None.
        """
        if self.screen.is_preview:
            return

        self.game_client.send_answer_submit(index)
        self.screen.set_status("Answer submitted")

    def _on_left_server(self) -> None:
        """
        Internal method. Intended to be called when the user wishes to leave the server.

        Disconnects the user from the server and displays the main menu screen.

        Returns:
            None.
        """
        self.game_client.disconnect_client()
        self.screen.go_to(Screen.COMMON_MENU)

        self.screen.reset_status()
        self.screen.set_status("Disconnected from server", 2000)

    def _on_results_received(self, data: dict) -> None:
        """
        Internal method. Intended to be called when the question has ended and the question results data has
        been received.

        The question results screen is displayed with the data provided, which is turned into a ClientResultsPayload.

        Arguments:
            data: A dictionary containing all the information needed for to display results information.
                A dictionary is used to store multiple values and allow easier conversion to the data transfer
                object payload.

        Returns:
            None.
        """
        try:
            payload = ClientResultsPayload.from_dict(data)
        except ValueError:
            self.game_client.disconnect_error("Invalid results payload format")
            return

        self.screen.set_status("Showing results")
        self.screen.go_to(Screen.CLIENT_MULTI_RESULT, payload)
