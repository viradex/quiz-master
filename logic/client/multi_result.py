"""
multi_results.py

The logic respective to the client multi-question results screen.
"""

from core.app.screen_ids import Screen
from core.services.app_context import Services
from core.services.game_client import GameClient
from logic.base_logic import BaseLogic
from models.payloads import ClientFinalResultsPayload
from ui.screens.client.multi_result import ClientMultiResultScreen


class ClientMultiResultLogic(BaseLogic):
    """
    Creates the multi-question results logic class, inheriting BaseLogic. This logic is part of the 'client'
    category.

    This logic class is responsible for displaying final results when they arrive, as well as disconnecting
    the client if and when they wish to leave the server.

    Arguments:
        screen: The screen respective to this logic class, to allow listening to signals from it and invoking
            methods to modify the UI.

        services: All the application Services, to allow access to various functions of the application
            in one single wrapper class.
    """

    def __init__(self, screen: ClientMultiResultScreen, services: Services) -> None:
        super().__init__()
        self.screen: ClientMultiResultScreen = screen
        self.game_client: GameClient = services.client

        # Screen PyQt signal connections
        self.screen.left_server.connect(self._on_left_server)

        # Client PyQt signal connections
        self.game_client.final_results_received.connect(self._on_final_results_received)

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

    def _on_final_results_received(self, data: dict) -> None:
        """
        Internal method. Intended to be called when the quiz game has ended and the final results data has
        been received.

        The final results screen is displayed with the data provided, which is turned into a ClientFinalResultsPayload.

        Arguments:
            data: A dictionary containing all the information needed for to display final results information.
                A dictionary is used to store multiple values and allow easier conversion to the data transfer
                object payload.

        Returns:
            None.
        """
        self.screen.set_status("Showing final results")
        self.screen.go_to(
            Screen.CLIENT_FINAL_RESULT, ClientFinalResultsPayload.from_dict(data)
        )
