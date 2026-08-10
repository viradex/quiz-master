"""
setup.py

The logic respective to the client networking setup screen.
"""

from core.app.enums import ClientConnectionError
from core.app.screen_ids import Screen
from core.services.app_context import Services
from core.services.game_client import GameClient
from logic.base_logic import BaseLogic
from ui.screens.client.setup import ClientSetupScreen
from utils.error_messages import CLIENT_CONNECTION_ERROR_MESSAGES


class ClientSetupLogic(BaseLogic):
    """
    Creates the client connection setup logic class, inheriting BaseLogic. This logic is part of the 'client'
    category.

    This logic class is responsible for setting the IP address and nickname on the GameClient, and attempting
    a connection to the remote game server.

    Arguments:
        screen: The screen respective to this logic class, to allow listening to signals from it and invoking
            methods to modify the UI.

        services: All the application Services, to allow access to various functions of the application
            in one single wrapper class.
    """

    def __init__(self, screen: ClientSetupScreen, services: Services) -> None:
        super().__init__()
        self.screen: ClientSetupScreen = screen
        self.game_client: GameClient = services.client

        # Screen PyQt signal connections
        self.screen.submitted.connect(self._on_submitted)

        # Client PyQt signal connections
        self.game_client.connected.connect(self._on_connected)
        self.game_client.connection_failed.connect(self._on_connection_failed)

    def _on_submitted(self, data: dict[str, str]) -> None:
        """
        Internal method. Intended to be called when the user submits the data required to connect to the server.

        The data provided is assumed to have already been properly validated. The data is set on the GameClient
        and the server is attempted to be connected to using those details, while showing the loading screen.

        Arguments:
            data: A dictionary containing all the information needed for to connect to the server. Currently,
                this is the 'ip_address' and 'nickname' keys, which are both expected to have string values.
                A dictionary is used to store multiple values.

        Returns:
            None.
        """
        # If the data hasn't been validated, its consequences will be felt here...
        self.game_client.set_ip_address(data["ip_address"])
        self.game_client.set_nickname(data["nickname"])

        # Attempts to connect to the server, showing the loading screen in the meanwhile
        self.game_client.connect()
        self.screen.set_status("Connecting to server...")

        self.screen.go_to(
            Screen.COMMON_LOADING,
            {"loading_msg": "Connecting...", "status_msg": "Connecting to server..."},
        )

    def _on_connected(self) -> None:
        """
        Internal method. Intended to be called when the client successfully connects to the server.

        Shows the lobby UI screen.

        Returns:
            None.
        """
        self.screen.go_to(Screen.CLIENT_LOBBY)
        self.screen.set_status("In lobby")

    def _on_connection_failed(self, reason: ClientConnectionError) -> None:
        """
        Internal method. Intended to be called when the client fails to connect to the server for any reason.

        The reason for the failure to connect is given as a ClientConnectionError enum, which is in term used
        to provide a user-friendly error message to the client explaining the issue in an error modal box. The
        screen is also reset back to the setup screen.

        Arguments:
            reason: The reason for the connection to fail, as a ClientConnectionError enum. An enum is used
                as it is more type-safe than a regular string and provides easier readability.

        Returns:
            None.
        """
        # Go from loading screen back to setup screen
        self.screen.go_to(Screen.CLIENT_SETUP)

        self.screen.reset_status()
        self.screen.set_status("Failed to connect", 5000)

        # Get and show error message box
        message = CLIENT_CONNECTION_ERROR_MESSAGES.get(
            reason, "An unknown error occurred."
        )

        self.screen.show_error(
            "Failed to Connect",
            f"Unable to connect to the server. {message} Please try again.",
        )
