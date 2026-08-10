"""
screen_factory.py

Contains the screen factory and registry for the application. Centralizes the creation of screens
and their respective logic to prevent other classes from knowing about the exact screen classes.
"""

# ruff: noqa: I001
from PyQt6.QtWidgets import QWidget

from core.app.screen_ids import Screen
from core.services.app_context import Services
from ui.screens.base_screen import BaseScreen
from logic.base_logic import BaseLogic

# Screens
from ui.screens.client.setup import ClientSetupScreen
from ui.screens.client.lobby import ClientLobbyScreen
from ui.screens.client.multi_question import ClientMultiQuestionScreen
from ui.screens.client.multi_result import ClientMultiResultScreen
from ui.screens.client.final_result import ClientFinalResultScreen
from ui.screens.client.disconnect import ClientDisconnectScreen

from ui.screens.server.lobby import ServerLobbyScreen
from ui.screens.server.multi_question import ServerMultiQuestionScreen
from ui.screens.server.multi_result import ServerMultiResultScreen
from ui.screens.server.final_result import ServerFinalResultScreen

from ui.screens.common.menu import CommonMenuScreen
from ui.screens.common.quiz_manager import CommonQuizManagerScreen
from ui.screens.common.quiz_setup import CommonQuizSetupScreen
from ui.screens.common.quiz_editor import CommonQuizEditorScreen
from ui.screens.common.loading import CommonLoadingScreen
from ui.screens.common.countdown import CommonCountdownScreen
from ui.screens.common.about import CommonAboutScreen

# Logic
from logic.client.setup import ClientSetupLogic
from logic.client.lobby import ClientLobbyLogic
from logic.client.multi_question import ClientMultiQuestionLogic
from logic.client.multi_result import ClientMultiResultLogic
from logic.client.final_result import ClientFinalResultLogic
from logic.client.disconnect import ClientDisconnectLogic

from logic.server.lobby import ServerLobbyLogic
from logic.server.multi_question import ServerMultiQuestionLogic
from logic.server.multi_result import ServerMultiResultLogic
from logic.server.final_result import ServerFinalResultLogic

from logic.common.menu import CommonMenuLogic
from logic.common.quiz_manager import CommonQuizManagerLogic
from logic.common.quiz_setup import CommonQuizSetupLogic
from logic.common.quiz_editor import CommonQuizEditorLogic
from logic.common.loading import CommonLoadingLogic
from logic.common.countdown import CommonCountdownLogic
from logic.common.about import CommonAboutLogic

# Registry for all screens and their respective logic
SCREEN_INFO: dict[Screen, tuple[BaseScreen, BaseLogic]] = {
    # Client
    Screen.CLIENT_SETUP: (ClientSetupScreen, ClientSetupLogic),
    Screen.CLIENT_LOBBY: (ClientLobbyScreen, ClientLobbyLogic),
    Screen.CLIENT_MULTI_QUESTION: (
        ClientMultiQuestionScreen,
        ClientMultiQuestionLogic,
    ),
    Screen.CLIENT_MULTI_RESULT: (ClientMultiResultScreen, ClientMultiResultLogic),
    Screen.CLIENT_FINAL_RESULT: (ClientFinalResultScreen, ClientFinalResultLogic),
    Screen.CLIENT_DISCONNECT: (ClientDisconnectScreen, ClientDisconnectLogic),
    # Server
    Screen.SERVER_LOBBY: (ServerLobbyScreen, ServerLobbyLogic),
    Screen.SERVER_MULTI_QUESTION: (
        ServerMultiQuestionScreen,
        ServerMultiQuestionLogic,
    ),
    Screen.SERVER_MULTI_RESULT: (ServerMultiResultScreen, ServerMultiResultLogic),
    Screen.SERVER_FINAL_RESULT: (ServerFinalResultScreen, ServerFinalResultLogic),
    # Common
    Screen.COMMON_MENU: (CommonMenuScreen, CommonMenuLogic),
    Screen.COMMON_LOADING: (CommonLoadingScreen, CommonLoadingLogic),
    Screen.COMMON_COUNTDOWN: (CommonCountdownScreen, CommonCountdownLogic),
    Screen.COMMON_ABOUT: (CommonAboutScreen, CommonAboutLogic),
    Screen.COMMON_QUIZ_MANAGER: (CommonQuizManagerScreen, CommonQuizManagerLogic),
    Screen.COMMON_QUIZ_SETUP: (CommonQuizSetupScreen, CommonQuizSetupLogic),
    Screen.COMMON_QUIZ_EDITOR: (CommonQuizEditorScreen, CommonQuizEditorLogic),
}


def create_screen_bundle(
    screen: Screen, services: Services, parent: QWidget | None = None
) -> tuple[BaseScreen, BaseLogic]:
    """
    A factory function; used to create the correct screen and its respective logic depending on the screen
    ID provided by searching the screen registry. Initializes both the screen and logic classes with its
    required arguments, and returns both initialized classes.

    Arguments:
        screen: The screen ID to create the bundle from, as the identifier. An enum is used as it is safer
            to use than a string to avoid accidental typos and provide easier readability.

        services: The services class for providing to the logic, to allow it to access the core logic.

        parent: The parent to make the screen a child of, or None to set no parent. Defaults to None.

    Returns:
        The screen and logic classes created as a tuple, with the screen first and the logic second.
        A tuple is used as it can group similar values together and allows for tuple unpacking.

    Raises:
        ValueError: If the screen provided could not be found in the registry.
    """
    try:
        screen_cls, logic_cls = SCREEN_INFO[screen]

        # Initialize screen and logic classes
        widget = screen_cls(parent)
        logic = logic_cls(widget, services)

        return widget, logic
    except KeyError as e:
        raise ValueError(f"Unknown screen: {screen}") from e
