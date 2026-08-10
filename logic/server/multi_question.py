"""
multi_question.py

The logic respective to the server multi-question screen.
"""

from core.app.enums import AnswerValidationResult
from core.app.screen_ids import Screen
from core.game.game_controller import GameController
from core.services.app_context import Services
from core.services.game_server import GameServer
from logic.base_logic import BaseLogic
from models.payloads import ClientResultsPayload, ServerResultsPayload
from ui.screens.server.multi_question import ServerMultiQuestionScreen


class ServerMultiQuestionLogic(BaseLogic):
    """
    Creates the multi-question logic class, inheriting BaseLogic. This logic is part of the 'server' category.

    This logic class is responsible for validating and recording submitted answers from clients during the
    duration of a question.

    Arguments:
        screen: The screen respective to this logic class, to allow listening to signals from it and invoking
            methods to modify the UI.

        services: All the application Services, to allow access to various functions of the application
            in one single wrapper class.
    """

    def __init__(self, screen: ServerMultiQuestionScreen, services: Services) -> None:
        super().__init__()
        self.screen: ServerMultiQuestionScreen = screen
        self.server: GameServer = services.server
        self.controller: GameController = services.controller

        # Screen PyQt signal connections
        self.screen.question_skipped.connect(self._on_question_skipped)

        # Server PyQt signal connections
        self.server.answer_submitted.connect(self._on_answer_submitted)

        # Game controller PyQt signal connections
        self.controller.question_results_ready.connect(self._on_question_results_ready)

    def _on_question_skipped(self) -> None:
        """
        Internal method. Intended to be called when the user wishes to skip the current question.

        Requests the game controller to skip the current question and end it prematurely.

        Returns:
            None.
        """
        self.screen.set_status("Skipped question", 2000)
        self.controller.skip_question()

    def _on_answer_submitted(
        self, player_id: str, selected_index: int, received_time: float
    ) -> None:
        """
        Internal method. Intended to be called when the server reports a player submitted a response for the
        answer.

        Validates the answer submitted by the player to ensure it is valid before adding it as a valid submission
        to the game controller. If the answer is not valid, the client is send an invalid action warning. However,
        they are not disconnected from the server for this.

        Arguments:
            player_id: The player ID of the player that sent the answer. A string is used as it can flexibly
                store IDs and can store many characters to make them more unique.

            selected_index: The index of the answer selected, as a zero-based index respective to the answer the
                player selected, ranging from 0 to the number of valid answers, minus 1. For example, for a
                question with 4 answers, the valid range is 0-3. An integer is used as an index is represented
                well by an integer.

            received_time: A float derived from `time.monotonic()` at the time the answer was submitted. A
                monotonic time is used to avoid the time being changed by DST or NTP and causing issues.

        Returns:
            None.
        """
        # Check with the controller itself to see if the answer is valid
        reason = self.controller.is_answer_legal(selected_index, received_time)

        # If answer submission is invalid, sends details back to client about why it was invalid
        if reason is AnswerValidationResult.TIME:
            self.server.send_invalid_action(
                player_id, "Answer submitted at invalid time"
            )
            return
        elif reason is AnswerValidationResult.ANSWER:
            self.server.send_invalid_action(player_id, "Invalid answer submitted")
            return

        # If answer is valid, adds it to the submission counter and lets the controller read it
        self.screen.add_submission()
        self.controller.receive_answer(player_id, selected_index, received_time)

        # Display nickname in status bar
        nickname = self.server.get_player(player_id).nickname
        self.screen.set_status(f"{nickname} submitted an answer", 2000)

    def _on_question_results_ready(
        self,
        server_data: ServerResultsPayload,
        clients_data: dict[str, ClientResultsPayload],
    ) -> None:
        """
        Internal method. Intended to be called when the question has ended and the question results data is ready.

        The question results screen is displayed with the data provided as a ServerResultsPayload, while the clients
        have their ClientResultsPayload turned into a dictionary to allow for seamless transfer across the network.

        Arguments:
            server_data: The information needed to display results information for the server-side UI. A
                ServerResultsPayload is used as it contains all the information needed in a type-safe manner.

            clients_data: A dictionary containing all the information needed for clients to display their own
                personalized results information. Each value, being a ClientResultsPayload, is paired with the
                client ID to ensure each payload is delivered to the correct player. A dictionary is used to
                store multiple player data payloads at once.

        Returns:
            None.
        """
        self.screen.set_status("Showing results")
        self.screen.go_to(Screen.SERVER_MULTI_RESULT, server_data)

        # Provide each client with its own specialized payload, converted to a
        # dictionary for easier transfer across the network.
        for player_id, data in clients_data.items():
            self.server.send_question_results(player_id, data.to_dict())
