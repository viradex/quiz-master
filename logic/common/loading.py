from ui.screens.common.loading import CommonLoadingScreen
from logic.base_logic import BaseLogic


class CommonLoadingLogic(BaseLogic):
    def __init__(self, screen, services):
        super().__init__()
        self.screen: CommonLoadingScreen = screen
