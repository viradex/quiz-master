"""
enums.py

Contains enums for various parts of the application, that are not specific to a certain process such
as screen IDs or networking message types.

Enums should be used to represent certain values that may have multiple possible values, and are better
than using strings or integers, which can cause readability issues and typos. Enums should only be used
when it is used across more than one file.
"""

from enum import Enum


class ClientConnectionError(Enum):
    """
    An error relating to a failed attempt to connecting to the server. Describes the error encountered.
    """

    CONNECTION_REFUSED = "connection_refused"
    TIMEOUT = "timeout"
    UNREACHABLE = "unreachable"
    INVALID = "invalid"
    CONNECTION_RESET = "connection_reset"
    CONNECTION_ABORTED = "connection_aborted"
    PERMISSION = "permission"
    UNKNOWN = "unknown"


class ServerStartingError(Enum):
    """
    An error related to a failed attempt to starting the server. Describes the error encountered.
    """

    IN_USE = "in_use"
    PERMISSION = "permission"
    INVALID_IP = "invalid_ip"
    INVALID = "invalid"
    UNKNOWN = "unknown"


class AddPlayerResult(Enum):
    """
    The result from adding a player to the server's player registry. Can be an error or `OK`.
    """

    LOBBY_FULL = "lobby_full"
    DUPLICATE_NICKNAME = "duplicate_nickname"
    EMPTY_NICKNAME = "empty_nickname"
    LONG_NICKNAME = "long_nickname"
    OK = "ok"


class AnswerValidationResult(Enum):
    """
    The result from validating the answer that the client (player) provided. Can be an error or `OK`.
    """

    ANSWER = "answer"
    TIME = "time"
    OK = "ok"


class QuizValidationError(Enum):
    """
    Any errors relating to failed quiz validation. Contains errors relating to the quiz as a whole,
    as well as any question errors. Contains illegal states about questions rather than incorrect
    states that the user can create in the quiz editor, for example (which are defined in
    `QuestionValidationError`).
    """

    # Global quiz errors
    MISSING_ID = "missing_id"
    MISSING_TITLE = "missing_title"
    MISSING_QUESTIONS = "missing_questions"
    NO_SHUFFLE_INFO = "no_shuffle_info"
    NO_PREMADE_INFO = "no_premade_info"
    NO_COMPLETENESS_INFO = "no_completeness_info"

    # Individual question errors
    INVALID_QUESTION_ID = "invalid_question_id"
    DUPLICATED_QUESTION_ID = "duplicated_question_id"
    INVALID_QUESTION_TEXT = "invalid_question_text"
    INVALID_ANSWERS = "invalid_answers"
    INVALID_CORRECT_ANSWER = "invalid_correct_answer"
    INVALID_TIME = "invalid_time"


class QuestionValidationError(Enum):
    """
    Any errors relating to failed individual question validation. Only contains incorrect states that
    are created in the quiz editor, for example.
    """

    MISSING_QUESTION = "missing_question"
    QUESTION_TOO_LONG = "question_too_long"
    MISSING_REQUIRED_ANSWERS = "missing_required_answers"
    ANSWER_TOO_LONG = "answer_too_long"
    DUPLICATE_ANSWER = "duplicate_answer"
    NO_CORRECT_ANSWER = "no_correct_answer"


class QuizSortingOrder(Enum):
    """
    Describes the sorting order of quizzes in the quiz manager.
    """

    NEWEST = "newest"
    OLDEST = "oldest"
    NAME_ASC = "name_asc"
    NAME_DESC = "name_desc"


class AnswerButtonGridMode(Enum):
    """
    Describes the internal mode for the answer button grid.
    """

    LIVE = "live"
    SERVER = "server"
    RESULT = "result"
