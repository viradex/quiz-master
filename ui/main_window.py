"""
main_window.py

The main creation point of the UI and logic of the application.

Contains the main window of the application, which hosts all individual screen
UIs and logic. Also initializes app controllers (global logic) and injects global
services.
"""

import ctypes
import sys

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QCloseEvent, QFontMetrics, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QStackedWidget,
    QStatusBar,
    QWidget,
)

from core.app.screen_factory import create_screen_bundle
from core.app.screen_ids import Screen
from core.config.constants import (
    DEFAULT_STATUS_BAR_MESSAGE,
    EAGER_SCREENS,
    STARTUP_SCREEN,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from core.services.app_context import Services
from logic.app_controller.client import ClientAppController
from logic.app_controller.server import ServerAppController
from logic.base_logic import BaseLogic
from ui.screens.base_screen import BaseScreen
from utils.paths import get_icons_dir


class MainWindow(QMainWindow):
    """
    Creates the main window of the application, inheriting `QMainWindow`.

    Sets up the main window and its UI, including the icon, theme, app controllers,
    and screens. Contains the heart of navigation throughout the app between various
    screens and the global status bar.

    Contains APIs for screens to access indirectly through signals, and for app
    controllers to directly call (though only a select few).

    Arguments:
        services: The global services of the application. These are passed directly to
            the application controllers; MainWindow does not use them.
    """

    def __init__(self, services: Services) -> None:
        super().__init__()

        # Injected services
        self.services = services

        # Set up screen widgets and logic; these are always the same length, with respective screens
        # and logic. The Screen enum is used as the key. A dictionary is used to allow easy lookups
        # when switching screens and creating screens/logic.
        self.screen_widgets: dict[Screen, BaseScreen] = {}
        self.screen_logic: dict[Screen, BaseLogic] = {}

        # The current screen is always paired with a respective logic relating to the same screen
        self.current_screen: BaseScreen | None = None
        self.current_logic: BaseLogic | None = None

        # Last or current permanent status bar text
        self.status_text: str = DEFAULT_STATUS_BAR_MESSAGE

        self.setMinimumSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.center_window()

        # Run full application setup
        self._setup_ui()
        self._setup_icon()
        self._setup_theme()
        self._setup_font()
        self._setup_app_controllers()
        self._build_eager_screens()

        self.go_to(STARTUP_SCREEN)

    def center_window(self) -> None:
        """
        Centers the window in the primary screen of the user's display from the available screen
        size to the application. For example, the taskbar on Windows is excluded from the available size.

        The top-left x and y positions are decided in mind with the current screen width and height
        and then halved to appear exactly in the center of the screen. In the case of multiple displays
        or monitors, the primary monitor is chosen to center the window in, not in between multiple displays.

        Returns:
            None.
        """
        screen = QApplication.primaryScreen().availableGeometry()

        # Calculate the top-left corner position of the app, keeping in mind the width and
        # height of the application so the corner itself does not appear at the center,
        # but rather the center of the application window itself.
        x = (screen.width() - WINDOW_WIDTH) // 2
        y = (screen.height() - WINDOW_HEIGHT) // 2

        self.move(x, y)

    def _setup_icon(self) -> None:
        """
        Internal method. Sets up the application icon for the main window and all children windows (e.g. messageboxes).
        On Windows, this also sets a unique ID for this application to display the icon on the taskbar rather than the
        generic Python logo.

        Returns:
            None.
        """
        icon_path = get_icons_dir() / "icon.ico"

        # Convert Path to string since QIcon doesn't interpret Paths
        self.setWindowIcon(QIcon(str(icon_path)))

        # Set taskbar icon if on Windows
        # See: https://stackoverflow.com/questions/1551605/how-to-set-applications-taskbar-icon-in-windows-7
        if sys.platform == "win32":
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "com.viradex.quizmaster"
            )

    def _setup_theme(self) -> None:
        """
        Internal method. Sets up the global application theme to be in dark mode, if supported. Setting to dark
        mode explicitly rather than following the global OS theme set by the user. This prevents certain UI
        elements hardcoded in QSS that assume dark mode to not appear broken or inconsistent.

        The forced color scheme change is only supported on certain operating systems, and is only available for
        Qt 6.8 and higher.

        Returns:
            None.
        """
        style_hints = QApplication.styleHints()

        try:
            # Some Qt versions don't have the setColorScheme() method
            style_hints.setColorScheme(Qt.ColorScheme.Dark)
        except AttributeError:
            # If theme is not already dark by default, show user warning
            if style_hints.colorScheme() != Qt.ColorScheme.Dark:
                self.show_warning(
                    "Failed to Set Theme",
                    "Failed to set the theme to dark mode. Some UI elements may appear to be inconsistent or broken.",
                )

    def _setup_font(self) -> None:
        """
        Internal method. Sets up font details. Preloads emojis/glyphs width details so they do not lag the UI
        when rendering.

        Emojis/glyphs can cause a noticeable lag when showing a screen containing them for the first time.
        To prevent that lag spike, this method makes Qt pre-calculate the width of the emojis to help with
        the rendering.

        Returns:
            None.
        """
        metrics = QFontMetrics(self.font())

        # Calculate width of glyphs used in app
        metrics.horizontalAdvance("✔")
        metrics.horizontalAdvance("✖")

    def _setup_app_controllers(self) -> None:
        """
        Internal method. Sets up app controllers, used for global logic. All app controllers have access to
        this MainWindow and the entire Services class for dependencies that may be needed.

        Multiple app controllers are used. While they are all initialized the same and could be in one AppController,
        they are separate to avoid mixing responsibilities (e.g. client and server are two separate app controllers
        rather than being the same class).

        Returns:
            None.
        """
        # Save app controllers to an attribute to avoid them being possibly garbage collected
        self.client_app_controller = ClientAppController(self, self.services)
        self.server_app_controller = ServerAppController(self, self.services)

    def _setup_ui(self) -> None:
        """
        Internal method. Sets up the main UI for the application. The central widget consists purely of a
        `QStackedWidget`, allowing to display and hide screens with ease, without destroying and manually
        showing them again, which can be costly in performance and can cause more bugs and unnecessary complexity.

        This method also creates the global status bar used throughout the application. The status bar is
        initialized with the default status bar text as defined in the constant.

        Returns:
            None.
        """
        # Make a wrapper QWidget rather than directly placing the QStackedWidget as the central widget
        # to allow global padding to apply, ensuring widgets don't appear too close to the edge.
        self.central = QWidget()
        self.setCentralWidget(self.central)

        self.stack = QStackedWidget()

        hbox = QHBoxLayout(self.central)
        hbox.addWidget(self.stack)

        # Create and set status bar with default text and styling
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.status_bar.setStyleSheet("border-top: 1px solid #444;" "font-size: 11px;")
        self.status_bar.setSizeGripEnabled(False)

        self.set_status(self.status_text)

    def _build_eager_screens(self) -> None:
        """
        Internal method. Build all screens as defined in `EAGER_SCREENS`, to allow faster performance when
        switching to commonly-visited screens rather than forcing PyQt to create the new screen when the
        user requests it (lazy loading).

        This method should be run at or near the end of the MainWindow startup process.

        Returns:
            None.
        """
        # Build all eager screens prematurely to increase performance for commonly-visited screens
        for screen in EAGER_SCREENS:
            self._build_screen(screen)

    def get_screen_bundle(self, screen: Screen) -> tuple[BaseScreen, BaseLogic]:
        """
        Gets a screen and logic bundle from the widgets and logic already saved, to avoid re-creating the
        screen/logic and increasing performance. If the screen does not exist, both are freshly created
        and then returned.

        Arguments:
            screen: The screen ID to find, and create if it has not yet been created. An enum is used to allow
                better type checking compared to a string and easier readability in code.

        Returns:
            A tuple containing the screen instance and its associated logic instance. A tuple is used to pair
            the widget and logic together cleanly and to allow easier unpacking.
        """
        # Build fresh screen and respective logic if it hasn't been created yet. Newly-created screens and
        # logic are automatically stored in the screen_widgets and screen_logic dictionaries.
        if screen not in self.screen_widgets:
            self._build_screen(screen)

        widget = self.screen_widgets[screen]
        logic = self.screen_logic[screen]

        return widget, logic

    def _build_screen(self, screen: Screen) -> None:
        """
        Internal method. Used to build a certain screen based on the ID given using the factory pattern, decoupling
        the MainWindow from the actual screen and logic instances themselves. If the screen already exists, no new
        screen or logic is built or overwritten.

        The screen and respective logic that is created is automatically saved in `screen_widgets` and `screen_logic`,
        respectively, with the screen ID as the key. The screen is also added to the `QStackedWidget` and signals
        are connected from the screen to the MainWindow.

        Arguments:
            screen: The screen ID to find and create for the widget and logic. An enum is used to allow better type
                checking compared to a string and easier readability in code.

        Returns:
            None.
        """
        # If screen already exists, return early to prevent an inconsistent state between
        # the dictionary and QStackedWidget
        if screen in self.screen_widgets:
            return

        # Create screen and its respective logic
        widget, logic = create_screen_bundle(screen, self.services, parent=self)

        # Save screen and logic for future lookup and use
        self.screen_widgets[screen] = widget
        self.screen_logic[screen] = logic

        self.stack.addWidget(widget)

        # Connect signals from the screen to this main window. Using signals adds decoupling,
        # ensuring the child screen does not know about MainWindow directly, and only actions
        # that affect the app as a whole are delegated to MainWindow.
        widget.navigate.connect(self.go_to)
        widget.title_change.connect(self.set_title)
        widget.status.connect(self.set_status)
        widget.status_reset.connect(self.reset_status)

    def go_to(self, screen: Screen, payload: object | None = None) -> None:
        """
        Navigates to another screen of the app as identified by the screen ID, with an optional payload.

        Before switching screens, the current screen, if any, is notified that it is about to be hidden through the
        `on_leave()` method, before the requested screen and logic are found (or created, if they haven't already
        been). The screen is then brought up and shown in the stacked widget and the title is changed to reflect
        the one set in the screen that has been switched to. The new screen's `on_enter()` method is called to
        notify it that the screen is now visible, and it is set as the current screen, along with the logic.

        The payload is an optional parameter that can be passed to the new screen via `on_enter()` as an
        argument. The receiving screen (and logic) can then decide how to use the data provided. The data simply
        passes through this method: it is not cleaned, validated, or mutated in any way.

        Arguments:
            screen: The screen ID to switch to for the UI and logic. An enum is used to allow better type checking
                compared to a string and easier readability in code.

            payload: The optional payload to provide the new screen and logic after switching, through the `on_enter()`
                method. The payload can be of any type, or None, allowing flexibility in what can be sent (typically
                a dictionary or specialized data transfer object).

        Returns:
            None.
        """
        # Call lifecycle functions if a screen exists. In normal usage, it will only not
        # exist if this is the first screen that is shown.
        if self.current_screen is not None:
            self.current_screen.on_leave()
            self.current_logic.on_leave()

        # Setup screen and logic
        widget, logic = self.get_screen_bundle(screen)

        # Show UI in stacked widget and set application title
        self.stack.setCurrentWidget(widget)
        self.set_title(widget.title_text)

        # Call lifecycle functions with payload
        widget.on_enter(payload)
        logic.on_enter(payload)

        self.current_screen = widget
        self.current_logic = logic

    def set_title(self, title: str) -> None:
        """
        Change the application's global window title, replacing the old title. The title should preferably follow
        the naming convention of this application, being _"Quiz Master – {window name}"_. This is not enforced, however.

        Arguments:
            title: A string for the new title text. A string is used as the window title only supports text.

        Returns:
            None.
        """
        self.setWindowTitle(title)

    def set_status(self, message: str, timeout: int = 0) -> None:
        """
        Sets the global status bar message, with an optional timeout in milliseconds.

        A timeout of 0 is treated as a permanent message, and will not change unless reset with `reset_status()`
        or a new permanent status is set using this method. When setting a temporary status by making timeout > 0,
        the most recent permanent status is reinstated when the timeout expires, rather than the default status bar message.

        Arguments:
            message: A string for the message to show in the status bar. A string is used as the status bar only displays
                text.

            timeout: An integer describing how long the status message is shown for before being reset to the last permanent
                status bar message. An integer is used for milliseconds to allow higher precision and easier usage with QTimer
                and the status bar API provided by PyQt.

        Returns:
            None.
        """
        # PyQt will automatically make a message with timeout=0 display forever until replaced
        self.status_bar.showMessage(message, timeout)

        # Set permanent status message
        if timeout <= 0:
            self.status_text = message

        # A status bar message with a timeout > 0 will clear when it expires, without showing another
        # message in its place. To avoid this, set a single shot timer to be called when the status bar
        # expires to replace it with the last permanent message rather than nothing. A single shot timer
        # automatically stops when it finishes without resetting.
        if timeout > 0:
            QTimer.singleShot(timeout, self._set_status_after_timeout)

    def reset_status(self) -> None:
        """
        Fully reset status bar message, resetting it to the default status bar message with no timeout. This
        does not set the last permanent status bar message.

        Returns:
            None.
        """
        self.status_text = DEFAULT_STATUS_BAR_MESSAGE
        self.status_bar.showMessage(self.status_text)

    def _set_status_after_timeout(self) -> None:
        """
        Internal method. Gets and sets the original permanent status bar text after a temporary one concludes.

        Returns:
            None.
        """
        self.status_bar.showMessage(self.status_text)

    def show_error(self, title: str, desc: str) -> None:
        """
        Shows an error messagebox. Should only be used by AppController and the MainWindow itself. Use an error
        messagebox when a critical issue occurs so that the program cannot continue the process.

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
        Shows a warning messagebox. Should only be used by AppController and the MainWindow itself. Use a warning
        messagebox when an issue occurs, and the program can continue, but with some side-effects or future errors.

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
        Shows an informational messagebox. Should only be used by AppController and the MainWindow itself. Use an
        informational messagebox when the user is required to learn information immediately.

        Arguments:
            title: The title to display on the informational messagebox. A string is used as the title is expected to
                consist of characters.

            desc: The description to display on the informational messagebox. A string is used as the description is
                expected to consist of characters.

        Returns:
            None.
        """
        QMessageBox.information(self, title, desc)

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Called automatically by PyQt when the window is about to be closed. For example, if the user presses the close
        button or Alt+F4 on Windows.

        Notifies all app controllers about the event, and if the app controllers accept the closing, the current screen
        and logic are also notified. If all processes notified accept the closure, the window is allowed to close. If
        any process declines the closure, the window remains open.

        Arguments:
            event: An argument passed automatically by PyQt upon this method being run. Allows the closure of the window
                to be controlled through the event property.

        Returns:
            None.
        """
        # Notify all app controllers first of window closure
        self.client_app_controller.on_window_close(event)
        self.server_app_controller.on_window_close(event)

        # If all app controllers accepted the closure, and a current screen
        # is shown, notify current screen and logic of the window closure via
        # lifecycle functions
        if event.isAccepted() and self.current_screen is not None:
            self.current_screen.on_window_close(event)
            self.current_logic.on_window_close(event)

        # If all processes that were asked accepted the closure, allow the
        # window to close. If any process ignored (aka declined) the closure,
        # the window remains open.
        if event.isAccepted():
            super().closeEvent(event)
