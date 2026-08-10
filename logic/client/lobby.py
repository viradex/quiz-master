"""
lobby.py

The logic respective to the client lobby screen.
"""

from core.app.screen_ids import Screen
from core.services.app_context import Services
from core.services.game_client import GameClient
from logic.base_logic import BaseLogic
from ui.screens.client.lobby import ClientLobbyScreen


class ClientLobbyLogic(BaseLogic):
    """
    Creates the lobby logic class, inheriting BaseLogic. This logic is part of the 'client' category.

    This logic class is responsible for adding/removing players from the UI player list, and disconnecting
    the client if and when they wish to leave the server.

    Arguments:
        screen: The screen respective to this logic class, to allow listening to signals from it and invoking
            methods to modify the UI.

        services: All the application Services, to allow access to various functions of the application
            in one single wrapper class.
    """

    def __init__(self, screen: ClientLobbyScreen, services: Services) -> None:
        super().__init__()
        self.screen: ClientLobbyScreen = screen
        self.game_client: GameClient = services.client

        # Screen PyQt signal connections
        self.screen.left_server.connect(self._on_left_server)

        # Client PyQt signal connections
        self.game_client.connected.connect(self._on_connected)
        self.game_client.player_joined.connect(self._on_player_joined)
        self.game_client.player_left.connect(self._on_player_left)
        self.game_client.rtt_updated.connect(self._on_rtt_updated)

    def _on_left_server(self) -> None:
        """
        Internal method. Intended to be called when the user wishes to leave the server.

        Disconnects the user from the server and displays the main menu screen.

        Returns:
            None.
        """
        self.game_client.disconnect_client()
        self.screen.go_to(Screen.COMMON_MENU)

        self.screen.reset_status()
        self.screen.set_status("Disconnected from server", 2000)

    def _on_connected(self, player_list: list[str]) -> None:
        """
        Internal method. Intended to be called when connection to the server was successful.

        Displays the player list to the UI, while ensuring the user's own nickname is added to the player list
        first.

        Arguments:
            player_list: The nicknames of all the players currently connected to the server at the time of
                joining, including the user's own nickname, as a list of strings. A list is used to group the
                similar values together and allow easier iteration.

        Returns:
            None.
        """
        own_nickname = self.game_client.nickname

        # Inserts the own nickname as the first element in the player list
        if own_nickname in player_list:
            player_list.remove(own_nickname)
            player_list.insert(0, own_nickname)

        # Refreshes and adds all players to the lobby screen
        self.screen.clear_lobby()

        for player in player_list:
            is_self = player == own_nickname
            self.screen.add_player_lobby(player, is_self)

    def _on_player_joined(self, nickname: str) -> None:
        """
        Internal method. Intended to be called when a player joins the server.

        Adds the player name to the lobby UI, unless the nickname matches the user's own nickname.

        Arguments:
            nickname: The nickname of the player that joined. A string is used as a nickname is easily
                represented by a string.

        Returns:
            None.
        """
        if nickname != self.game_client.nickname:
            self.screen.add_player_lobby(nickname, is_self=False)

    def _on_player_left(self, nickname: str) -> None:
        """
        Internal method. Intended to be called when a player leaves the server.

        Removes the player name from the lobby UI.

        Arguments:
            nickname: The nickname of the player that left. A string is used as a nickname is easily
                represented by a string.

        Returns:
            None.
        """
        self.screen.remove_player_lobby(nickname)

    def _on_rtt_updated(self, rtt: float | None) -> None:
        """
        Internal method. Intended to be called when the round-trip time for communication between the client
        and server has been calculated.

        Updates the round-trip time on the lobby screen.

        Arguments:
            rtt: The time taken to communicate to the server and back in milliseconds, with decimal precision,
                or None if no time has been calculated yet. A float is used for decimal precision.

        Returns:
            None.
        """
        self.screen.update_rtt(rtt)
