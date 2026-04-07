from enum import Enum


class MessageType(str, Enum):
    """Defines all valid message types that can be sent/received between the client and the server."""

    JOIN = "join"
    KICK = "kick"
    LEAVE = "leave"

    OTHER_JOIN = "other_join"
    OTHER_KICK = "other_kick"
    OTHER_LEAVE = "other_leave"

    PLAYER_LIST = "player_list"
    SHUT_DOWN = "shut_down"

    STARTING = "starting"
    QUESTION = "question"
    ANSWER = "answer"
    ANSWER_RESULT = "answer_result"
    GAME_OVER = "game_over"
