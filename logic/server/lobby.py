from ui.screens.server.lobby import ServerLobbyScreen
from logic.base_logic import BaseLogic
from core.services.game_server import GameServer
from core.app.screen_ids import Screens
from core.game.game_controller import GameController
from data.quiz_repo import QuizRepository

from utils.networking import get_hostname
from core.config.constants import MIN_PLAYERS_FOR_START


class ServerLobbyLogic(BaseLogic):
    def __init__(self, screen, services) -> None:
        super().__init__()
        self.screen: ServerLobbyScreen = screen

        self.server: GameServer = services.server
        self.controller: GameController = services.controller
        self.quiz_repo: QuizRepository = services.quiz_repo

        self.server.player_joined.connect(self.on_player_joined)
        self.server.player_left.connect(self.on_player_left)

        self.screen.get_player_info.connect(self.on_get_player_info)
        self.screen.kick_player.connect(self.on_kick_player)
        self.screen.start_game.connect(self.on_start_game)
        self.screen.close_server.connect(self.on_close_server)

    def on_player_joined(self, nickname: str) -> None:
        self.screen.add_player_lobby(nickname)
        self.screen.set_status(f"{nickname} joined the game", 5000)

    def on_player_left(self, nickname: str) -> None:
        self.screen.remove_player_lobby(nickname)
        self.screen.set_status(f"{nickname} left the game", 5000)

    def on_get_player_info(self, nickname: str) -> None:
        player_id = self.server.registry.get_id_by_nickname(nickname)

        ip, port = self.server.get_player_address(player_id)
        hostname = get_hostname(ip)

        self.screen.show_player_info(nickname, ip, port, hostname)

    def on_kick_player(self, nickname: str) -> None:
        player_id = self.server.registry.get_id_by_nickname(nickname)
        self.server.kick_player(player_id, "Kicked by host")

        self.screen.set_status("Kicked player", 2000)

    def on_start_game(self, quiz_name: str) -> None:
        players = len(self.server.registry.get_all())

        self.quiz_repo.refresh_cache()
        quizzes = self.quiz_repo.load_quizzes()
        names = {q.quiz_title for q in quizzes.values()}

        if quiz_name not in names:
            self.screen.show_error(
                "Invalid Conditions for Start", "The quiz selected does not exist."
            )
            return
        elif players < MIN_PLAYERS_FOR_START:
            self.screen.show_error(
                "Invalid Conditions for Start",
                "There are not enough players to start the game.",
            )
            return

        for quiz in quizzes.values():
            if quiz_name == quiz.quiz_title:
                quiz_id = quiz.quiz_id
                break

        quiz = self.quiz_repo.load_quiz(quiz_id)
        self.controller.load_quiz(quiz)

        self.controller.start_game()

    def on_close_server(self) -> None:
        self.server.stop()
        self.screen.go_to(Screens.COMMON_MENU)

        self.screen.reset_status()
        self.screen.set_status("Stopped server", 2000)

    def on_enter(self):
        quizzes = self.quiz_repo.load_quizzes()
        names = [q.quiz_title for q in quizzes.values()]

        self.screen.set_quizzes(names)
