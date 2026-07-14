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


class QuizValidationError(Enum):
    """
    Errors relating to quiz validation. For questions, contains illegal states rather
    than states that the user can create (which are defined in `QuestionValidationError`).
    """

    # Global quiz errors
    MISSING_ID = "missing_id"
    MISSING_TITLE = "missing_title"
    MISSING_QUESTIONS = "missing_questions"
    NO_SHUFFLE_INFO = "no_shuffle_info"
    NO_PREMADE_INFO = "no_premade_info"
    UPDATED_FUTURE = "updated_future"

    # Individual question errors
    DUPLICATED_ID = "id_used"
    INVALID_ANSWERS = "invalid_answers"
    INVALID_CORRECT_ANSWER = "invalid_correct_answer"
    INVALID_TIME = "invalid_time"


class QuestionValidationError(Enum):
    """Errors relating to question validation."""

    MISSING_QUESTION = "missing_question"
    QUESTION_TOO_LONG = "question_too_long"
    MISSING_REQUIRED_ANSWERS = "missing_required_answers"
    ANSWER_TOO_LONG = "answer_too_long"
    DUPLICATE_ANSWER = "duplicate_answer"
    NO_CORRECT_ANSWER = "no_correct_answer"


class QuizSortingOrder(Enum):
    """Possible quiz sorting orders for the manager."""

    NEWEST = "newest"
    OLDEST = "oldest"
    NAME_ASC = "name_asc"
    NAME_DESC = "name_desc"
