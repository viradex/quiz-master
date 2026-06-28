import math
from PyQt6.QtWidgets import QLabel, QWidget, QProgressBar, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

from utils.color import darken_color

FPS = 60
INTERVAL = 1000 // FPS


class QuestionTimer(QWidget):
    """Custom question countdown timer widget, for questions."""

    timeup = pyqtSignal()
    timeout = pyqtSignal(int)

    def __init__(self, total_ms: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        if total_ms < 0:
            raise ValueError(
                f"total_ms must be a number greater than zero (received {total_ms})"
            )

        # Initialize properties
        self.reset(total_ms)

        self.setup_component()
        self.setup_timer()

    def setup_component(self) -> None:
        # Vertical timer progress bar
        self.timer_bar = QProgressBar()
        self.timer_bar.setOrientation(Qt.Orientation.Vertical)
        self.timer_bar.setTextVisible(False)
        self.timer_bar.setRange(0, 10000)
        self.timer_bar.setFixedWidth(40)

        # Small timer numeric counter in capsule
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

    def setup_timer(self) -> None:
        self.timer = QTimer(self)
        self.timer.setTimerType(Qt.TimerType.PreciseTimer)  # To reduce jittering
        self.timer.timeout.connect(self._on_elapsed)

    def _style_progress_bar(self, bg: str) -> str:
        """Returns a QSS stylesheet for styling the progress bar."""
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

    def _update_ui(self) -> None:
        """Updates the UI when the timer times out."""
        # Gets remaining time, converting it to percentage
        remaining = max(0, self.total_ms - self.elapsed_ms)
        percent = (remaining / self.total_ms) * 100
        self.timer_bar.setValue(int(percent * 100))

        # Seconds display
        seconds = math.ceil((self.total_ms - self.elapsed_ms) / 1000)
        self.timer_count.setText(str(seconds))

        if not self.locked:
            # >60%    - green
            # 30%-60% - yellow
            # <30%    - red
            if percent >= 60:
                color = "#22c55e"
            elif percent >= 30:
                color = "#f59e0b"
            else:
                color = "#eb3434"

            # Only updates stylesheet if color actually changed, to reduce lag
            if color != self.current_color:
                self.current_color = color
                self.timer_bar.setStyleSheet(self._style_progress_bar(color))

    def _on_elapsed(self) -> None:
        """Updates timer UI when timer elapses."""
        self.elapsed_ms += INTERVAL
        self.timeout.emit(self.elapsed_ms)

        # If timer has completed
        if self.elapsed_ms >= self.total_ms:
            self.elapsed_ms = self.total_ms
            self.timer.stop()
            self.timeup.emit()

        self._update_ui()

    def reset(self, total_ms: int) -> None:
        """Reset all properties of the component."""
        self.total_ms = total_ms
        self.elapsed_ms = 0
        self.locked = False
        self.current_color = None

    def lock(self) -> None:
        """Lock the widget timer. This does not freeze the timer,
        but freezes the color to always show a darker green color."""
        self.locked = True

        dim = darken_color("#22c55e", 0.8)
        self.timer_bar.setStyleSheet(self._style_progress_bar(dim))

    def on_enter(self) -> None:
        self.elapsed_ms = 0
        self.locked = False
        self.current_color = None

        self._update_ui()
        self.timer.start(INTERVAL)

    def on_leave(self) -> None:
        self.timer.stop()
