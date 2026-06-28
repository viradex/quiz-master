from PyQt6.QtWidgets import QWidget

from core.app.screen_ids import Screens
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
from logic.common.loading import CommonLoadingLogic
from logic.common.countdown import CommonCountdownLogic
from logic.common.about import CommonAboutLogic

# Registry for all screens and respective logic
SCREEN_INFO: dict[Screens, tuple[BaseScreen, BaseLogic]] = {
    # Client
    Screens.CLIENT_SETUP: (ClientSetupScreen, ClientSetupLogic),
    Screens.CLIENT_LOBBY: (ClientLobbyScreen, ClientLobbyLogic),
    Screens.CLIENT_MULTI_QUESTION: (
        ClientMultiQuestionScreen,
        ClientMultiQuestionLogic,
    ),
    Screens.CLIENT_MULTI_RESULT: (ClientMultiResultScreen, ClientMultiResultLogic),
    Screens.CLIENT_FINAL_RESULT: (ClientFinalResultScreen, ClientFinalResultLogic),
    Screens.CLIENT_DISCONNECT: (ClientDisconnectScreen, ClientDisconnectLogic),
    # Server
    Screens.SERVER_LOBBY: (ServerLobbyScreen, ServerLobbyLogic),
    Screens.SERVER_MULTI_QUESTION: (
        ServerMultiQuestionScreen,
        ServerMultiQuestionLogic,
    ),
    Screens.SERVER_MULTI_RESULT: (ServerMultiResultScreen, ServerMultiResultLogic),
    Screens.SERVER_FINAL_RESULT: (ServerFinalResultScreen, ServerFinalResultLogic),
    # Common
    Screens.COMMON_MENU: (CommonMenuScreen, CommonMenuLogic),
    Screens.COMMON_LOADING: (CommonLoadingScreen, CommonLoadingLogic),
    Screens.COMMON_COUNTDOWN: (CommonCountdownScreen, CommonCountdownLogic),
    Screens.COMMON_ABOUT: (CommonAboutScreen, CommonAboutLogic),
}


def create_screen_bundle(
    screen: Screens, services: Services, parent: QWidget | None = None
) -> tuple[BaseScreen, BaseLogic]:
    """Creates a screen bundle, containing a screen and respective logic."""
    try:
        screen_cls, logic_cls = SCREEN_INFO[screen]

        # Initialize screen and logic classes
        widget = screen_cls(parent)
        logic = logic_cls(widget, services)

        return widget, logic
    except KeyError as e:
        raise ValueError(f"Unknown screen: {screen}") from e
