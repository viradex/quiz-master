from enum import Enum


class ClientConnectionError(Enum):
    """Errors related to connecting to the server."""

    CONNECTION_REFUSED = "connection_refused"
    TIMEOUT = "timeout"
    UNREACHABLE = "unreachable"
    INVALID = "invalid"
    CONNECTION_RESET = "connection_reset"
    CONNECTION_ABORTED = "connection_aborted"
    PERMISSION = "permission"
    UNKNOWN = "unknown"


class ServerStartingError(Enum):
    """Errors related to staring the server."""

    IN_USE = "in_use"
    PERMISSION = "permission"
    INVALID_IP = "invalid_ip"
    INVALID = "invalid"
    UNKNOWN = "unknown"


class AddPlayerResult(Enum):
    """Errors relating to adding a player to the server registry."""

    LOBBY_FULL = "lobby_full"
    DUPLICATE_NICKNAME = "dupe_nickname"
    LONG_NICKNAME = "long_nickname"
    OK = "ok"


class AnswerValidationResult(Enum):
    """Errors relating to answer submissions from a client."""

    TIME = "time"
    ANSWER = "answer"
    OK = "ok"


class QuizValidationResult(Enum):
    """Errors relating to quiz validation."""

    # Global quiz errors
    EMPTY_ID = "empty_id"
    EMPTY_TITLE = "empty_title"
    EMPTY_QUESTIONS = "empty_questions"
    NO_SHUFFLE_INFO = "no_shuffle_info"
    NO_PREMADE_INFO = "no_premade_info"

    # Individual question errors
    ID_USED = "id_used"
    EMPTY_QUESTION = "empty_question"
    INVALID_ANSWERS = "invalid_answers"
    INVALID_CORRECT_ANSWER = "invalid_correct_answer"
    INVALID_TIME = "invalid_time"

    # Success
    OK = "ok"
