from ui.screens.common.about import CommonAboutScreen
from logic.base_logic import BaseLogic
from core.services.app_context import Services


class CommonAboutLogic(BaseLogic):
    def __init__(self, screen, services) -> None:
        super().__init__()
        self.screen: CommonAboutScreen = screen
        self.services: Services = services
