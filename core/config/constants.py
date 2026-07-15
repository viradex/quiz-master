from core.app.screen_ids import Screens

###################
## SCREEN CONFIG ##
###################

# Screen to start the app on
STARTUP_SCREEN = Screens.COMMON_MENU

# Screens that should be preloaded
EAGER_SCREENS = {
    Screens.CLIENT_SETUP,
    Screens.CLIENT_LOBBY,
    Screens.SERVER_LOBBY,
    Screens.COMMON_MENU,
    Screens.COMMON_QUIZ_MANAGER,
    Screens.COMMON_LOADING,
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

# TODO Only for development; set blank or remove when done
# Populates the IP address field when connecting to a server
DEFAULT_IP_ADDRESS = "127.0.0.1"

# Port to start the server on and connect to
PORT = 7878

# Maximum players to allow joining the server
MAX_PLAYERS = 50

# Time in seconds until client stops connecting to server
CLIENT_CONNECTION_TIMEOUT = 10

# Interval in seconds for client sending a heartbeat
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
