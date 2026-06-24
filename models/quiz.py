from dataclasses import dataclass
import random
from enum import Enum

from models.question import Question


@dataclass
class Quiz:
    """Represents a Quiz and the data fields it contains (not file system manipulation)."""

    quiz_id: str
    quiz_title: str
    questions: list[Question]

    def add_question(self, question: Question) -> None:
        """Adds a new question to the quiz."""
        self.questions.append(question)

    def remove_question(self, question_id: str) -> None:
        """Removes a question from the quiz, based on the question ID."""
        # TODO this removes all matching IDs, it shouldn't matter
        # but maybe make it only remove the first occurrence?
        self.questions = [q for q in self.questions if q.question_id != question_id]

    def get_question(self, index: int) -> Question:
        """Get a specific question."""
        return self.questions[index]

    def get_all_questions(self) -> list[Question]:
        """Get all questions in the quiz."""
        return self.questions

    def shuffle_questions(self) -> None:
        """Randomly shuffles and moves questions."""
        random.shuffle(self.questions)

    def validate_quiz(self) -> tuple[bool, str, int | None]:
        """
        Validates the quiz and its questions.

        Return values:
            `(False, "empty_id", None)`
                Quiz ID does not exist or is not a string.

            `(False, "empty_title", None)`
                Quiz title does not exist or is not a string.

            `(False, "empty_questions", None)`
                Quiz questions do not exist.

            `(False, "id_used", index)`
                Question ID has been duplicated.

            `(False, "empty_question", index)`
                Question text is blank.

            `(False, "invalid_answers", index)`
                Answers are not a list or are out of the valid range.

            `(False, "invalid_correct_answer", index)`
                The correct answer index is not a number or out of the valid range.

            `(False, "invalid_time", index)`
                The time is not a positive integer.

            `(True, "", None)`
                All validation checks passed.

        Returns:
            Return format is `(passed, error, answer_index)` for values discussed above.
        """

        # General quiz metadata information validation
        if not self.quiz_id or not isinstance(self.quiz_id, str):
            return (False, "empty_id", None)

        if not self.quiz_title or not isinstance(self.quiz_title, str):
            return (False, "empty_title", None)

        if not self.questions:
            return (False, "empty_questions", None)

        # Store all IDs that were currently used
        # Set used to increase lookup speed
        seen_ids = set()

        # Individual question validation
        for index, question in enumerate(self.questions):
            if question.question_id in seen_ids:
                return (False, "id_used", index)

            seen_ids.add(question.question_id)

            if not question.question_text.strip():
                return (False, "empty_question", index)

            if (
                not isinstance(question.answer_options, list)
                or not 2 <= len(question.answer_options) <= 4
            ):
                return (False, "invalid_answers", index)

            if question.correct_answer_index not in range(len(question.answer_options)):
                return (False, "invalid_correct_answer", index)

            if question.time_limit <= 0:
                return (False, "invalid_time", index)

        return (True, "", None)

    def to_dict(self) -> dict:
        """Convert to a dictionary for serialization."""
        return {
            "quiz_id": self.question_id,
            "quiz_title": self.question_text,
            "questions": [q.to_dict() for q in self.questions],
        }

    @staticmethod
    def from_dict(data: dict) -> Quiz:
        """Convert from a dictionary for deserialization."""
        return Quiz(
            quiz_id=data["quiz_id"],
            quiz_title=data["quiz_title"],
            questions=[Question.from_dict(q) for q in data["questions"]],
        )
