from ui.screens.common.quiz_editor import CommonQuizEditorScreen
from logic.base_logic import BaseLogic
from core.services.app_context import Services


class CommonQuizEditorLogic(BaseLogic):
    def __init__(self, screen, services) -> None:
        super().__init__()
        self.screen: CommonQuizEditorScreen = screen
        self.services: Services = services
