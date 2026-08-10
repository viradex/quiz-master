"""
base_logic.py

The definition for a base definition of a logic in this application. All logic classes are expected
to inherit BaseLogic.

Contains lifecycle methods that are called when certain events happen within higher levels of the
application.
"""

from PyQt6.QtGui import QCloseEvent


class BaseLogic:
    """
    Creates a base logic. This class is used as the blueprint for all logic classes in the application.
    All logic classes are expected to inherit BaseLogic.

    This class provides lifecycle functions which are called automatically when certain events occur,
    such as the logic's respective screen being shown and hidden. The lifecycle methods are stubs, intended
    to be overwritten by inheriting classes.
    """

    def on_enter(self, payload: object | None = None) -> None:
        """
        Called when the logic's respective screen becomes active and displayed, with an optional payload.

        Arguments:
            payload: The optional payload that is provided after switching.

        Returns:
            None.
        """
        # Stub method; can be overwritten by inheriting classes
        pass

    def on_leave(self) -> None:
        """
        Called when the logic's respective screen becomes inactive and hidden visually.

        Returns:
            None.
        """
        # Stub method; can be overwritten by inheriting classes
        pass

    def on_window_close(self, event: QCloseEvent) -> None:
        """
        Called when the window is about to be closed. For example, if the user presses the close button or
        Alt+F4 on Windows.

        To allow the application to close, run `event.accept()`. To prevent a closure, run `event.ignore()`.

        Arguments:
            event: The close event to control whether the application can and should close or not.

        Returns:
            None.
        """
        # Stub method; can be overwritten by inheriting classes
        pass
