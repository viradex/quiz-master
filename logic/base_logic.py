from PyQt6.QtGui import QCloseEvent


class BaseLogic:
    """Base logic for all logic of the app."""

    def __init__(self) -> None:
        pass

    def on_enter(self, payload=None) -> None:
        pass

    def on_leave(self) -> None:
        pass

    def on_window_close(self, event: QCloseEvent) -> None:
        pass
