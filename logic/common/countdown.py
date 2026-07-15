from core.services.app_context import Services
from logic.base_logic import BaseLogic
from ui.screens.common.countdown import CommonCountdownScreen


# This logic class must exist, despite it being blank, else the screen-logic factory will fail
class CommonCountdownLogic(BaseLogic):
    def __init__(self, screen, services) -> None:
        super().__init__()
        self.screen: CommonCountdownScreen = screen
        self.services: Services = services
