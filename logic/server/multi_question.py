from logic.base_logic import BaseLogic


class ServerMultiQuestionLogic(BaseLogic):
    def __init__(self, screen, services) -> None:
        super().__init__()
        self.screen = screen
        self.services = services
