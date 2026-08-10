"""
question_timer.py

The question timer UI component, for displaying the remaining amount of time for a question.
"""

import math

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import QLabel, QProgressBar, QVBoxLayout, QWidget

from utils.color import darken_color

# FPS of the progress bar
FPS = 60

# Interval of progress bar updates in milliseconds
INTERVAL = 1000 // FPS


class QuestionTimer(QWidget):
    """
    Creates a question countdown timer widget, to display the remaining time for a question. The progress
    bar is a vertical progress bar with the timer text below it. The color changes depending on the
    percentage of time remaining. Inherits `QWidget`.

    Attributes:
        timer_ended: A `pyqtSignal` that emits when the question timer ends. No arguments are provided.

    Arguments:
        total_ms: The total milliseconds that the timer should last for, or None to set no time. The value
            must be a valid positive integer. An integer is used as milliseconds are precise enough for timers
            without needing extra precision. Defaults to None.

        parent: The parent to make this widget a child of, or None to set no parent. Defaults to None.

    Raises:
        ValueError: If the `total_ms` provided is a negative integer.
    """

    timer_ended = pyqtSignal()

    def __init__(
        self, total_ms: int | None = None, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)

        # Automatically deals with negative integer error handling
        # Sets it in self.total_ms
        self.set_duration(total_ms)

        self.elapsed_ms: int = 0
        self.locked: bool = False
        self.current_color: bool = None

        self._setup_timer()
        self._setup_component()

    def _setup_timer(self) -> None:
        """
        Internal method. Sets up the `QTimer` needed to decrease the progress bar and decrease the timer. This
        method should only be run once, preferably in the initialization logic.

        Returns:
            None.
        """
        self.timer = QTimer(self)
        self.timer.setInterval(INTERVAL)
        self.timer.timeout.connect(self._on_elapsed)

        # Makes timer more precise to avoid jittering, though this uses more CPU
        self.timer.setTimerType(Qt.TimerType.PreciseTimer)

    def _setup_component(self) -> None:
        """
        Internal method. Sets up the component UI, such as widgets and layouts. This method should only be
        called once, preferably in the initialization logic.

        Returns:
            None.
        """
        # Using a range of 0-10000 rather than 0-100 allows for smoother visual
        # movement. Initialize progress bar value at full, since we are counting
        # down, not up.
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

        # Makes progress bar take rest of space that capsule doesn't take
        vbox = QVBoxLayout()
        vbox.addWidget(
            self.timer_bar, stretch=1, alignment=Qt.AlignmentFlag.AlignHCenter
        )
        vbox.addSpacing(2)
        vbox.addWidget(
            self.timer_count, stretch=0, alignment=Qt.AlignmentFlag.AlignHCenter
        )

        self.setLayout(vbox)

    def set_duration(self, total_ms: int | None) -> None:
        """
        Configures the duration of the question timer in milliseconds. This does not start the timer, however.
        To start the timer, run `start()` after setting the time.

        Arguments:
            total_ms: The total milliseconds that the timer should last for, or None to set no time. The value
                must be a valid positive integer. An integer is used as milliseconds are precise enough for timers
                without needing extra precision.

        Returns:
            None.

        Raises:
            ValueError: If the `total_ms` provided is a negative integer.
        """
        # If time is not a positive integer, reject
        if total_ms is not None and total_ms < 0:
            raise ValueError(
                f"total_ms must be a number greater than zero (received {total_ms})"
            )

        self.total_ms = total_ms

    def start(self) -> None:
        """
        Start the question timer internally and on the UI, resetting all values except the total duration.
        The `total_ms` is required to be set before running this; to do so, run `set_duration()` beforehand.

        Returns:
            None.

        Raises:
            RuntimeError: If the `total_ms` property has not been set.
        """
        if self.total_ms is None:
            raise RuntimeError("No time has been set; the timer cannot be started")

        self._reset()

        # Update UI to reflect current reset values and start timer
        self._update_ui()
        self.timer.start()

    def stop(self) -> None:
        """
        Stop the question timer in place, freezing the timer from when it was stopped. This method should be
        run when the timer is no longer visible to reduce CPU usage.

        Returns:
            None.
        """
        self.timer.stop()

    def lock(self) -> None:
        """
        Locks the question timer. This does not stop the timer in place or pause the timer, but ensures the color
        of the timer does not change depending on the time remaining, staying at a static color of darker green.
        Should be run when the user has answered, for example.

        Returns:
            None.
        """
        self.locked = True

        # Darken color here as _update_ui() will not do it when locked
        dim = darken_color("#22c55e", factor=0.2)
        self.timer_bar.setStyleSheet(self._style_progress_bar(dim))

    def _reset(self) -> None:
        """
        Reset all properties of the question timer, except the total duration.

        Returns:
            None.
        """
        self.elapsed_ms = 0
        self.locked = False
        self.current_color = None

    def _style_progress_bar(self, bg: str) -> str:
        """
        Internal method. Give a QSS stylesheet string containing styling data for the question timer progress
        bar, depending on the background provided.

        Arguments:
            bg: The filled-in section background of the progress bar, as a hex code. A string is used as it
                represents hex codes well.

        Returns:
            The QSS as a string. A string is used as it can represent the QSS well and also works well with
            f-strings.
        """
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
        """
        Internal method. Updates the UI when the timer decreases in elapsed time. Decreases the progress bar,
        and, if needed, the visual seconds counter. The seconds counter is a whole integer display, so it never
        displays fractions of a second (e.g. 2.7).

        Returns:
            None.
        """
        # Calculate remaining milliseconds, ensuring it never dips below 0ms
        remaining = max(0, self.total_ms - self.elapsed_ms)
        percent = (remaining / self.total_ms) * 100

        # Set progress bar, and adapts the percentage to the 0-10000 range
        # that the progress bar is set to.
        self.timer_bar.setValue(int(percent * 100))

        # Calculate remaining seconds, then ceil it. For example, if
        # there are 1.5 seconds remaining, the text displays 2, preventing
        # a lower value from being seen too soon. Displays the number of seconds.
        seconds = math.ceil((self.total_ms - self.elapsed_ms) / 1000)
        self.timer_count.setText(str(seconds))

        # If the timer is locked, the color is fixed
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
        """
        Internal method. Intended to be called when the countdown `QTimer` times out. Increases the elapsed time,
        and, if the elapsed time has surpassed the total time, ends the timer and emits a signal. Otherwise,
        updates the UI.

        Returns:
            None.
        """
        self.elapsed_ms += INTERVAL

        # If timer has completed, stop timer and emit signal
        if self.elapsed_ms >= self.total_ms:
            self.elapsed_ms = self.total_ms
            self.stop()

            self.timer_ended.emit()

        # Update UI if timer is still going
        self._update_ui()
