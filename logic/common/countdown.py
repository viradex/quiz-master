"""
countdown.py

The logic respective to the common countdown screen.
"""

from core.services.app_context import Services
from logic.base_logic import BaseLogic
from ui.screens.common.countdown import CommonCountdownScreen


class CommonCountdownLogic(BaseLogic):
    """
    Creates the countdown logic class, inheriting BaseLogic. This logic is part of the 'common' category.

    This logic class is a stub; it does not do anything. However, the class is required to exist, as otherwise
    the screen factory will fail.

    Arguments:
        screen: The screen respective to this logic class, to allow listening to signals from it and invoking
            methods to modify the UI.

        services: All the application Services, to allow access to various functions of the application
            in one single wrapper class.
    """

    def __init__(self, screen: CommonCountdownScreen, services: Services) -> None:
        super().__init__()
        self.screen: CommonCountdownScreen = screen
        self.services: Services = services
