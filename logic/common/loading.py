from ui.screens.common.loading import CommonLoadingScreen
from logic.base_logic import BaseLogic
from core.services.app_context import Services


class CommonLoadingLogic(BaseLogic):
    def __init__(self, screen, services) -> None:
        super().__init__()
        self.screen: CommonLoadingScreen = screen
        self.services: Services = services
