"""
types.py

Contains message types for client-server communication. All messages between the client and the
server must use one of these defined message types.
"""

# Must use StrEnum for proper serialization when communicating over network
from enum import StrEnum


class ClientMessageType(StrEnum):
    """
    Defines the message types the client can send to the server, and that the server can listen to
    from the client. A StrEnum is used to allow proper serialization when communicating across the
    network, without having to use `.value`.
    """

    PONG = "pong"

    JOIN_LOBBY = "join_lobby"
    LEAVE_LOBBY = "leave_lobby"

    ANSWER_SUBMIT = "answer_submit"


class ServerMessageType(StrEnum):
    """
    Defines the message types the server can send to the client, and that the client can listen to
    from the server. A StrEnum is used to allow proper serialization when communicating across the
    network, without having to use `.value`.
    """

    PING = "ping"

    PLAYER_JOINED = "player_joined"
    PLAYER_LEFT = "player_left"
    CONNECTION_SUCCESSFUL = "connection_successful"

    COUNTDOWN_STARTED = "countdown_started"
    QUESTION_DATA = "question_data"
    RESULTS = "results"
    FINAL_RESULTS = "final_results"

    ERROR = "error"
    KICK = "kick"
    INVALID_ACTION = "invalid_action"
