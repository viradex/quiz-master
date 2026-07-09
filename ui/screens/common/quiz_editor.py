from ui.screens.base_screen import BaseScreen


class CommonQuizEditorScreen(BaseScreen):
    title_text = "Quiz Master – Quiz Editor (Quiz Name)"

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setup_ui()

    def setup_ui(self) -> None:
        pass
