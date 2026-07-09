from enum import Enum


class Screens(Enum):
    """Screen IDs within the app."""

    # Client
    CLIENT_SETUP = "client_setup"
    CLIENT_LOBBY = "client_lobby"
    CLIENT_MULTI_QUESTION = "client_multi_question"
    CLIENT_MULTI_RESULT = "client_multi_result"
    CLIENT_FINAL_RESULT = "client_final_result"
    CLIENT_DISCONNECT = "client_disconnect"

    # Server
    SERVER_LOBBY = "server_lobby"
    SERVER_MULTI_QUESTION = "server_multi_question"
    SERVER_MULTI_RESULT = "server_multi_result"
    SERVER_FINAL_RESULT = "server_final_result"

    # Common
    COMMON_MENU = "common_menu"
    COMMON_QUIZ_MANAGER = "common_quiz_manager"
    COMMON_QUIZ_SETUP = "common_quiz_setup"
    COMMON_QUIZ_EDITOR = "common_quiz_editor"
    COMMON_LOADING = "common_loading"
    COMMON_COUNTDOWN = "common_countdown"
    COMMON_ABOUT = "common_about"
