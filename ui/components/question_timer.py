import math
from PyQt6.QtWidgets import QLabel, QWidget, QProgressBar, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

from ui.utils.color import darken_color

FPS = 60
INTERVAL = 1000 // FPS


class QuestionTimer(QWidget):
    timeup = pyqtSignal()
    timeout = pyqtSignal(int)

    def __init__(self, total_ms, parent=None):
        super().__init__(parent)

        if total_ms <= 0:
            raise ValueError(
                f"total_ms must be a number greater than zero (received {total_ms})"
            )

        self.reset(total_ms)

        self._setup_component()
        self._setup_timer()

    def _setup_component(self):
        self.timer_bar = QProgressBar()
        self.timer_bar.setOrientation(Qt.Orientation.Vertical)
        self.timer_bar.setTextVisible(False)
        self.timer_bar.setRange(0, 10000)
        self.timer_bar.setFixedWidth(40)

        self.timer_count = QLabel()
        self.timer_count.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_count.setFixedWidth(40)
        self.timer_count.setStyleSheet("""
            QLabel {
                color: white;
                background-color: #2a2a2a;
                border-radius: 10px;
                padding: 3px;
                font-weight: bold;
                font-size: 14px;
            }
""")

        vbox = QVBoxLayout()
        vbox.addWidget(self.timer_bar, 1, alignment=Qt.AlignmentFlag.AlignHCenter)
        vbox.addSpacing(2)
        vbox.addWidget(self.timer_count, 0, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.setLayout(vbox)

    def _setup_timer(self):
        self.timer = QTimer(self)
        self.timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.timer.timeout.connect(self._on_elapsed)

    def _style_progress_bar(self, bg):
        return f"""
            QProgressBar {{
                background-color: #1e1e1e;
                border: 2px solid #333;
                border-radius: 8px;
                padding: 3px;
            }}

            QProgressBar::chunk {{
                background-color: {bg};
                border-radius: 4px;
            }}
        """

    def _update_ui(self):
        remaining = max(0, self.total_ms - self.elapsed_ms)
        percent = (remaining / self.total_ms) * 100
        self.timer_bar.setValue(int(percent * 100))

        seconds = math.ceil((self.total_ms - self.elapsed_ms) / 1000)
        self.timer_count.setText(str(seconds))

        if not self.locked:
            if percent >= 60:
                color = "#22c55e"
            elif percent >= 30:
                color = "#f59e0b"
            else:
                color = "#eb3434"

            if color != self.current_color:
                self.current_color = color
                self.timer_bar.setStyleSheet(self._style_progress_bar(color))

    def _on_elapsed(self):
        self.elapsed_ms += INTERVAL
        self.timeout.emit(self.elapsed_ms)

        if self.elapsed_ms >= self.total_ms:
            self.elapsed_ms = self.total_ms
            self.timer.stop()
            self.timeup.emit()

        self._update_ui()

    def reset(self, total_ms):
        self.total_ms = total_ms
        self.elapsed_ms = 0
        self.locked = False
        self.current_color = None

    def lock(self):
        self.locked = True

        dim = darken_color("#22c55e", 0.8)
        self.timer_bar.setStyleSheet(self._style_progress_bar(dim))

    def on_enter(self):
        self.elapsed_ms = 0
        self.locked = False
        self.current_color = None

        self._update_ui()
        self.timer.start(INTERVAL)

    def on_leave(self):
        self.timer.stop()
