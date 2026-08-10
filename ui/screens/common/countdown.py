"""
countdown.py

The countdown UI screen. Contains a simple countdown timer and progress bar in the center of the
screen.
"""

import math

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QProgressBar, QVBoxLayout, QWidget

from ui.screens.base_screen import BaseScreen

# FPS of the progress bar
FPS = 60

# Interval of progress bar updates in milliseconds
INTERVAL = 1000 // FPS


class CommonCountdownScreen(BaseScreen):
    """
    Creates the countdown screen, inheriting BaseScreen. This screen is part of the 'common' category.

    This screen is responsible for showing a countdown timer and text, typically for before a new
    question begins.

    Attributes:
        title_text: The default text of the screen when entered. A string is used as that is what the
            title changing code requires.

    Arguments:
        parent: The parent of this screen, or None. Typically, this is the MainWindow.
    """

    title_text = "Quiz Master – Starting..."

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.total_ms: int | None = None
        self.elapsed_ms = 0

        self._setup_timer()
        self._setup_ui()

    def _setup_timer(self) -> None:
        """
        Internal method. Sets up the countdown timer using `QTimer`, with the interval and certain
        timer properties. This does not start the timer, however.

        This method should only be called once, preferably in the initialization logic.

        Returns:
            None.
        """
        self.countdown_timer = QTimer()
        self.countdown_timer.setInterval(INTERVAL)

        # Make PyQt use the most accurate timer possible, without delaying
        # updates to reduce CPU usage. This allows the progress bar to
        # update at a smoother interval.
        self.countdown_timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.countdown_timer.timeout.connect(self._on_timeout)

    def _setup_ui(self) -> None:
        """
        Internal method. Sets up the screen UI, including fonts, widgets, and layouts, for the first time.
        This method should only be called once, preferably in the initialization logic.

        Returns:
            None.
        """
        ## FONTS SETUP ##
        loading_font = QFont()
        loading_font.setPointSize(72)

        ## WIDGETS SETUP ##
        self.countdown_lbl = QLabel()
        self.countdown_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.countdown_lbl.setFont(loading_font)

        # Using a range of 0-10000 rather than 0-100 allows for smoother
        # visual movement. Initialize progress bar value at full, since
        # we are counting down, not up.
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 10000)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedWidth(200)
        self.progress_bar.setValue(10000)

        ## LAYOUTS SETUP ##
        # Add same stretch on top and bottom to ensure widgets appear in the middle
        vbox = QVBoxLayout()
        vbox.addStretch()
        vbox.addWidget(self.countdown_lbl)
        vbox.addSpacing(10)
        vbox.addWidget(self.progress_bar, alignment=Qt.AlignmentFlag.AlignCenter)
        vbox.addStretch()

        self.setLayout(vbox)

    def _on_timeout(self) -> None:
        """
        Internal method. Intended to be run when the countdown `QTimer` times out. Internally increases
        the elapsed time, decreases the progress bar, and, if needed, the visual seconds counter. The seconds
        counter is a whole integer display, so it never displays fractions of a second (e.g. 2.7).

        The progress bar never decreases below 0%, and the countdown text never goes below 1 visually, even
        if the time reaches 0, preventing a perceived flicker in case of network latency. Neither ever increases.

        Returns:
            None.
        """
        self.elapsed_ms += INTERVAL

        # Calculate remaining milliseconds, ensuring it never dips below 0ms
        remaining = max(0, self.total_ms - self.elapsed_ms)
        percent = (remaining / self.total_ms) * 100

        # Set progress bar, and adapts the percentage to the 0-10000 range
        # that the progress bar is set to.
        self.progress_bar.setValue(int(percent * 100))

        # Calculate remaining seconds, then ceil it. For example, if
        # there are 1.5 seconds remaining, the text displays 2, preventing
        # a lower value from being seen too soon.
        seconds = math.ceil((self.total_ms - self.elapsed_ms) / 1000)

        # Set the text to show the seconds remaining, ensuring the user never
        # sees anything below 1 second. In an ideal scenario, the screen would
        # switch instantly when reaching zero, but because of networking latency,
        # if zero was allowed, a 0 would be seen for a split second before
        # transitioning, which can be awkwardly seen as a flicker.
        self.countdown_lbl.setText(str(max(1, seconds)))

        # Stop timer if finished; although the UI would not update, this saves CPU power
        if remaining <= 0:
            self.countdown_timer.stop()

    def on_enter(self, payload: dict) -> None:
        # Get duration in milliseconds
        duration = payload["duration"]

        # Reset timer and UI to initial values
        self.total_ms = duration
        self.elapsed_ms = 0

        self.countdown_lbl.setText(str(self.total_ms // 1000))
        self.progress_bar.setValue(10000)

        self.countdown_timer.start()

    def on_leave(self) -> None:
        # Stop countdown after leaving screen to save CPU power
        self.countdown_timer.stop()
