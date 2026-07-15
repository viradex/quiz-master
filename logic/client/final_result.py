from core.services.app_context import Services
from logic.base_logic import BaseLogic
from ui.screens.client.final_result import ClientFinalResultScreen


# This logic class must exist, despite it being blank, else the screen-logic factory will fail
class ClientFinalResultLogic(BaseLogic):
    def __init__(self, screen, services) -> None:
        super().__init__()
        self.screen: ClientFinalResultScreen = screen
        self.services: Services = services
