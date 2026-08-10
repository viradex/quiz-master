"""
constants.py

Contains customizable global constants that can change the behavior of the program. These values are
not validated and should not be set to extreme values or values that may break the program indirectly.

Categories:
- Screen config: Configuration relating to the screens, such as the first screen and eager screens to
    load immediately.
- Window config: Configuration relating to the application window, such as the window size.
- Client/server config: Configuration relating to the client and server as a whole, not the game itself.
    Mainly contains data relating to the networking concepts of the server and client, such as the port.
- Generic config: The miscellaneous configuration relating to the application, such as game configuration
    and quiz editor configuration.
- Generic validation config: The configuration relating to the validation across the application, such as
    maximum character limits.
"""

from core.app.screen_ids import Screen

###################
## SCREEN CONFIG ##
###################

# Screen to start the app on
STARTUP_SCREEN = Screen.COMMON_MENU

# Screens that should be preloaded
EAGER_SCREENS: set[Screen] = {
    Screen.CLIENT_SETUP,
    Screen.CLIENT_LOBBY,
    Screen.SERVER_LOBBY,
    Screen.COMMON_MENU,
    Screen.COMMON_QUIZ_MANAGER,
    Screen.COMMON_LOADING,
}

###################
## WINDOW CONFIG ##
###################

# App window dimensions
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600

# Status bar message to show when no other message is being shown
DEFAULT_STATUS_BAR_MESSAGE = "Ready"

##########################
## CLIENT/SERVER CONFIG ##
##########################

# Port to start the server on and connect to
PORT = 7878

# Maximum players to allow joining the server
MAX_PLAYERS = 50

# Maximum message size of a single network request before it is rejected
MAX_MESSAGE_SIZE = 64 * 1024  # (64 KiB)

# Time in seconds until client stops connecting to server
CLIENT_CONNECTION_TIMEOUT = 10

# Interval in seconds for server sending PING to client (heartbeat)
CLIENT_PING_INTERVAL = 6

# Time in seconds for no response until the client is disconnected
RESPONSE_TIMEOUT = 15

####################
## GENERIC CONFIG ##
####################

# Minimum players needed to start the quiz game, and for there to be during the game
MIN_PLAYERS_FOR_GAME = 2

# Time in seconds for the countdown between each question
COUNTDOWN_TIME = 3

# Interval in seconds for when a quiz will autosave in the quiz editor
QUIZ_AUTOSAVE_INTERVAL = 10

# The maximum round trip time in milliseconds which is considered 'good'
RTT_GOOD_THRESHOLD_MS = 50

# The maximum round trip time in milliseconds which is considered as a 'warning'
RTT_WARNING_THRESHOLD_MS = 150

###############################
## GENERIC VALIDATION CONFIG ##
###############################

# Maximum nickname length to join with
MAX_NICKNAME_LENGTH = 40

# Maximum quiz title length that can be created
MAX_QUIZ_TITLE_LENGTH = 60

# Maximum question text length in characters
MAX_QUESTION_LENGTH = 120

# Maximum single answer text length in characters
MAX_ANSWER_LENGTH = 75
