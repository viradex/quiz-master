from ui.screens.common.menu import CommonMenuScreen
from logic.base_logic import BaseLogic
from core.services.services import GameServer
from core.app.screen_ids import Screens


class CommonMenuLogic(BaseLogic):
    def __init__(self, screen, services):
        super().__init__()
        self.screen: CommonMenuScreen = screen
        self.game_server: GameServer = services.server

        self.screen.start_server.connect(self.handle_start)

        self.game_server.starting.connect(self.on_starting)
        self.game_server.start_success.connect(self.on_start_success)
        self.game_server.start_fail.connect(self.on_start_fail)

    def handle_start(self):
        self.game_server.start()

    def on_starting(self):
        # TODO should the loading screen be shown?
        # self.screen.go_to(
        #     Screens.COMMON_LOADING,
        #     {"loading_msg": "Starting...", "status_msg": "Starting the server..."},
        # )

        pass

    def on_start_success(self):
        self.screen.go_to(Screens.SERVER_LOBBY)

    def on_start_fail(self, reason):
        # self.screen.go_to(Screens.COMMON_MENU)
        self.screen.show_starting_error(reason)
