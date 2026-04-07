import json
from pathlib import Path


class JSONLoader:
    """Class for reading the JSON file relating to questions."""

    def __init__(self) -> None:
        """Initialize paths for the questions JSON file."""
        self.base_dir = Path(__file__).resolve().parent.parent
        self.data_dir = self.base_dir / "data"
        self.json_path = self.data_dir / "questions.json"

    def _ensure_data_dir(self) -> None:
        """Ensure the data directory exists, and create it if it doesn't."""
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _ensure_json_exists(self) -> None:
        """Ensure the JSON file exists (along with the data directory), and create it if it doesn't."""

        self._ensure_data_dir()

        if self.json_path.exists():
            return

        self.json_path.touch()

        # TODO remove when in-app question editing is added
        print(
            "WARNING: No questions.json file detected. A new one has been created in data/questions.json, however the file is empty."
        )

    def load_all(self) -> list[dict[str, str | int | list[str]]]:
        """
        Load all questions from the JSON file, ensuring it and its parent directory exist beforehand.

        Returns:
            list: A list of dictionaries containing respective question information.
        """

        self._ensure_json_exists()

        with open(self.json_path, "r", newline="", encoding="utf-8") as file:
            data = json.load(file)

        return data
