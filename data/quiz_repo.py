import json
from datetime import datetime
from pathlib import Path

from models.quiz import Quiz


# NOTE Custom quizzes are saved as {quiz_id}.json
class QuizRepository:
    """Discovers and loads quizzes from disk."""

    def __init__(self) -> None:
        """Initialize the quiz repo by setting paths and empty cache."""
        self.data_path = Path(__file__).resolve().parent

        self.custom_quiz_path = self.data_path / "quizzes" / "custom"
        self.default_quiz_path = self.data_path / "quizzes" / "default"

        self.quiz_cache: dict[str, Quiz] = {}

    def get(self, quiz_id: str) -> Quiz | None:
        """Load a certain quiz by ID stored on disk."""
        # self.exists() loads cache automatically
        if not self.exists(quiz_id):
            return None

        return self.quiz_cache[quiz_id]

    def get_all(self) -> dict[str, Quiz]:
        """Return a dictionary of all quizzes on disk (quiz ID -> quiz data)."""
        if not self.quiz_cache:
            self._load_cache()

        return self.quiz_cache.copy()

    def edit(self, quiz_id: str, data: dict) -> bool:
        """Edit a quiz save file on disk based on ID."""
        if not self.quiz_cache:
            self._load_cache()

        quiz = self.get(quiz_id)
        if quiz is None:
            return False

        # Set preferable for membership tests due to uniqueness
        # and faster performance (though negligible here)
        protected = {"quiz_id", "is_premade"}

        for key, value in data.items():
            if key in protected:
                continue

            # Checks if the quiz has an attribute with same name
            if hasattr(quiz, key):
                # Set attribute in quiz by name
                setattr(quiz, key, value)

        self.save(quiz)
        return True

    def save(self, quiz: Quiz) -> None:
        """Save a quiz instance to disk in the custom quiz directory, with the quiz ID as the filename."""
        quiz.updated_at = datetime.now()

        # TODO only for dev to easily test quiz editor without a billion save files
        print("Saving temporarily disabled")
        return

        file_path = self.custom_quiz_path / f"{quiz.quiz_id}.json"
        with open(file_path, mode="w", encoding="utf-8") as f:
            json.dump(quiz.to_dict(), f)

        self.quiz_cache[quiz.quiz_id] = quiz

    def remove(self, quiz_id: str) -> bool:
        """Delete a custom quiz from disk."""
        file_path = self.custom_quiz_path / f"{quiz_id}.json"
        if not file_path.exists():
            return False

        file_path.unlink()
        self.quiz_cache.pop(quiz_id, None)

        return True

    def exists(self, quiz_id: str) -> bool:
        """Check if a quiz exists by ID on disk."""
        if not self.quiz_cache:
            self._load_cache()

        return quiz_id in self.quiz_cache

    def refresh_cache(self) -> None:
        """Refresh the cache, such as when a quiz save file has been added, removed, or modified."""
        self._load_cache()

    def _load_cache(self) -> None:
        """Loads the cache of all quizzes on disk in `quiz_cache`."""
        self.quiz_cache.clear()

        for directory in (self.custom_quiz_path, self.default_quiz_path):
            if not directory.exists():
                continue

            for file in directory.glob("*.json"):
                with open(file, mode="r", encoding="utf-8") as f:
                    data = json.load(f)

                quiz = Quiz.from_dict(data)
                self.quiz_cache[quiz.quiz_id] = quiz
