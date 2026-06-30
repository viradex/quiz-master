from typing import TYPE_CHECKING

from core.services.app_context import Services

if TYPE_CHECKING:
    from ui.main_window import MainWindow


class CommonAppController:
    """Global common logic, connected to MainWindow."""

    def __init__(self, window: MainWindow, services: Services) -> None:
        super().__init__()
        self.window: MainWindow = window
        self.services: Services = services
