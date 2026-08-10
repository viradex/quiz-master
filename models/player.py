"""
player.py

Defines a player in the quiz game and for the player registry in the server-side.
"""

from dataclasses import dataclass


@dataclass
class Player:
    """
    Creates a new Player instance, which is used for representing a game player within the system, in
    both the quiz game and the player registry. Provides methods and attributes for easier management
    of a single player.

    Arguments:
        player_id: A string describing the ID that should be used to uniquely identify this instance.
            A string is used as it can flexibly store IDs and can store many characters to make them
            more unique.

        nickname: A string describing the nickname to store with the Player. A string is used as it can
            flexibly store nicknames.

    All other arguments should not be filled in during initialization, and should be left to their
    default values.
    """

    player_id: str
    nickname: str

    # Total points earned in quiz game
    total_points: int = 0

    # Total questions answered correctly
    total_correct: int = 0

    # Points earned in the single question
    question_points: int = 0

    # Whether the previously-answered question was correct
    is_correct: bool = False

    # The previously-selected answer, or None if none was selected
    selected_answer: int | None = None

    # The time taken to submit the previous answer, or None if no answer was selected
    time_taken: float | None = None

    # Whether or not the player has submitted an answer yet
    submitted: bool = False

    def update_total_points(self, points: int) -> None:
        """
        Adds the number of points earned in the question to the total number of points earned, and sets the
        number of question points earned to the points passed. This method should be run upon completion of
        a question, when the total amount of points for a single question are known.

        Arguments:
            points: The number of points earned in the question. An integer is used as it is a whole number,
                which is what points are.

        Returns:
            None.
        """
        self.question_points = points
        self.total_points += points

    def update_correctness(self, is_correct: bool) -> None:
        """
        Updates the total number of correct answers if the question was answered correctly, and sets the
        `is_correct` property to be equal to the value passed.

        Arguments:
            is_correct: Whether or not the answer was correct or not. If it was correct, the total number of
                correct answers is updated, otherwise, it is not. The value passed here is set as the `is_correct`
                attribute.

        Returns:
            None.
        """
        self.is_correct = is_correct

        # Adds 1 if True, else 0 if False
        self.total_correct += is_correct

    def calculate_accuracy(self, total_questions: int) -> float:
        """
        Calculates the total accuracy of all questions answered correctly so far, and returns it as a percentage
        ranging from 0.0-1.0.

        Arguments:
            total_questions: The total number of questions completed so far, to accurately calculate the ratio
                of correct answers to total questions. The value should be greater than 0; if it is zero or below,
                to avoid a `ZeroDivisionError`, 0.0 is explicitly returned.

        Returns:
            A float ranging from 0.0-1.0 to represent a percentage, where 0.0 is 0% and 1.0 is 100%. A float is
            used for the percentage as it provides easier readability of values, and can be easily converted
            into a human-readable percentage if needed.
        """
        return self.total_correct / total_questions if total_questions > 0 else 0.0

    def submit_answer(
        self, points: int, selected_answer: int, time_taken: float, is_correct: bool
    ) -> None:
        """
        Submits an answer on behalf of this player, saving the data to this instance.

        Arguments:
            points: An integer containing the number of points the player earned in this question only, not the
                total points they have earned so far. An integer is used as the points are a whole number and
                used for calculations.

            selected_answer: The index of the answer selected, as a zero-based index respective to the answer the
                player selected, ranging from 0 to the number of valid answers, minus 1. For example, for a
                question with 4 answers, the valid range is 0-3.

            time_taken: A float derived from calculations with values derived from `time.monotonic()`, informing
                the number of seconds taken to answer the question, whether correct or incorrect. A monotonic time
                is used to avoid the time being changed by DST or NTP and causing issues.

            is_correct: Whether or not the answer provided is correct. A boolean is used as the value is naturally
                either a yes or no.

        Returns:
            None.
        """
        self.update_total_points(points)
        self.update_correctness(is_correct)

        self.selected_answer = selected_answer
        self.time_taken = time_taken
        self.submitted = True

    def submit_forced_answer(self) -> None:
        """
        Submits a forced answer on behalf of this player, meaning all values are left blank, but the player
        instance is marked as being submitted. Use this when, for example, the player did not answer in time.

        Returns:
            None.
        """
        self.question_points = 0
        self.is_correct = False
        self.selected_answer = None
        self.time_taken = None
        self.submitted = True

    def reset_for_question(self) -> None:
        """
        Resets all data fields on this instance that relate only to the previous question, not whole quiz
        statistics. For example, the number of question points earned is reset, but the total points earned is
        left intact.

        Returns:
            None.
        """
        self.question_points = 0
        self.is_correct = False
        self.selected_answer = None
        self.time_taken = None
        self.submitted = False
