from dataclasses import dataclass, asdict
from datetime import datetime
import random
import secrets

from core.app.enums import QuizValidationResult
from models.question import Question


@dataclass
class Quiz:
    """Represents a Quiz and the data fields it contains."""

    quiz_id: str
    quiz_title: str
    questions: list[Question]
    do_shuffle: bool
    is_premade: bool
    updated_at: datetime | None = None

    @staticmethod
    def generate_random_id() -> str:
        """Generate a random ID. Static method; can be used when initializing a Quiz."""
        return secrets.token_hex(4)

    def add_question(self, question: Question) -> None:
        """Adds a new question to the quiz."""
        self.questions.append(question)

    def remove_question(self, question_id: str) -> None:
        """Removes a question from the quiz, based on the question ID."""
        self.questions = [q for q in self.questions if q.question_id != question_id]

    def get_question(self, index: int) -> Question:
        """Get a specific question."""
        return self.questions[index]

    def get_all_questions(self) -> list[Question]:
        """Get all questions in the quiz."""
        return self.questions

    def shuffle_questions(self) -> None:
        """Randomly shuffles questions."""
        random.shuffle(self.questions)

    def validate_quiz(self) -> tuple[bool, QuizValidationResult, int | None]:
        """
        Validates the quiz and its questions.

        Return format is `(success, error, answer_index)`. If the error is with the quiz
        in general, `answer_index` is None. The error type is of `QuizValidationResult`.
        """

        # General quiz metadata information validation
        if not self.quiz_id or not isinstance(self.quiz_id, str):
            return False, QuizValidationResult.EMPTY_ID, None

        if not self.quiz_title or not isinstance(self.quiz_title, str):
            return False, QuizValidationResult.EMPTY_TITLE, None

        if not self.questions:
            return False, QuizValidationResult.EMPTY_QUESTIONS, None

        if not isinstance(self.do_shuffle, bool):
            return False, QuizValidationResult.NO_SHUFFLE_INFO, None

        if not isinstance(self.is_premade, bool):
            return False, QuizValidationResult.NO_PREMADE_INFO, None

        if self.updated_at is not None and self.updated_at > datetime.now():
            return False, QuizValidationResult.INVALID_UPDATED_AT, None

        # Store all IDs that were currently used
        # Set used to increase lookup speed
        seen_ids = set()

        # Individual question validation
        for index, question in enumerate(self.questions):
            if question.question_id in seen_ids:
                return False, QuizValidationResult.ID_USED, index

            seen_ids.add(question.question_id)

            if not question.question_text.strip():
                return False, QuizValidationResult.EMPTY_QUESTION, index

            if (
                not isinstance(question.answer_options, list)
                or not 2 <= len(question.answer_options) <= 4
            ):
                return False, QuizValidationResult.INVALID_ANSWERS, index

            if not (0 <= question.correct_answer_index < len(question.answer_options)):
                return False, QuizValidationResult.INVALID_CORRECT_ANSWER, index

            if question.time_limit <= 0:
                return False, QuizValidationResult.INVALID_TIME, index

        return True, QuizValidationResult.OK, None

    def to_dict(self) -> dict:
        """Convert to a dictionary for serialization."""
        data = asdict(self)

        if self.updated_at is not None:
            # Avoid saving microseconds using timespec="seconds"
            data["updated_at"] = self.updated_at.isoformat(timespec="seconds")

        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Quiz":
        """Convert from a dictionary for deserialization."""
        updated_at = data.get("updated_at")

        try:
            if updated_at is not None:
                updated_at = datetime.fromisoformat(updated_at)
        except (TypeError, ValueError):
            updated_at = None

        try:
            return cls(
                quiz_id=data["quiz_id"],
                quiz_title=data["quiz_title"],
                questions=[Question.from_dict(q) for q in data["questions"]],
                do_shuffle=data["do_shuffle"],
                is_premade=data["is_premade"],
                updated_at=updated_at,
            )
        except TypeError as e:
            raise ValueError(f"Invalid format: {e}") from e
