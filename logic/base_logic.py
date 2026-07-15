from PyQt6.QtGui import QCloseEvent


class BaseLogic:
    """Base logic for all logic of the app."""

    def on_enter(self, payload=None) -> None:
        """Called when the logic's respective screen is shown. The same payload given to the screen is also passed."""
        pass

    def on_leave(self) -> None:
        """Called when the logic's respective screen is hidden."""
        pass

    def on_window_close(self, event: QCloseEvent) -> None:
        """Called when the application is about to be closed."""
        pass
