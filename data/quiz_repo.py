"""
quiz_repo.py

A repository pattern for providing a simple interface to creating, reading, updating, and deleting
quizzes from disk.
"""

import json
from datetime import datetime

from models.quiz import Quiz
from utils.paths import get_quizzes_dir


class QuizRepository:
    """
    An abstraction for creating, reading, updating, and deleting quizzes from the disk as JSON, while providing
    a clean API for performing those actions while only working with the Quiz instance or quiz ID.

    This class manages both default and custom quizzes. Default quizzes cannot be created, updated, or
    deleted, but custom quizzes can be fully modified. Custom quizzes are saved as `{quiz_id}.json`.
    """

    def __init__(self) -> None:
        self.custom_quiz_path = get_quizzes_dir() / "custom"
        self.default_quiz_path = get_quizzes_dir() / "default"

        # Create in-memory dictionary to prevent repeated disk reads
        self.quiz_cache: dict[str, Quiz] = {}

    def get(self, quiz_id: str) -> Quiz | None:
        """
        Retrieves a Quiz from the disk/cache, identified by the quiz ID, if it exists.

        If the cache is empty, the cache is refreshed before retrieving the Quiz. The cache is not automatically
        refreshed if it already has at least one value in it.

        Arguments:
            quiz_id: A string describing the ID that is linked to the Quiz to retrieve. A string is used
                as it can flexibly store IDs and can store many characters to make them more unique.

        Returns:
            The Quiz object if it was found from the disk/cache, or None if the quiz could not be found from
            the quiz ID.
        """
        if not self.quiz_cache:
            self._load_cache()

        if not self.exists(quiz_id):
            return None

        return self.quiz_cache[quiz_id]

    def get_all(self) -> dict[str, Quiz]:
        """
        Retrieves all Quizzes from the registry as a dictionary with the quiz ID as the key. A copy of the
        quiz cache is returned.

        If the cache is empty, the cache is refreshed before retrieving the Quiz. The cache is not automatically
        refreshed if it already has at least one value in it.

        Returns:
            A dictionary containing all the Quiz objects identified by the quiz IDs, as a copy of the cache.
        """
        if not self.quiz_cache:
            self._load_cache()

        return self.quiz_cache.copy()

    def save(self, quiz: Quiz) -> None:
        """
        Saves a quiz to disk, as a custom quiz (not a default quiz). No validation checks are performed;
        validation is assumed to have been completed before this method is run. The quiz is saved in the custom
        quiz directory, with the quiz ID as the filename for the JSON save file. Overwrites any existing file
        if it has the same filename.

        The saved quiz is added to the quiz cache automatically.

        Arguments:
            quiz: The validated Quiz object to save to disk as a JSON file.

        Returns:
            None.
        """
        # Avoid naive datetime by using astimezone() for local timezone
        quiz.updated_at = datetime.now().astimezone()

        # Ensure custom quiz directory exists
        self.custom_quiz_path.mkdir(parents=True, exist_ok=True)

        # Converts Quiz to dictionary, then JSON, and saves
        file_path = self.custom_quiz_path / f"{quiz.quiz_id}.json"
        with open(file_path, mode="w", encoding="utf-8") as f:
            json.dump(quiz.to_dict(), f)

        # Automatically adds saved quiz to cache
        self.quiz_cache[quiz.quiz_id] = quiz

    def remove(self, quiz_id: str) -> bool:
        """
        Removes a quiz from the cache and disk, identified by the quiz ID.

        The old quiz is removed from the quiz cache automatically.

        Arguments:
            quiz_id: A string describing the ID that is linked to the Quiz to remove. A string is used
                as it can flexibly store IDs and can store many characters to make them more unique.

        Returns:
            A boolean specifying if removal was successful. True is returned if the quiz was found and removed,
            else, returns False if the quiz could not be found by ID.
        """
        # Checks if the expected file name exists or not
        file_path = self.custom_quiz_path / f"{quiz_id}.json"
        if not file_path.exists():
            return False

        # Remove from disk and cache
        file_path.unlink()
        self.quiz_cache.pop(quiz_id, None)

        return True

    def exists(self, quiz_id: str) -> bool:
        """
        Whether the disk/cache already contains the quiz ID provided.

        If the cache is empty, the cache is refreshed before retrieving the Quiz. The cache is not automatically
        refreshed if it already has at least one value in it.

        Arguments:
            quiz_id: A string describing the ID that is linked to the Quiz to check if it exists. A string is
                used as it can flexibly store IDs and can store many characters to make them more unique.

        Returns:
            A boolean stating if the ID exists or not. Returns True if the ID was found on disk or in the registry
            as a key, else, returns False.
        """
        if not self.quiz_cache:
            self._load_cache()

        return quiz_id in self.quiz_cache

    def refresh_cache(self) -> None:
        """
        Manually refresh the cache, such as when a quiz save file has been or is about to be added, removed,
        retrieved, or modified.

        Returns:
            None.
        """
        # Acts as a public-facing method for _load_cache()
        self._load_cache()

    def _load_cache(self) -> None:
        """
        Internal method. Clears the existing quiz cache and loads all of the quizzes currently on disk into
        the quiz cache, to refresh it for other methods that may modify the quiz cache. Ensures the quiz cache
        does not contain stale data.

        If the custom or default quiz directory does not exist, they are not created, but ignored.

        Returns:
            None.
        """
        # Ensure no stale data remains
        self.quiz_cache.clear()

        for directory in (self.default_quiz_path, self.custom_quiz_path):
            if not directory.exists():
                continue

            # Only reads .json files in the directory
            for file in directory.glob("*.json"):
                # Read the JSON file and convert it to a Python dictionary
                with open(file, mode="r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                    except (json.JSONDecodeError, UnicodeDecodeError) as e:
                        print(f"Invalid JSON in {file.name}: {e}")
                        continue

                if not isinstance(data, dict):
                    print(f"JSON must be an object in {file.name}")
                    continue

                # Convert dictionary to a Quiz object and store it in cache
                quiz = Quiz.from_dict(data)
                self.quiz_cache[quiz.quiz_id] = quiz
