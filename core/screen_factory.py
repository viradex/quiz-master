from core.screen_ids import Screens

from ui.screens.client.setup import ClientSetupScreen
from ui.screens.client.lobby import ClientLobbyScreen
from ui.screens.client.multi_question import ClientMultiQuestionScreen
from ui.screens.client.multi_result import ClientMultiResultScreen
from ui.screens.client.entry_question import ClientEntryQuestionScreen
from ui.screens.client.entry_result import ClientEntryResultScreen
from ui.screens.client.final_result import ClientFinalResultScreen
from ui.screens.client.disconnect import ClientDisconnectScreen

from ui.screens.server.lobby import ServerLobbyScreen
from ui.screens.server.multi_question import ServerMultiQuestionScreen
from ui.screens.server.multi_result import ServerMultiResultScreen
from ui.screens.server.entry_question import ServerEntryQuestionScreen
from ui.screens.server.entry_result import ServerEntryResultScreen
from ui.screens.server.final_result import ServerFinalResultScreen

from ui.screens.common.menu import CommonMenuScreen
from ui.screens.common.loading import CommonLoadingScreen
from ui.screens.common.countdown import CommonCountdownScreen
from ui.screens.common.about import CommonAboutScreen

SCREENS = {
    # Client
    Screens.CLIENT_SETUP: ClientSetupScreen,
    Screens.CLIENT_LOBBY: ClientLobbyScreen,
    Screens.CLIENT_MULTI_QUESTION: ClientMultiQuestionScreen,
    Screens.CLIENT_MULTI_RESULT: ClientMultiResultScreen,
    Screens.CLIENT_ENTRY_QUESTION: ClientEntryQuestionScreen,
    Screens.CLIENT_ENTRY_RESULT: ClientEntryResultScreen,
    Screens.CLIENT_FINAL_RESULT: ClientFinalResultScreen,
    Screens.CLIENT_DISCONNECT: ClientDisconnectScreen,
    # Server
    Screens.SERVER_LOBBY: ServerLobbyScreen,
    Screens.SERVER_MULTI_QUESTION: ServerMultiQuestionScreen,
    Screens.SERVER_MULTI_RESULT: ServerMultiResultScreen,
    Screens.SERVER_ENTRY_QUESTION: ServerEntryQuestionScreen,
    Screens.SERVER_ENTRY_RESULT: ServerEntryResultScreen,
    Screens.SERVER_FINAL_RESULT: ServerFinalResultScreen,
    # Common
    Screens.COMMON_MENU: CommonMenuScreen,
    Screens.COMMON_LOADING: CommonLoadingScreen,
    Screens.COMMON_COUNTDOWN: CommonCountdownScreen,
    Screens.COMMON_ABOUT: CommonAboutScreen,
}


def create_screen(screen: Screens, parent=None):
    try:
        return SCREENS[screen](parent)
    except KeyError:
        raise ValueError(f"Unknown screen: {screen}")
