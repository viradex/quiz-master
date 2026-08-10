"""
payloads.py

Defines data transfer objects (DTOs) for transferring data between different parts of the application
or through the network, that has many fields, requiring organization and stricter type-checking.

Payloads should only be used for data transfer that has several data fields. If the payload only has
about 1-3 fields, the payload can and should be a dictionary to avoid too many payloads that make the
code harder to read (for example, a payload with a single field).
"""

from dataclasses import asdict, dataclass


class BasePayload:
    """
    The base payload that all payloads inherit. Contains methods to convert the payload to and from a
    Python dictionary and the payload object, for easier data transfer.
    """

    def to_dict(self) -> dict:
        """
        Converts a payload to a dictionary. Useful for serialization for networking data transfer.

        Returns:
            The payload converted to a dictionary.
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "BasePayload":
        """
        Converts a dictionary to a payload. Useful for deserializing data from a network transfer.

        Arguments:
            data: The dictionary to convert to the payload object.

        Returns:
            The newly-created payload object from the dictionary provided.

        Raises:
            ValueError: If the dictionary provided did not follow the payload format.
        """
        try:
            return cls(**data)
        except TypeError as e:
            raise ValueError(f"Invalid payload format: {e}") from e


@dataclass
class QuestionPayload(BasePayload):
    """
    A payload, inheriting BasePayload, to represent a question in the system, for displaying on the UI.
    This payload can be used for both the client and server question UI screens, in a live game as well
    as for the previewing functionality in the quiz editor.

    Arguments:
        question_num: An integer detailing the current number of this question.

        total_questions: An integer detailing the total number of questions in the quiz.

        question_text: An string containing the question text itself.

        answer_options: An list of strings containing all available answer options for the question.

        time_limit: An integer containing the amount of time in seconds to complete the question.

        is_preview: Whether this payload is for a live game or for a preview from the quiz editor.

        read_only_quiz: If this payload is for a preview, whether the payload came from a read-only quiz.
    """

    question_num: int
    total_questions: int
    question_text: str
    answer_options: list[str]
    time_limit: int
    is_preview: bool = False
    read_only_quiz: bool = False


@dataclass
class ClientResultsPayload(BasePayload):
    """
    A payload, inheriting BasePayload, to represent the question results in the system, for displaying
    on the UI. This payload can be used for the client results UI screen in a live game.

    Arguments:
        question_text: An string containing the question text itself.

        answer_options: An list of strings containing all available answer options for the question.

        correct_answer: The correct zero-based answer index from the answer options.

        selected_answer: The selected zero-based answer index from the answer options, or None if the
            question ended before an answer was selected.

        is_correct: A boolean identifying whether the user answered correctly or not.

        time_taken: A float detailing the amount of time in seconds taken to answer the question, or None
            if the question ended before an answer was selected.

        total_points: An integer containing the total points gained from the entire quiz so far.

        gained_points: An integer containing the gained points from just this question.

        rank: An integer for the numerical rank in the leaderboard, or None if the question is the final
            question of the quiz.

        nickname: A string containing the nickname of the current player.
    """

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
    """
    A payload, inheriting BasePayload, to represent the question results in the system, for displaying
    on the UI. This payload can be used for the server results UI screen in a live game.

    Arguments:
        question_num: An integer detailing the current number of the question.

        total_questions: An integer detailing the total number of questions in the quiz.

        accuracy: A float from 0.0-1.0 representing the percentage of players who answered correctly.

        answer_frequency: A list of integers containing the number of responses, respective to the index
            of the list for the corresponding answer.

        question_text: An string containing the question text itself.

        answer_options: An list of strings containing all available answer options for the question.

        correct_answer: The correct zero-based answer index from the answer options.

        leaderboard: A list of dictionaries containing the entire leaderboard of the quiz game so far,
            including gained points. Set to None if this is the last question of the quiz.
    """

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
    """
    A payload, inheriting BasePayload, to represent the final results in the system, for displaying
    on the UI. This payload can be used for the client final results UI screen in a live game.

    Arguments:
        rank: An integer for the numerical rank in the leaderboard.

        total_points: An integer containing the total points gained from the entire quiz game.

        total_correct: An integer containing the total answers that were answered correctly in the
            entire quiz game.

        total_questions: An integer containing the total questions in the quiz game.

        accuracy: A float from 0.0-1.0 representing the percentage of questions answered correctly.

        on_podium: A boolean identifying whether the player ended up on the podium or not.

        is_first: A boolean identifying whether the player is in first place or not.

        is_last: A boolean identifying whether the player is in last place or not.

        behind_nickname: A string containing the nickname of the player in front, or None if the user
            is in first place.

        points_behind: An integer containing the number of points the user is behind the player in front.

        nickname: A string containing the nickname of the current player.

        leaderboard: A list of dictionaries containing the immediate player positions around the
            current user in the leaderboard.
    """

    rank: int
    total_points: int
    total_correct: int
    total_questions: int
    accuracy: float
    on_podium: bool
    is_first: bool
    is_last: bool
    behind_nickname: str | None
    points_behind: int
    nickname: str
    leaderboard: list[dict]


@dataclass
class ServerFinalResultsPayload(BasePayload):
    """
    A payload, inheriting BasePayload, to represent the final results in the system, for displaying
    on the UI. This payload can be used for the server final results UI screen in a live game.

    Arguments:
        winner: A string containing the nickname of the winning player (the player in first place).

        highest_points: An integer containing the highest points earned from a single player (aka the
            total points earned by the winner).

        fastest_answer: A float detailing the smallest amount of time in seconds taken to answer any
            question, or None if no data is available (e.g. if no answers were actually submitted in
            the entire quiz game).

        average_accuracy: A float from 0.0-1.0 representing the average of the accuracy of all players,
            in terms of the number of questions answered correctly.

        total_players: An integer containing the total players who participated in the entire quiz game
            (did not leave early).

        total_questions: An integer containing the total questions in the quiz game.

        leaderboard: A list of dictionaries containing the entire leaderboard of the quiz game.
    """

    winner: str
    highest_points: int
    fastest_answer: float | None
    average_accuracy: float
    total_players: int
    total_questions: int
    leaderboard: list[dict]
