from dataclasses import dataclass, asdict


# Payloads should only be used for data transfer that has multiple data fields.
# If it's 1-3 fields, it can and should just be a plain old dictionary
class BasePayload:
    """Base payload for all payloads."""

    def to_dict(self) -> dict:
        """Convert payload to a dictionary. Useful for serialization for networking data transfer."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict):
        """Convert dictionary to a payload. Useful for deserializing data from a network transfer."""
        try:
            return cls(**data)
        except TypeError as e:
            raise ValueError(f"Invalid payload format: {e}") from e


@dataclass
class QuestionPayload(BasePayload):
    """Used for question data (for client/server and the quiz editor for previewing functionality)."""

    question_num: int
    total_questions: int
    question_text: str
    answer_options: list[str]
    time_limit: int
    is_preview: bool = False


@dataclass
class ClientResultsPayload(BasePayload):
    """Used for per-question results for the client."""

    question_text: str
    answer_options: list[str]
    correct_answer: int
    selected_answer: int | None
    is_correct: bool
    time_taken: float | None
    total_points: int
    gained_points: int
    rank: int | None
    nickname: str


@dataclass
class ServerResultsPayload(BasePayload):
    """Used for per-question results for the server."""

    question_num: int
    total_questions: int
    accuracy: float
    answer_frequency: list[int]
    question_text: str
    answer_options: list[str]
    correct_answer: int
    leaderboard: list[dict] | None


@dataclass
class ClientFinalResultsPayload(BasePayload):
    """Used for final results for the client."""

    rank: int
    total_points: int
    total_correct: int
    total_questions: int
    accuracy: float
    on_podium: bool
    is_first: bool
    is_last: bool
    behind_nickname: str | None
    points_behind: int | None
    nickname: str
    leaderboard: list[dict]


@dataclass
class ServerFinalResultsPayload(BasePayload):
    """Used for final results for the server."""

    winner: str
    highest_points: int
    fastest_answer: float
    average_accuracy: float
    total_players: int
    total_questions: int
    leaderboard: list[dict]
