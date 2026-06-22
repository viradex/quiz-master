from core.app.screen_ids import Screens

# Screen config
STARTUP_SCREEN = Screens.COMMON_MENU
EAGER_SCREENS = {
    Screens.CLIENT_SETUP,
    Screens.CLIENT_LOBBY,
    Screens.SERVER_LOBBY,
    Screens.COMMON_MENU,
    Screens.COMMON_LOADING,
}

# Window config
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600

DEFAULT_STATUS_BAR_MESSAGE = "Ready"

# Client/server config
DEFAULT_IP_ADDRESS = "127.0.0.1"  # should only be used for development
PORT = 7878
MAX_PLAYERS = 50

CLIENT_PING_INTERVAL = 6
RESPONSE_TIMEOUT = 12

# Generic validation config
MAX_NICKNAME_LENGTH = 40
