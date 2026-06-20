from core.app.screen_ids import Screens

STARTUP_SCREEN = Screens.COMMON_MENU
EAGER_SCREENS = {
    Screens.CLIENT_SETUP,
    Screens.CLIENT_LOBBY,
    Screens.SERVER_LOBBY,
    Screens.COMMON_MENU,
    Screens.COMMON_LOADING,
}

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600

DEFAULT_IP_ADDRESS = "127.0.0.1"  # should only be used for development
PORT = 7878
MAX_PLAYERS = 50

MAX_NICKNAME_LENGTH = 40
