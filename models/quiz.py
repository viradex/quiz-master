import random
import secrets
from dataclasses import asdict, dataclass
from datetime import datetime

from core.app.enums import QuizValidationError
from models.question import Question


@dataclass
class Quiz:
    """Represents a Quiz and the data fields it contains."""

    quiz_id: str
    quiz_title: str
    questions: list[Question]
    do_shuffle: bool
    is_premade: bool
    is_complete: bool
    updated_at: datetime | None = None

    @staticmethod
    def generate_random_id() -> str:
        """Generate a random ID. Static method; can be used when initializing a Quiz."""
        return secrets.token_hex(4)

    def add_question(self, question: Question, index: int | None = None) -> int:
        """Adds a new question to the quiz. Returns index of the question."""
        if index is None:
            self.questions.append(question)
            return len(self.questions) - 1
        else:
            self.questions.insert(index, question)
            return index

    def remove_question(self, question_id: str) -> None:
        """Removes a question from the quiz, based on the question ID."""
        self.questions = [q for q in self.questions if q.question_id != question_id]

    def get_question(self, index: int) -> Question:
        """Get a specific question."""
        return self.questions[index]

    def get_question_index(self, question_id: str) -> int | None:
        """Get the index of a specified question by ID, or None if it doesn't exist."""
        for i, question in enumerate(self.questions):
            if question.question_id == question_id:
                return i

        return None

    def get_all_questions(self) -> list[Question]:
        """Get all questions in the quiz."""
        return self.questions

    def shuffle_questions(self) -> None:
        """Randomly shuffles questions."""
        random.shuffle(self.questions)

    def move_question(self, question_id: str, new_index: int) -> None:
        """Move a question to the new specified index, pushing questions in front of it one index down."""
        questions = self.questions

        # Get the question index on the first question ID match
        old_index = next(
            (i for i, q in enumerate(questions) if q.question_id == question_id), None
        )

        if old_index is None:
            return

        question = questions.pop(old_index)
        questions.insert(new_index, question)

    def validate_quiz(self) -> set[QuizValidationError]:
        """
        Validates the quiz and its questions. Does validation ensuring the quiz is legal and can be
        safely used in a quiz game. Some question-specific validation is not included; for that, use
        `Question.validate_question()`. Returns a set containing all the errors as a `QuizValidationError`.
        """

        errors = set()
        seen_question_ids = set()

        # General quiz metadata information validation
        if not self.quiz_id or not isinstance(self.quiz_id, str):
            errors.add(QuizValidationError.MISSING_ID)

        if not self.quiz_title or not isinstance(self.quiz_title, str):
            errors.add(QuizValidationError.MISSING_TITLE)

        if not self.questions:
            errors.add(QuizValidationError.MISSING_QUESTIONS)

        if not isinstance(self.do_shuffle, bool):
            errors.add(QuizValidationError.NO_SHUFFLE_INFO)

        if not isinstance(self.is_premade, bool):
            errors.add(QuizValidationError.NO_PREMADE_INFO)

        if not isinstance(self.is_complete, bool):
            errors.add(QuizValidationError.NO_COMPLETENESS_INFO)

        # Individual question validation
        for question in self.questions:
            if question.question_id in seen_question_ids:
                errors.add(QuizValidationError.DUPLICATED_ID)

            seen_question_ids.add(question.question_id)

            # Ensures there are between 2-4 questions inclusive
            if (
                not isinstance(question.answer_options, list)
                or not 2 <= len(question.answer_options) <= 4
            ):
                errors.add(QuizValidationError.INVALID_ANSWERS)

            # If the correct answer index is out of the range for the amount of answers
            # (e.g. correct answer index is 4 when question indexes are only 0-3)
            if not isinstance(question.correct_answer_index, int) or not 0 <= int(
                question.correct_answer_index
            ) < len(question.answer_options):
                errors.add(QuizValidationError.INVALID_CORRECT_ANSWER)

            if not isinstance(question.time_limit, int) or question.time_limit <= 0:
                errors.add(QuizValidationError.INVALID_TIME)

        return errors

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
            # Try converting the saved date, if valid
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
                is_complete=data["is_complete"],
                updated_at=updated_at,
            )
        except TypeError as e:
            raise ValueError(f"Invalid format: {e}") from e
