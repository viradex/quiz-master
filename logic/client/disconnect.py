"""
disconnect.py

The logic respective to the client disconnection screen.
"""

from core.services.app_context import Services
from logic.base_logic import BaseLogic
from ui.screens.client.disconnect import ClientDisconnectScreen


class ClientDisconnectLogic(BaseLogic):
    """
    Creates the disconnect logic class, inheriting BaseLogic. This logic is part of the 'client' category.

    This logic class is a stub; it does not do anything. However, the class is required to exist, as otherwise
    the screen factory will fail.

    Arguments:
        screen: The screen respective to this logic class, to allow listening to signals from it and invoking
            methods to modify the UI.

        services: All the application Services, to allow access to various functions of the application
            in one single wrapper class.
    """

    def __init__(self, screen: ClientDisconnectScreen, services: Services) -> None:
        super().__init__()
        self.screen: ClientDisconnectScreen = screen
        self.services: Services = services
