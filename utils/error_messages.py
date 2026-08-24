"""
error_messages.py

Contains mapping dictionaries for converting error codes into user-friendly error messages.
"""

from core.app.enums import (
    ClientConnectionError,
    QuestionValidationError,
    QuizValidationError,
    ServerStartingError,
)
from core.config.constants import (
    CLIENT_CONNECTION_TIMEOUT,
    MAX_ANSWER_LENGTH,
    MAX_QUESTION_LENGTH,
)

# Errors relating to failing to connect to a remote game server.
CLIENT_CONNECTION_ERROR_MESSAGES: dict[ClientConnectionError, str] = {
    ClientConnectionError.CONNECTION_REFUSED: "The connection was refused.",
    ClientConnectionError.TIMEOUT: f"The server did not respond within {CLIENT_CONNECTION_TIMEOUT} seconds.",
    ClientConnectionError.UNREACHABLE: "The server is unreachable.",
    ClientConnectionError.INVALID: "The IP address is invalid for connecting to a server.",
    ClientConnectionError.CONNECTION_RESET: "The connection was forcibly closed by the server.",
    ClientConnectionError.CONNECTION_ABORTED: "The connection was aborted.",
    ClientConnectionError.PERMISSION: "Permission denied.",
    ClientConnectionError.UNKNOWN: "An unknown error occurred.",
}

# Errors relating to failing to start the game server.
SERVER_STARTING_ERROR_MESSAGES: dict[ServerStartingError, str] = {
    ServerStartingError.IN_USE: "Another instance of the server is already running on this device, or the port is in use.",
    ServerStartingError.PERMISSION: "Permission denied.",
    ServerStartingError.INVALID_IP: "The server was attempted to be started on an IP that does not belong to the device.",
    ServerStartingError.INVALID_PORT: "The TCP server port is out of range.",
    ServerStartingError.INVALID: "Invalid argument(s).",
    ServerStartingError.UNKNOWN: "An unknown error occurred.",
}

# Errors relating to an individual question. Should mainly contain errors that are possible from the editor.
QUESTION_ERROR_MESSAGES: dict[QuestionValidationError, str] = {
    QuestionValidationError.MISSING_QUESTION: "The question text is blank.",
    QuestionValidationError.QUESTION_TOO_LONG: f"The question text exceeds the character limit of {MAX_QUESTION_LENGTH} characters.",
    QuestionValidationError.MISSING_REQUIRED_ANSWERS: "The first two answers are blank.",
    QuestionValidationError.ANSWER_TOO_LONG: f"An answer, or answers, exceed the character limit of {MAX_ANSWER_LENGTH} characters.",
    QuestionValidationError.DUPLICATE_ANSWER: "Two or more answers are the same.",
    QuestionValidationError.NO_CORRECT_ANSWER: "No correct answer is selected.",
}

# Errors relating to the quiz as a whole. Should mainly contain errors that are of a result of direct file tampering.
QUIZ_ERROR_MESSAGES: dict[QuizValidationError, str] = {
    # Global quiz errors
    QuizValidationError.MISSING_ID: "The quiz is missing an ID.",
    QuizValidationError.MISSING_TITLE: "The quiz title is blank.",
    QuizValidationError.MISSING_QUESTIONS: "The quiz does not contain any questions.",
    QuizValidationError.NO_SHUFFLE_INFO: "The quiz does not contain information about shuffling questions.",
    QuizValidationError.NO_PREMADE_INFO: "The quiz does not contain information about whether it is a default quiz.",
    QuizValidationError.NO_COMPLETENESS_INFO: "The quiz does not contain information for if it is completed.",
    QuizValidationError.INVALID_UPDATED_AT: "The quiz does not contain a valid updated at date.",
    # Individual question errors
    QuizValidationError.INVALID_QUESTION_ID: "One or more questions have an invalid question ID.",
    QuizValidationError.DUPLICATED_QUESTION_ID: "Two or more questions have the same question ID.",
    QuizValidationError.INVALID_QUESTION_TEXT: "One or more questions have invalid question text.",
    QuizValidationError.INVALID_ANSWERS: "One or more questions contain either invalid answers, or too few/many answers.",
    QuizValidationError.INVALID_CORRECT_ANSWER: "One or more questions have a correct answer that does not correspond to a valid answer.",
    QuizValidationError.INVALID_TIME: "One or more questions have the time limit less than or equal to zero.",
}


def format_errors(errors: list[str]) -> str:
    """
    Formats error messages into a clean list with bullet points denoted as dashes, with each error message
    separated by a newline, to cleanly display it to the user.

    Arguments:
        errors: A list of error strings to convert to a list-styled string. A list is used as it provides
            a simple iterable collection of the error messages.

    Returns:
        A string with errors having dashes before them and separated by newlines.
    """
    errors = [f"- {error}" for error in errors]
    return "\n".join(errors)
