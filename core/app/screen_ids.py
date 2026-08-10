"""
screen_ids.py

Contains IDs for every screen in the application as an enum, to avoid using strings or integers
literally, which can cause readability issues and typos.
"""

from enum import Enum


class Screen(Enum):
    """
    Describes a screen within the app, to reference a certain screen.
    """

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
    COMMON_LOADING = "common_loading"
    COMMON_COUNTDOWN = "common_countdown"
    COMMON_ABOUT = "common_about"
    COMMON_QUIZ_MANAGER = "common_quiz_manager"
    COMMON_QUIZ_SETUP = "common_quiz_setup"
    COMMON_QUIZ_EDITOR = "common_quiz_editor"
