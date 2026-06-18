from PyQt6.QtCore import QObject, pyqtSignal


class QuizManager(QObject):
    def __init__(self):
        super().__init__()
