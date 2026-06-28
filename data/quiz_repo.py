from pathlib import Path
import json

from models.quiz import Quiz


class QuizRepository:
    """Discovers and loads quizzes from disk."""

    def __init__(self) -> None:
        """Initialize the quiz repo by setting paths and empty cache."""
        self.data_path = Path(__file__).resolve().parent

        self.custom_quiz_path = self.data_path / "custom"
        self.default_quiz_path = self.data_path / "default"

        self.quiz_cache = {}

    def _load_cache(self) -> None:
        """Loads the cache of all quizzes on disk in `quiz_cache`."""
        self.quiz_cache.clear()

        # Check child directories for .json files
        for file in self.data_path.rglob("*.json"):
            with open(file, mode="r", newline="", encoding="utf-8") as f:
                data = json.load(f)

            quiz = Quiz.from_dict(data)
            self.quiz_cache[quiz.quiz_id] = quiz

    def load_quizzes(self) -> dict[str, Quiz]:
        """Return a dictionary of all quizzes on disk (quiz ID -> quiz data)."""
        if not self.quiz_cache:
            self._load_cache()

        return self.quiz_cache.copy()

    def load_quiz(self, quiz_id: str) -> Quiz | None:
        """Load a certain quiz by ID stored on disk."""
        if not self.quiz_exists(quiz_id):
            return None

        return self.quiz_cache[quiz_id]

    def quiz_exists(self, quiz_id: str) -> bool:
        """Check if a quiz exists by ID on disk."""
        if not self.quiz_cache:
            self._load_cache()

        return quiz_id in self.quiz_cache

    def refresh_cache(self) -> None:
        """Refresh the cache, such as when a quiz save file has been added, removed, or modified."""
        self._load_cache()
