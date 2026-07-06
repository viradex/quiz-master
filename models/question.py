from dataclasses import dataclass, asdict
import secrets


@dataclass
class Question:
    """Represents a single question in a Quiz."""

    question_id: str
    question_text: str
    answer_options: list[str]
    correct_answer_index: int
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

    def update_question(
        self,
        question_text: str,
        answer_options: list[str],
        correct_answer_index: int,
        time_limit: int,
    ) -> None:
        """Update certain properties of a Question."""
        self.question_text = question_text
        self.answer_options = answer_options
        self.correct_answer_index = correct_answer_index
        self.time_limit = time_limit

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
