"""
final_result.py

The logic respective to the client final results screen.
"""

from core.services.app_context import Services
from logic.base_logic import BaseLogic
from ui.screens.client.final_result import ClientFinalResultScreen


class ClientFinalResultLogic(BaseLogic):
    """
    Creates the final results logic class, inheriting BaseLogic. This logic is part of the 'client' category.

    This logic class is a stub; it does not do anything. However, the class is required to exist, as otherwise
    the screen factory will fail.

    Arguments:
        screen: The screen respective to this logic class, to allow listening to signals from it and invoking
            methods to modify the UI.

        services: All the application Services, to allow access to various functions of the application
            in one single wrapper class.
    """

    def __init__(self, screen: ClientFinalResultScreen, services: Services) -> None:
        super().__init__()
        self.screen: ClientFinalResultScreen = screen
        self.services: Services = services
