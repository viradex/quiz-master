import secrets
from dataclasses import asdict, dataclass

from core.app.enums import QuestionValidationError

from core.config.constants import MAX_QUESTION_LENGTH, MAX_ANSWER_LENGTH


@dataclass
class Question:
    """Represents a single question in a Quiz."""

    question_id: str
    question_text: str
    answer_options: list[str]
    correct_answer_index: int | None
    time_limit: int

    @staticmethod
    def generate_random_id() -> str:
        """Generate a random ID. Static method; can be used when initializing a Question."""
        return secrets.token_hex(4)

    def is_correct(self, selected_answer_index: int) -> bool:
        """Whether the selected answer index matches with the correct answer index."""
        return selected_answer_index == self.correct_answer_index

    def get_correct_answer(self) -> str | None:
        """Retrieves the correct answer text."""
        if self.correct_answer_index is None:
            return None

        return self.answer_options[self.correct_answer_index]

    def remove_empty_answers(self, mutate_answers: bool = True) -> list[str]:
        """
        Removes empty answers from `self.answer_options` (if wanted) and returns the list.
        This should only be run once it is confirmed the first two answers are filled in to avoid shifting positions.
        """
        non_empty_answers = [a.strip() for a in self.answer_options if a.strip() != ""]

        if mutate_answers:
            self.answer_options = non_empty_answers

        return non_empty_answers

    def validate_question(self) -> set[QuestionValidationError]:
        """
        Validates this individual question for any issues. It does not check if issues
        that are not possible to be done directly through the app by the user are done
        (e.g. invalid type). All errors are added to a set and are a `QuestionValidationError`.
        """
        errors = set()

        question_text = self.question_text.strip()
        answer_options = [a.strip() for a in self.answer_options]
        non_empty_answers = self.remove_empty_answers(mutate_answers=False)

        if not question_text:
            errors.add(QuestionValidationError.MISSING_QUESTION)

        if len(question_text) > MAX_QUESTION_LENGTH:
            errors.add(QuestionValidationError.QUESTION_TOO_LONG)

        # At least two answers, and the first two answers, are required
        if len(answer_options) < 2 or not answer_options[0] or not answer_options[1]:
            errors.add(QuestionValidationError.MISSING_REQUIRED_ANSWERS)

        if any(len(answer) > MAX_ANSWER_LENGTH for answer in answer_options):
            errors.add(QuestionValidationError.ANSWER_TOO_LONG)

        if len(non_empty_answers) != len(set(non_empty_answers)):
            errors.add(QuestionValidationError.DUPLICATE_ANSWER)

        if self.correct_answer_index is None:
            errors.add(QuestionValidationError.NO_CORRECT_ANSWER)

        return errors

    def to_dict(self) -> dict:
        """Convert to a dictionary for serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Question":
        """Convert from a dictionary for deserialization."""
        try:
            return cls(**data)
        except TypeError as e:
            raise ValueError(f"Invalid format: {e}") from e
