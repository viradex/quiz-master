from core.services.app_context import Services
from logic.base_logic import BaseLogic
from ui.screens.client.disconnect import ClientDisconnectScreen


# This logic class must exist, despite it being blank, else the screen-logic factory will fail
class ClientDisconnectLogic(BaseLogic):
    def __init__(self, screen, services) -> None:
        super().__init__()
        self.screen: ClientDisconnectScreen = screen
        self.services: Services = services
