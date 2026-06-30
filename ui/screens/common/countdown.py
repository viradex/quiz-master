import math
from PyQt6.QtWidgets import QLabel, QProgressBar, QVBoxLayout
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QTimer

from ui.screens.base_screen import BaseScreen

FPS = 60
INTERVAL = 1000 // FPS


class CommonCountdownScreen(BaseScreen):
    title_text = "Quiz Master – Starting..."

    def __init__(self, parent=None):
        super().__init__(parent)

        self.total_ms = None
        self.elapsed_ms = 0

        self.timer = QTimer()
        self.timer.setInterval(INTERVAL)
        self.timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.timer.timeout.connect(self.on_timeout)

        self.setup_ui()

    def setup_ui(self):
        loading_font = QFont()
        loading_font.setPointSize(72)

        self.countdown_lbl = QLabel()
        self.countdown_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.countdown_lbl.setFont(loading_font)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 10000)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedWidth(200)
        self.progress_bar.setValue(10000)

        vbox = QVBoxLayout()
        vbox.addStretch()
        vbox.addWidget(self.countdown_lbl)
        vbox.addSpacing(10)
        vbox.addWidget(self.progress_bar, alignment=Qt.AlignmentFlag.AlignCenter)
        vbox.addStretch()

        self.setLayout(vbox)

    def on_timeout(self):
        self.elapsed_ms += INTERVAL

        remaining = max(0, self.total_ms - self.elapsed_ms)
        percent = (remaining / self.total_ms) * 100
        self.progress_bar.setValue(int(percent * 100))

        seconds = math.ceil((self.total_ms - self.elapsed_ms) / 1000)
        self.countdown_lbl.setText(str(max(1, seconds)))

        if remaining <= 0:
            self.timer.stop()

    def on_enter(self, payload: dict | None = None):
        duration = payload["duration"]

        self.total_ms = int(duration * 1000)
        self.elapsed_ms = 0

        self.countdown_lbl.setText(str(self.total_ms // 1000))
        self.progress_bar.setValue(10000)

        self.timer.start()

    def on_leave(self):
        self.timer.stop()
