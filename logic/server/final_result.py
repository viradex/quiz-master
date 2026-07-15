from core.services.app_context import Services
from logic.base_logic import BaseLogic
from ui.screens.server.final_result import ServerFinalResultScreen


# This logic class must exist, despite it being blank, else the screen-logic factory will fail
class ServerFinalResultLogic(BaseLogic):
    def __init__(self, screen, services) -> None:
        super().__init__()
        self.screen: ServerFinalResultScreen = screen
        self.services: Services = services
