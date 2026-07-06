from core.services.app_context import Services

from typing import TYPE_CHECKING

# Needed to avoid circular imports
if TYPE_CHECKING:
    from ui.main_window import MainWindow


class CommonAppController:
    """Global common logic, connected to MainWindow."""

    def __init__(self, window, services) -> None:
        super().__init__()
        self.window: MainWindow = window
        self.services: Services = services
