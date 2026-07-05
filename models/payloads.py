from dataclasses import dataclass, asdict


# Payloads should only be used for data transfer that has multiple data fields.
# If it's 1-3 fields, it can and should just be a plain old dictionary
class BasePayload:
    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict):
        try:
            return cls(**data)
        except TypeError as e:
            raise ValueError(f"Invalid payload format: {e}") from e


@dataclass
class QuestionPayload(BasePayload):
    question_num: int
    total_questions: int
    question_text: str
    answer_options: list[str]
    time_limit: int


@dataclass
class ClientResultsPayload(BasePayload):
    question_text: str
    answer_options: list[str]
    correct_answer: int
    selected_answer: int
    is_correct: bool
    time_taken: float | None
    total_points: int
    gained_points: int
    rank: int | None
    nickname: str


@dataclass
class ServerResultsPayload(BasePayload):
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
    winner: str
    highest_points: int
    fastest_answer: float
    average_accuracy: float
    total_players: int
    total_questions: int
    leaderboard: list[dict]
