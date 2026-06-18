from logic.base_logic import BaseLogic


class ServerFinalResultLogic(BaseLogic):
    def __init__(self, screen, services):
        super().__init__()
        self.screen = screen
        self.services = services
