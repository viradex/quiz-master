# Must use StrEnum for proper serialization when communicating over network
from enum import StrEnum


class ClientMessageType(StrEnum):
    """Defines messages a client can send to the server."""

    PING = "ping"

    JOIN_LOBBY = "join_lobby"
    LEAVE_LOBBY = "leave_lobby"

    ANSWER_SUBMIT = "answer_submit"


class ServerMessageType(StrEnum):
    """Defines messages the server can send to clients."""

    PONG = "pong"

    PLAYER_JOINED = "player_joined"
    PLAYER_LEFT = "player_left"
    CONNECTION_SUCCESSFUL = "connection_successful"

    GAME_STARTING = "game_starting"
    GAME_START = "game_start"
    COUNTDOWN = "countdown"
    QUESTION_DATA = "question_data"
    RESULTS = "results"
    FINAL_RESULTS = "final_results"

    ERROR = "error"  # generic only, if no other criteria fits
    KICK = "kick"
    INVALID_ACTION = "invalid_action"
