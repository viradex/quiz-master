from ui.screens.common.countdown import CommonCountdownScreen
from logic.base_logic import BaseLogic
from core.services.app_context import Services


class CommonCountdownLogic(BaseLogic):
    def __init__(self, screen, services) -> None:
        super().__init__()
        self.screen: CommonCountdownScreen = screen
        self.services: Services = services
