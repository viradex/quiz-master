from core.app.enums import QuizValidationError, QuestionValidationError

from core.config.constants import MAX_QUESTION_LENGTH, MAX_ANSWER_LENGTH

QUIZ_ERROR_MESSAGES: dict[QuizValidationError, str] = {
    # Global quiz errors
    QuizValidationError.MISSING_ID: "The quiz is missing an ID.",
    QuizValidationError.MISSING_TITLE: "The quiz title is blank.",
    QuizValidationError.MISSING_QUESTIONS: "The quiz does not contain any questions.",
    QuizValidationError.NO_SHUFFLE_INFO: "The quiz does not contain information about shuffling questions.",
    QuizValidationError.NO_PREMADE_INFO: "The quiz does not contain information for if the quiz is a default.",
    QuizValidationError.UPDATED_FUTURE: "The quiz's updated at date is in the future.",
    # Individual question errors
    QuizValidationError.DUPLICATED_ID: "Two or more questions have the same question ID.",
    QuizValidationError.INVALID_ANSWERS: "One or more questions contain too few or too many answers.",
    QuizValidationError.INVALID_CORRECT_ANSWER: "One or more questions have the correct answer not correspond to a valid answer.",
    QuizValidationError.INVALID_TIME: "One or more questions have the time limit less than or equal to zero.",
}

QUESTION_ERROR_MESSAGES: dict[QuestionValidationError, str] = {
    QuestionValidationError.MISSING_QUESTION: "The question is blank.",
    QuestionValidationError.QUESTION_TOO_LONG: f"The question exceeds the character limit of {MAX_QUESTION_LENGTH} characters.",
    QuestionValidationError.MISSING_REQUIRED_ANSWERS: "The first two answers are blank.",
    QuestionValidationError.ANSWER_TOO_LONG: f"An answer, or answers, exceed the character limit of {MAX_ANSWER_LENGTH} characters.",
    QuestionValidationError.DUPLICATE_ANSWER: "Two or more answers are the same.",
    QuestionValidationError.NO_CORRECT_ANSWER: "No correct answer is selected.",
}


def format_errors(errors: list) -> str:
    errors = ["- " + error for error in errors]
    return "\n".join(errors)
