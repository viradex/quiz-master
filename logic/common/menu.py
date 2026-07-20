from core.app.enums import ServerStartingError
from core.app.screen_ids import Screens
from core.services.game_server import GameServer
from data.quiz_repo import QuizRepository
from logic.base_logic import BaseLogic
from ui.screens.common.menu import CommonMenuScreen


class CommonMenuLogic(BaseLogic):
    def __init__(self, screen, services) -> None:
        super().__init__()
        self.screen: CommonMenuScreen = screen
        self.game_server: GameServer = services.server
        self.quiz_repo: QuizRepository = services.quiz_repo

        # Screen
        self.screen.started_server.connect(self.on_started_server)

        # Server
        self.game_server.started.connect(self.on_started)
        self.game_server.start_failed.connect(self.on_start_failed)

    def on_started_server(self) -> None:
        """When the server is requested to be started."""
        # Get all available quizzes to see if any can be played
        quizzes = self.quiz_repo.get_all()

        # No quizzes are in the directory
        if not quizzes:
            self.screen.show_error(
                "No Quizzes Available",
                "There are no quizzes available. You need at least one quiz before you can host a game. Create a quiz using the quiz manager, then try again.",
            )
            return

        # No quizzes are complete
        if not any(quiz.is_complete for quiz in quizzes.values()):
            self.screen.show_error(
                "No Complete Quizzes Available",
                "There are no quizzes available that are ready to play. Finish a quiz using the quiz editor, then try again.",
            )
            return

        self.game_server.start()
        self.screen.set_status("Starting...")

    def on_started(self) -> None:
        """When the server has successfully started."""
        self.screen.go_to(Screens.SERVER_LOBBY)
        self.screen.set_status("In lobby")

    def on_start_failed(self, reason: ServerStartingError) -> None:
        """When the server failed to start. Shows an error modal window displaying the reason."""
        self.screen.reset_status()
        self.screen.set_status("Failed to start server", 5000)

        if reason == ServerStartingError.IN_USE:
            self.screen.show_error(
                "Failed to Start",
                "Unable to start the server. Another instance of the server is already running on this device, or the port is in use. Please try again.",
            )
        if reason == ServerStartingError.PERMISSION:
            self.screen.show_error(
                "Failed to Start",
                "Unable to start the server. Permission denied. Please try again.",
            )
        if reason == ServerStartingError.INVALID_IP:
            self.screen.show_error(
                "Failed to Start",
                "Unable to start the server. The server was attempted to be started on an IP that does not belong to the device. Please try again.",
            )
        if reason == ServerStartingError.INVALID:
            self.screen.show_error(
                "Failed to Start",
                "Unable to start the server. Invalid argument(s). Please try again.",
            )
        if reason == ServerStartingError.UNKNOWN:
            self.screen.show_error(
                "Failed to Start",
                "Unable to start the server. An unknown error occurred. Please try again.",
            )
