import secrets
from dataclasses import dataclass, asdict

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

    def get_correct_answer(self) -> str:
        """Retrieves the correct answer text."""
        return self.answer_options[self.correct_answer_index]

    def validate_question(self) -> set[QuestionValidationError]:
        errors = set()

        question_text = self.question_text.strip()
        answer_options = [a.strip() for a in self.answer_options]
        non_empty_answers = [a for a in answer_options if a != ""]

        if not question_text:
            errors.add(QuestionValidationError.MISSING_QUESTION)

        if len(question_text) > MAX_QUESTION_LENGTH:
            errors.add(QuestionValidationError.QUESTION_TOO_LONG)

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
