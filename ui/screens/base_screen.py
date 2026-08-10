"""
base_screen.py

The definition for a base definition of a screen in this application. All screens are expected to
inherit BaseScreen.

Contains methods that can communicate with higher levels of the application, and lifecycle methods.
"""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QMessageBox, QWidget

from core.app.screen_ids import Screen


class BaseScreen(QWidget):
    """
    Creates a base screen, inheriting `QWidget`. This class is used as the blueprint for all screens in the
    application. All screens are expected to inherit BaseScreen.

    This class provides some utility methods that can interact with higher levels of the application, such
    as navigation and application title bar changes. There are also lifecycle functions which are called
    automatically when certain events occur, such as the screen being shown and hidden.

    Attributes:
        title_text: The default text of the screen when entered. Changing this will not apply the changes,
            to change the title text while the screen is active, use `set_title()`. A string is used for
            compatibility with the title setting API.

        navigate: A `pyqtSignal` that emits when navigation to a different screen is requested. The screen
            ID to navigate to is provided as the first argument, as a Screen enum for better type checking.
            The second argument is an optional payload of any type.

        title_change: A `pyqtSignal` that emits when the global application title is requested to be changed.
            The new title is provided as the argument, as a string represents the title well since it can
            store many characters.

        status: A `pyqtSignal` that emits when the global status bar should change state and/or text. The first
            argument is the new text to show on the status bar, as a string since strings can display a variety
            of characters. The second argument is the timeout as an integer in milliseconds, as the integer
            can represent the data in the amount of precision required.

        status_reset: A `pyqtSignal` that emits when the global status bar should reset to its default value.
            No arguments are provided.
    """

    # Can be overwritten by inheriting screens
    title_text = "Quiz Master"

    # These signals should be invoked via their wrapper methods, not directly
    navigate = pyqtSignal(Screen, object)
    title_change = pyqtSignal(str)
    status = pyqtSignal(str, int)
    status_reset = pyqtSignal()

    def go_to(self, screen: Screen, payload: object | None = None) -> None:
        """
        Navigates to another screen of the app as identified by the screen ID, with an optional payload.

        Navigation requests are emitted as signals and handled by the navigation controller.
        The implementation is defined in :func:`~ui.main_window.MainWindow.go_to`.

        Arguments:
            screen: The screen ID to switch to for the UI and logic. An enum is used to allow better type checking
                compared to a string and easier readability in code.

            payload: The optional payload to provide the new screen and logic after switching. The payload can be of
                any type, or None, allowing flexibility in what can be sent (typically a dictionary or specialized
                data transfer object).

        Returns:
            None.
        """
        self.navigate.emit(screen, payload)

    def set_title(self, title: str) -> None:
        """
        Change the application's global window title. The title should preferably follow the naming convention
        of this application, being _"Quiz Master – {window name}"_.

        Arguments:
            title: A string for the new title text. A string is used as the window title only supports text.

        Returns:
            None.
        """
        self.title_change.emit(title)

    def set_status(self, message: str, timeout: int = 0) -> None:
        """
        Sets the global status bar message, with an optional timeout in milliseconds. A timeout of 0 is treated
        as a permanent message.

        Arguments:
            message: A string for the message to show in the status bar. A string is used as the status bar
                only displays text.

            timeout: An integer describing how long the status message is shown for. An integer is used for
                milliseconds to allow higher precision.

        Returns:
            None.
        """
        self.status.emit(message, timeout)

    def reset_status(self) -> None:
        """
        Fully reset status bar message, resetting it to the default status bar message with no timeout.

        Returns:
            None.
        """
        self.status_reset.emit()

    def show_error(self, title: str, desc: str) -> None:
        """
        Shows an error messagebox. Use this when a critical issue occurs so that the program cannot continue
        the process.

        Arguments:
            title: The title to display on the error messagebox. A string is used as the title is expected to
                consist of characters.

            desc: The description to display on the error messagebox. A string is used as the description is
                expected to consist of characters.

        Returns:
            None.
        """
        QMessageBox.critical(self, title, desc)

    def show_warning(self, title: str, desc: str) -> None:
        """
        Shows a warning messagebox. Use this when an issue occurs, and the program can continue, but with some
        side-effects or future errors.

        Arguments:
            title: The title to display on the warning messagebox. A string is used as the title is expected to
                consist of characters.

            desc: The description to display on the warning messagebox. A string is used as the description is
                expected to consist of characters.

        Returns:
            None.
        """
        QMessageBox.warning(self, title, desc)

    def show_info(self, title: str, desc: str) -> None:
        """
        Shows an informational messagebox. Use this when the user is required to learn information immediately.

        Arguments:
            title: The title to display on the informational messagebox. A string is used as the title is expected to
                consist of characters.

            desc: The description to display on the informational messagebox. A string is used as the description is
                expected to consist of characters.

        Returns:
            None.
        """
        QMessageBox.information(self, title, desc)

    def show_question(self, title: str, desc: str, default: str = "no") -> bool:
        """
        Shows an question messagebox. Use to ask a question without any danger if one or the other option is picked.
        If there is, use the external `confirm_warning()` function.

        Arguments:
            title: The title to display on the question messagebox. A string is used as the title is expected to
                consist of characters.

            desc: The description to display on the question messagebox. A string is used as the description is
                expected to consist of characters.

            default: The default button to select. Default value is 'no', and available values are either 'yes' or
                'no'. If the value is not recognized, raises ValueError. A string is used for easier readability.

        Returns:
            A boolean indicating the value selected from the messagebox: True if Yes was selected, else False. A
                boolean is used as it easily represents a yes/no value for operations and conditional statements.

        Raises:
            ValueError: If the default is not 'yes' or 'no'.
        """
        # Validate default button value
        default = default.lower()
        if default not in ("yes", "no"):
            raise ValueError(f"Invalid default value: {default}")

        # Convert default string to QMessageBox enum. An enum is not requested
        # directly to reduce code length in calling code and reduce QMessageBox imports.
        default_button = (
            QMessageBox.StandardButton.No
            if default == "no"
            else QMessageBox.StandardButton.Yes
        )

        confirm = QMessageBox.question(
            self,
            title,
            desc,
            defaultButton=default_button,
        )

        return confirm == QMessageBox.StandardButton.Yes

    def on_enter(self, payload: object | None = None) -> None:
        """
        Called when this screen becomes active and displayed, with an optional payload.

        Arguments:
            payload: The optional payload that is provided after switching.

        Returns:
            None.
        """
        # Stub method; can be overwritten by inheriting classes
        pass

    def on_leave(self) -> None:
        """
        Called when this screen becomes inactive and hidden visually.

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
