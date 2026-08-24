"""
quiz_manager.py

Contains the logic for a quiz game. Constructs payloads for sending to clients and server. However,
this class does not run the game itself (that is delegated to `GameController`, which also uses this
class for quiz logic).
"""

import math

from models.leaderboard import Leaderboard
from models.payloads import (
    ClientFinalResultsPayload,
    ClientResultsPayload,
    QuestionPayload,
    ServerFinalResultsPayload,
    ServerResultsPayload,
)
from models.player import Player
from models.question import Question
from models.quiz import Quiz


class QuizManager:
    """
    Manages the quiz game rules, containing logic for running the quiz game and calculations, as well as
    constructing payloads to send to the server and clients. This does not run the actual game itself,
    but exposes methods for running the logic.
    """

    def __init__(self) -> None:
        self.quiz: Quiz | None = None
        self.players: dict[str, Player] = {}
        self.leaderboard = Leaderboard()

        # Used for statistics throughout the game
        self.total_start_players: int = 0
        self.all_time_taken: list[float] = []
        self.all_accuracies: list[float] = []

    def load_quiz(self, quiz: Quiz) -> None:
        """
        Loads and uses the Quiz provided to run the quiz game off of. Shuffles questions if required.

        Arguments:
            quiz: The Quiz to run the game off of. A Quiz object is used as it contains the required
                metadata used for running the game.

        Returns:
            None.

        Raises:
            ValueError: If the quiz provided contains no questions.
        """
        self.quiz = quiz

        if not self.quiz.questions:
            raise ValueError("The quiz loaded has no questions")

        # Shuffle questions if the quiz property do_shuffle is True
        self.quiz.shuffle_questions()

    def add_player(self, player: Player) -> None:
        """
        Adds a player to the quiz game and the leaderboard.

        Arguments:
            player: The Player to add to the quiz manager and game. A Player object is used as it allows using
                its helper properties and methods, and is also what the leaderboard expects.

        Returns:
            None.
        """
        self.players[player.player_id] = player
        self.leaderboard.add_player(player)

    def remove_player(self, player_id: str) -> None:
        """
        Removes a player from the quiz game and the leaderboard. If the player ID does not exist, nothing
        happens.

        Arguments:
            player_id: A string describing the ID of the Player instance to remove. A string is used as it
                can flexibly store IDs and can store many characters to make them more unique.

        Returns:
            None.
        """
        self.players.pop(player_id, None)
        self.leaderboard.remove_player(player_id)

    def get_question(self, index: int) -> Question:
        """
        Retrieve a Question from the given `index` in the quiz. The index is not the question number, and is
        a zero-based index corresponding to the respective question stored in the Quiz. Negative indexes are
        disallowed.

        Arguments:
            index: The index of the question position in the Quiz, as a non-negative integer. The maximum value
                allowed is the number of questions in the quiz minus one. An integer is used as it is used
                for indexing in lists.

        Returns:
            The Question at the provided index.

        Raises:
            RuntimeError: If the Quiz object has not been loaded yet via `load_quiz()`.

            IndexError: If the question index provided is out of range. Negative indexes are disallowed and they
                must not exceed the length of the questions list.
        """
        if self.quiz is None:
            raise RuntimeError("The quiz has not been loaded yet")

        # Use pre-checks rather than try/except to avoid negative indexes, which Python allows
        if not 0 <= index < len(self.quiz.questions):
            raise IndexError(f"Question index {index} is out of range")

        return self.quiz.questions[index]

    def get_total_questions(self) -> int:
        """
        Gets the total number of questions in the quiz. This does not get the highest zero-based question index,
        however that can be derived from getting the return value of this method and subtracting one from it.

        ```
        # User-friendly total questions
        get_total_questions()  # -> 3

        # Internal max question index
        get_total_questions() - 1  # -> 2
        ```

        Returns:
            An integer that represents the total number of questions in the quiz game. This value can be used
            to find the highest internal question index by subtracting one from it.

        Raises:
            RuntimeError: If the Quiz object has not been loaded yet via `load_quiz()`.
        """
        if self.quiz is None:
            raise RuntimeError("The quiz has not been loaded yet")

        return len(self.quiz.questions)

    def prepare_for_game(self) -> None:
        """
        Prepares for the game to begin. Snapshots the current total players in the game for accurate statistics
        when the game is over, without it being modified when players leave during the game.

        Returns:
            None.
        """
        self.total_start_players = len(self.players)

    def prepare_for_question(self) -> None:
        """
        Prepares for an upcoming question. This method should be run before the next question begins. Snapshots
        the current points in the leaderboard for a delta calculation when the question ends.

        Returns:
            None.
        """
        self.leaderboard.snapshot_points()

    def submit_answer(
        self,
        player_id: str,
        points: int,
        selected_answer: int,
        time_taken: float,
        is_correct: bool,
    ) -> None:
        """
        Submits an answer on behalf of a player, based on the data passed. **The data is not validated here;
        it is assumed to have already been validated!** Saves the data to the respective Player object, and,
        if the answer provided was marked as correct, adds the time taken to the global stats.

        Arguments:
            player_id: A string describing the ID of the Player instance. A string is used as it can flexibly
                store IDs and can store many characters to make them more unique.

            points: An integer containing the number of points the player earned in this question only, not the
                total points they have earned so far. An integer is used as the points are a whole number and
                used for calculations.

            selected_answer: The index of the answer selected, as a zero-based index respective to the answer the
                player selected, ranging from 0 to the number of valid answers, minus 1. For example, for a
                question with 4 answers, the valid range is 0-3.

            time_taken: A float derived from calculations with values derived from `time.monotonic()`, informing
                the number of seconds taken to answer the question, whether correct or incorrect. A monotonic time
                is used to avoid the time being changed by DST or NTP and causing issues.

            is_correct: Whether or not the answer provided is correct. This can be checked using the
                `is_answer_correct()` method. A boolean is used as the value is naturally either a yes or no.

        Returns:
            None.
        """
        player = self.players[player_id]
        player.submit_answer(points, selected_answer, time_taken, is_correct)

        # Adds time to the time taken global stats if the answer is correct.
        # Ensures the answer is correct before adding as it is unfair if a player
        # answers instantly but the answer is incorrect.
        if is_correct:
            self.all_time_taken.append(time_taken)

    def finish_question(self) -> None:
        """
        Run when the question has concluded, by forcing all players who haven't submitted yet to submit, and
        sorting the leaderboard, as well as calculating the question accuracy for global statistics.

        Returns:
            None.
        """
        self.force_remaining_submissions()
        self.leaderboard.sort_players()

        self.all_accuracies.append(self.calculate_question_accuracy())

    def force_remaining_submissions(self) -> None:
        """
        Forces all players who are not marked as having submitted an answer yet to forcefully submit an answer,
        for example, if the time has run out or the host wishes to skip the question early. This method ensures
        all players are marked as submitted.

        Returns:
            None.
        """
        for player in self.players.values():
            if not player.submitted:
                player.submit_forced_answer()

    def all_players_answered(self) -> bool:
        """
        Checks if all players currently in the quiz game have submitted an answer yet, whether forcefully via
        or not, and returns the state.

        Returns:
            Whether or not all the players have submitted an answer. True if all players have submitted an answer,
            else False if at least one person has not yet submitted an answer yet.
        """
        # Only returns True if all submitted values were True
        return all(player.submitted for player in self.players.values())

    def reset_for_question(self) -> None:
        """
        Reset all non-permanent individual player data for the next question, for all the players in the game.

        Returns:
            None.
        """
        for player in self.players.values():
            player.reset_for_question()

    def is_answer_valid(self, question: Question, answer_index: int) -> bool:
        """
        Checks if the answer index provided is in the valid answer range for the question provided. This should
        be used for validation before submitting the player answer.

        Arguments:
            question: The Question instance to check on if the answer index provided is valid. Ensures the
                index is within the valid range based on the number of answers in the question. A Question
                instance is used as it is simpler than manually passing in only the answers.

            answer_index: The index of the answer to check, as a zero-based index respective to the answer. An
                integer is used as it works well as an index and for range checks.

        Returns:
            Whether or not the answer index provided is legal. True if the answer is in the valid range, else
            False. If the value is False, the answer should not be submitted.
        """
        return 0 <= answer_index < len(question.answer_options)

    def is_answer_correct(self, question: Question, answer_index: int) -> bool:
        """
        Checks if the answer index provided matches the correct answer index of the question provided. If it
        does, that means the answer is correct. This method does not check if the answer index provided is out
        of the valid range.

        Arguments:
            question: The Question instance to check on if the answer index provided is correct. A Question
                instance is used as it is simpler than manually passing in only the answer index.

            answer_index: The index of the answer to check, as a zero-based index respective to the answer. An
                integer is used as it works well as an index and for range checks.

        Returns:
            Whether or not the answer index provided is correct. True if the answer is correct, else False.
        """
        return answer_index == question.correct_answer_index

    def calculate_points(self, time_taken: float, max_time: float) -> int:
        """
        Calculates the points the player earned, depending on the time taken compared to the maximum time allowed
        on the question. The primary formula used for calculating the number of points is a linear decay formula.

        The function used for calculating points is defined as a piecewise, when the condition `m > 0.5` is satisfied:

        > `P(t) = 1000`

        > where `0 <= t <= 0.5`

        and:

        > `P(t) = -(500 / (m - 0.5)) * (t - 0.5) + 1000`

        > where `0.5 < t <= m`

        Where:
        - `P(t)` is the number of points
        - `t` is the time taken in seconds (`time_taken`)
        - `m` is the maximum time for the question in seconds (`max_time`)

        The number of points returned is `0` if the time taken is not in the range `[0, m]`.

        Arguments:
            time_taken: The time taken in seconds for the player to submit an answer. This should be counted
                up from 0, not timed down from the maximum time allowed. A float is used as the time is
                counted with precision to ensure more accurate points.

            max_time: The maximum time allowed to answer the question, in seconds. This value must be greater
                than 0.5. Both floats and integers are accepted, as the maximum time only needs to be a
                numerical value.

        Returns:
            The final number of points calculated, floored. The number of points is always between 500-1000,
            inclusive, or 0 if the time taken is not in the valid range.

        Raises:
            ValueError: If the maximum time does not satisfy the condition `m > 0.5`.
        """
        # If max_time does not satisfy condition m > 0.5
        if max_time <= 0.5:
            raise ValueError("max_time must be greater than 0.5")

        # If time_taken is not in the range [0, m]
        if time_taken < 0 or time_taken > max_time:
            return 0

        if time_taken <= 0.5:
            # Full score window for very fast responses
            points = 1000
        elif time_taken > 0.5 and time_taken <= max_time:
            # Apply linear decay to reduce score at constant rate
            slope = -500 / (max_time - 0.5)
            points = slope * (time_taken - 0.5) + 1000

        # Remove decimal values by flooring
        return math.floor(points)

    def calculate_question_accuracy(self) -> float:
        """
        Calculates the average accuracy across all players for the question that was last completed.

        Returns:
            A float that represents a percentage, ranging from 0.0 to 1.0, where 0.0 represents 0% and 1.0
            represents 100%. If there are no players who answered correctly, 0 is explicitly returned. A
            float is used for the percentage as it provides easier readability of values, and can be easily
            converted into a human-readable percentage if needed.
        """
        correctness = [player.is_correct for player in self.players.values()]

        # As True = 1 and False = 0, this counts all Trues
        corrects = sum(correctness)
        total = len(correctness)

        # Avoid ZeroDivisionError
        percentage = corrects / total if total > 0 else 0.0
        return percentage

    def calculate_answer_frequency(self, num_answers: int) -> list[int]:
        """
        Calculates the number of responses for each answer across all players for the question that was last
        completed. This method only counts actual responses; if the selected answer is None, it is not counted.
        The length of the list returned is the same as the number of answers.

        Arguments:
            num_answers: The number of answers in the last completed question. The number provided in this
                argument is the same as the length of the return value. An integer is used as it can be used
                easily in loops and indexing.

        Returns:
            A list that contains the number of responses for each respective answer in the list. For example,
            index 0 contains the number of responses for the first answer.
        """
        answers_frequency = []
        selected_answers = [player.selected_answer for player in self.players.values()]

        # Adds number of answer submissions for each answer option. None is never
        # counted as the answer is only ever an integer due to range().
        for answer in range(num_answers):
            answers_frequency.append(selected_answers.count(answer))

        return answers_frequency

    def get_question_data(
        self, question: Question, question_num: int
    ) -> QuestionPayload:
        """
        Gets the question data from the question provided and returns it structured in a data transfer object
        payload, for use by both the server and clients to display a question to the UI.

        Arguments:
            question: The Question instance to get the data from. A Question instance is used as it stores
                multiple data fields that are required for the payload, and is cleaner to pass directly rather
                than all the attributes separately.

            question_num: The question number of this question. This argument is required to be provided
                separately from the Question object as the question does not contain the question number in its
                data. An integer is used as the number is a whole number.

        Returns:
            The QuestionPayload instance to provide to the server and clients to display a question to the UI.
        """
        total_questions = self.get_total_questions()
        question_text = question.question_text
        answer_options = question.answer_options
        time_limit = question.time_limit

        return QuestionPayload(
            question_num=question_num,
            total_questions=total_questions,
            question_text=question_text,
            answer_options=answer_options,
            time_limit=time_limit,
        )

    def get_server_result_stats(
        self, question: Question, question_num: int
    ) -> ServerResultsPayload:
        """
        Gets the results statistics for the previously played question and returns it structured in a data
        transfer object payload, for use by the server to display the results to the UI.

        The leaderboard is not provided if this is the final question.

        Arguments:
            question: The Question instance to get the data from about the previous question. A Question instance
                is used as it stores multiple data fields that are required for the payload, and is cleaner to
                pass directly rather than all the attributes separately.

            question_num: The question number of the previous question. This argument is required to be provided
                separately from the Question object as the question does not contain the question number in its
                data. An integer is used as the number is a whole number.

        Returns:
            The ServerResultsPayload instance to provide to the server to display the results to the UI.
        """
        total_questions = self.get_total_questions()

        accuracy = self.calculate_question_accuracy()
        answer_frequency = self.calculate_answer_frequency(len(question.answer_options))

        question_text = question.question_text
        answer_options = question.answer_options
        correct_answer = question.correct_answer_index

        # Do not give leaderboard if it is the final question, to create suspense before final results
        if self.get_total_questions() != question_num:
            leaderboard = self.leaderboard.get_global_leaderboard(include_delta=True)
        else:
            leaderboard = None

        return ServerResultsPayload(
            question_num=question_num,
            total_questions=total_questions,
            accuracy=accuracy,
            answer_frequency=answer_frequency,
            question_text=question_text,
            answer_options=answer_options,
            correct_answer=correct_answer,
            leaderboard=leaderboard,
        )

    def get_server_final_result_stats(self) -> ServerFinalResultsPayload:
        """
        Gets the final results statistics for the entire played quiz and returns it structured in a data transfer
        object payload, for use by the server to display the final results to the UI.

        Returns:
            The ServerFinalResultsPayload instance to provide to the server to display the final results to the UI.
        """
        winner = self.leaderboard.sorted_players[0].nickname
        highest_points = self.leaderboard.sorted_players[0].total_points

        fastest_answer = min(self.all_time_taken, default=None)
        average_accuracy = (
            sum(self.all_accuracies) / len(self.all_accuracies)
            if self.all_accuracies
            else 0.0
        )

        total_players = self.total_start_players
        total_questions = self.get_total_questions()

        leaderboard = self.leaderboard.get_global_leaderboard()

        return ServerFinalResultsPayload(
            winner=winner,
            highest_points=highest_points,
            fastest_answer=fastest_answer,
            average_accuracy=average_accuracy,
            total_players=total_players,
            total_questions=total_questions,
            leaderboard=leaderboard,
        )

    def get_client_result_stats(
        self, player_id: str, question: Question, question_num: int
    ) -> ClientResultsPayload:
        """
        Gets the results statistics for the previously played question and returns it structured in a data
        transfer object payload, for use by the client to display the results to the UI. This method gets
        the results data for one specific player, as provided in the player ID.

        The rank is not provided if this is the final question.

        Arguments:
            player_id: A string describing the ID of the Player instance to get the statistics for. A string
                is used as it can flexibly store IDs and can store many characters to make them more unique.

            question: The Question instance to get the data from about the previous question. A Question instance
                is used as it stores multiple data fields that are required for the payload, and is cleaner to
                pass directly rather than all the attributes separately.

            question_num: The question number of the previous question. This argument is required to be provided
                separately from the Question object as the question does not contain the question number in its
                data. An integer is used as the number is a whole number.

        Returns:
            The ClientResultsPayload instance to provide to the client to display the results to the UI.
        """
        player = self.players[player_id]
        nickname = player.nickname

        question_text = question.question_text
        answer_options = question.answer_options
        correct_answer = question.correct_answer_index

        selected_answer = player.selected_answer
        is_correct = player.is_correct

        time_taken = player.time_taken
        total_points = player.total_points
        gained_points = player.question_points

        # Do not give leaderboard if it is the final question, to create suspense before final results
        if self.get_total_questions() != question_num:
            rank = self.leaderboard.get_player_rank(player_id)
        else:
            rank = None

        return ClientResultsPayload(
            question_text=question_text,
            answer_options=answer_options,
            correct_answer=correct_answer,
            selected_answer=selected_answer,
            is_correct=is_correct,
            time_taken=time_taken,
            total_points=total_points,
            gained_points=gained_points,
            rank=rank,
            nickname=nickname,
        )

    def get_client_final_result_stats(
        self, player_id: str, completed_questions: int
    ) -> ClientFinalResultsPayload:
        """
        Gets the final results statistics for the entire played quiz and returns it structured in a data transfer
        object payload, for use by the client to display the final results to the UI. This method gets the final
        results data for one specific player, as provided in the player ID.

        Arguments:
            player_id: A string describing the ID of the Player instance to get the statistics for. A string
                is used as it can flexibly store IDs and can store many characters to make them more unique.

            completed_questions: The total number of questions that were fully completed in the game so far.
                An integer is used as the number of completed questions is a whole number.

        Returns:
            The ClientFinalResultsPayload instance to provide to the client to display the final results to the UI.
        """
        player = self.players[player_id]
        nickname = player.nickname

        rank = self.leaderboard.get_player_rank(player_id)
        total_points = player.total_points
        total_correct = player.total_correct
        total_questions = completed_questions
        accuracy = player.calculate_accuracy(completed_questions)

        on_podium = self.leaderboard.is_on_podium(player_id)
        is_first = self.leaderboard.is_first(player_id)
        is_last = self.leaderboard.is_last(player_id)
        behind_nickname, points_behind = self.leaderboard.get_points_behind(player_id)

        adjacent = self.leaderboard.get_adjacent_players(player_id, radius=1)
        leaderboard = self.leaderboard.get_leaderboard(adjacent)

        return ClientFinalResultsPayload(
            rank=rank,
            total_points=total_points,
            total_correct=total_correct,
            total_questions=total_questions,
            accuracy=accuracy,
            on_podium=on_podium,
            is_first=is_first,
            is_last=is_last,
            behind_nickname=behind_nickname,
            points_behind=points_behind,
            nickname=nickname,
            leaderboard=leaderboard,
        )

    def generate_clients_result_stats(
        self, question: Question, question_num: int
    ) -> dict[str, ClientResultsPayload]:
        """
        Generates result statistics for each player in the quiz game, categorizing them by player ID and
        automatically obtaining result statistics for each one in the form of a data transfer object.

        Arguments:
            question: The Question instance to get the data from about the previous question. A Question instance
                is used as it stores multiple data fields that are required for the payload, and is cleaner to
                pass directly rather than all the attributes separately.

            question_num: The question number of the previous question. This argument is required to be provided
                separately from the Question object as the question does not contain the question number in its
                data. An integer is used as the number is a whole number.

        Returns:
            A dictionary containing ClientResultsPayloads respective to the player they represent by the player
            ID key.
        """
        individual_stats = {}

        # Generate DTO for each player and save them identified by the player ID
        for player_id in self.players:
            stats = self.get_client_result_stats(player_id, question, question_num)
            individual_stats[player_id] = stats

        return individual_stats

    def generate_clients_final_result_stats(
        self, completed_questions: int
    ) -> dict[str, ClientFinalResultsPayload]:
        """
        Generates final result statistics for each player in the quiz game, categorizing them by player ID and
        automatically obtaining final result statistics for each one in the form of a data transfer object.

        Arguments:
            completed_questions: The total number of questions that were fully completed in the game so far.
                An integer is used as the number of completed questions is a whole number.

        Returns:
            A dictionary containing ClientFinalResultsPayload respective to the player they represent by the player
            ID key.
        """
        # Prevent completed questions exceeding total questions
        completed_questions = min(completed_questions, self.get_total_questions())

        individual_stats = {}

        # Generate DTO for each player and save them identified by the player ID
        for player_id in self.players:
            stats = self.get_client_final_result_stats(player_id, completed_questions)
            individual_stats[player_id] = stats

        return individual_stats

    def reset(self) -> None:
        """
        Resets the quiz manager attributes and any models used, such as the leaderboard, to their original
        initial values, to prepare for any future game and ensure no data from the current game remains in the
        next game.

        Returns:
            None.
        """
        self.quiz = None
        self.players.clear()
        self.leaderboard.clear()

        self.all_time_taken.clear()
        self.all_accuracies.clear()
