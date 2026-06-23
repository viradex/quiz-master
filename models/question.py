from dataclasses import dataclass
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
        return {
            "question_id": self.question_id,
            "question_text": self.question_text,
            "answer_options": self.answer_options,
            "correct_answer_index": self.correct_answer_index,
            "time_limit": self.time_limit,
        }

    @staticmethod
    def from_dict(data: dict) -> Question:
        """Convert from a dictionary for deserialization."""
        return Question(
            question_id=data["question_id"],
            question_text=data["question_text"],
            answer_options=data["answer_options"],
            correct_answer_index=data["correct_answer_index"],
            time_limit=data["time_limit"],
        )
