from core.services.app_context import Services
from logic.base_logic import BaseLogic
from ui.screens.common.about import CommonAboutScreen


# This logic class must exist, despite it being blank, else the screen-logic factory will fail
class CommonAboutLogic(BaseLogic):
    def __init__(self, screen, services) -> None:
        super().__init__()
        self.screen: CommonAboutScreen = screen
        self.services: Services = services
