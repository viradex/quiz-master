from ui.screens.base_screen import BaseScreen


class CommonLoadingScreen(BaseScreen):
    title_text = "Quiz Master – Loading..."

    def __init__(self, parent=None):
        super().__init__(parent)
