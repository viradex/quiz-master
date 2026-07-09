from ui.screens.common.menu import CommonMenuScreen
from logic.base_logic import BaseLogic
from core.services.app_context import Services


class CommonQuizManagerLogic(BaseLogic):
    def __init__(self, screen, services) -> None:
        super().__init__()
        self.screen: CommonMenuScreen = screen
        self.services: Services = services
