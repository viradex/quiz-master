"""
multi_results.py

The logic respective to the server multi-question results screen.
"""

from core.app.screen_ids import Screen
from core.game.game_controller import GameController
from core.services.app_context import Services
from core.services.game_server import GameServer
from logic.base_logic import BaseLogic
from models.payloads import ClientFinalResultsPayload, ServerFinalResultsPayload
from ui.screens.server.multi_result import ServerMultiResultScreen
from utils.formatting import format_ping


class ServerMultiResultLogic(BaseLogic):
    """
    Creates the multi-question results logic class, inheriting BaseLogic. This logic is part of the 'server'
    category.

    This logic class is responsible for displaying final results when they arrive, as well as disconnecting
    the client if and when they wish to leave the server.

    Arguments:
        screen: The screen respective to this logic class, to allow listening to signals from it and invoking
            methods to modify the UI.

        services: All the application Services, to allow access to various functions of the application
            in one single wrapper class.
    """

    def __init__(self, screen: ServerMultiResultScreen, services: Services) -> None:
        super().__init__()
        self.screen: ServerMultiResultScreen = screen
        self.server: GameServer = services.server
        self.controller: GameController = services.controller

        # Screen PyQt signal connections
        self.screen.next_question_requested.connect(self._on_next_question_requested)
        self.screen.end_game_requested.connect(self._on_end_game_requested)
        self.screen.player_info_requested.connect(self._on_player_info_requested)
        self.screen.player_kicked.connect(self._on_player_kicked)

        # Server PyQt signal connections
        self.server.player_left.connect(self._on_player_left)

        # Game controller PyQt signal connections
        self.controller.final_results_ready.connect(self._on_final_results_ready)

    def _on_next_question_requested(self) -> None:
        """
        Internal method. Intended to be called when the user wishes to start the next question.

        Requests the controller to begin the following question, or end the quiz if there are no further
        questions.

        Returns:
            None.
        """
        self.controller.start_next_question()

    def _on_end_game_requested(self) -> None:
        """
        Internal method. Intended to be called when the user wishes to end the quiz game prematurely.

        Requests the controller to finish the quiz game.

        Returns:
            None.
        """
        self.controller.finish_quiz()

    def _on_player_info_requested(self, player_id: str) -> None:
        """
        Internal method. Intended to be called when the host requests detailed player information on a specific
        player.

        Retrieves and displays all available player information in an information modal box.

        Arguments:
            player_id: A string describing the ID of the player to get information about. A string is used as
                it can flexibly store IDs and can store many characters to make them more unique.

        Returns:
            None.
        """
        nickname = self.server.get_player(player_id).nickname
        address = self.server.get_client_address(player_id)

        # In normal operation, the address should never be None
        if address is not None:
            ip, port = address
        else:
            ip = "N/A"
            port = "N/A"

        # The hostname can be unavailable if the reverse DNS lookup takes too long or fails
        hostname = self.server.get_client_hostname(player_id) or "N/A"

        # The RTT could still be calculating, therefore show 'Unknown' if that is the case
        rtt = self.server.get_client_rtt(player_id)
        rtt_text = format_ping(rtt) if rtt is not None else "Unknown"

        self.screen.show_info(
            "Player Info",
            f"Nickname: {nickname}\nPing: {rtt_text}\n\nIP address: {ip}\nPort: {port}\nHostname: {hostname}",
        )

    def _on_player_kicked(self, player_id: str) -> None:
        """
        Internal method. Intended to be called when the host wishes to kick a player.

        Kicks the player from the server. There is no confirmation prompt shown here.

        Arguments:
            player_id: A string describing the ID of the player to kick. A string is used as it can flexibly
                store IDs and can store many characters to make them more unique.

        Returns:
            None.
        """
        self.server.kick_player(player_id, "Kicked by host")
        self.screen.set_status("Kicked player", 2000)

    def _on_player_left(self, player_id: str, nickname: str) -> None:
        """
        Internal method. Intended to be called when a player leaves the server.

        Removes the player name from the leaderboard UI, along with the hidden player ID.

        Arguments:
            player_id: The player ID of the player that left. A string is used as it can flexibly store
                IDs and can store many characters to make them more unique.

            nickname: The nickname of the player that left. This value is unused by the method, however, is
                required to exist as the signal that calls this forces the nickname argument.

        Returns:
            None.
        """
        self.screen.remove_player(player_id)

    def _on_final_results_ready(
        self,
        server_data: ServerFinalResultsPayload,
        clients_data: dict[str, ClientFinalResultsPayload],
    ) -> None:
        """
        Internal method. Intended to be called when the quiz has concluded and the final results data is ready.

        The question results screen is displayed with the data provided as a ServerFinalResultsPayload, while the
        clients have their ClientFinalResultsPayload turned into a dictionary to allow for seamless transfer
        across the network.

        Arguments:
            server_data: The information needed to display final results information for the server-side UI. A
                ServerFinalResultsPayload is used as it contains all the information needed in a type-safe manner.

            clients_data: A dictionary containing all the information needed for clients to display their own
                personalized final results information. Each value, being a ClientFinalResultsPayload, is paired
                with the client ID to ensure each payload is delivered to the correct player. A dictionary is
                used to store multiple player data payloads at once.

        Returns:
            None.
        """
        self.screen.reset_status()
        self.screen.go_to(Screen.SERVER_FINAL_RESULT, server_data)

        # Provide each client with its own specialized payload, converted to a
        # dictionary for easier transfer across the network.
        for player_id, data in clients_data.items():
            self.server.send_final_results(player_id, data.to_dict())

        # Disconnect clients, since no more data is needed to be transferred now.
        # The clients should've disconnected themselves at this point, so this
        # should happen silently, and they shouldn't get the disconnection screen.
        self.server.stop("Game over")
