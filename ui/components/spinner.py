"""
spinner.py

The spinner UI component. Allows showing a customizable indefinite waiting indicator for users.
"""

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QPainter, QPaintEvent, QPen
from PyQt6.QtWidgets import QWidget

# The length of the spinner visible section, out of 360
# Current value is 1/3 of the circle
ARC_LENGTH = 120


class Spinner(QWidget):
    """
    Creates the spinner component. The spinner is a rounded circle that spins indefinitely, with a
    customizable color and speed. This should be used for a loading progress where the time to complete
    the task is unknown (an indefinite loading indicator). Inherits `QWidget`.

    Arguments:
        size: The size in pixels of the spinner. As the spinner is a square with 1:1 ratio, the size is
            applied to the width and height of the spinner. An integer is used as the size only accepts
            whole values.

        interval_ms: The speed that the spinner spins at, in milliseconds. Smaller values make the spinner
            spin faster and appear more smooth, but can cause more frequent repaints. Optional; defaults to
            20.

        color: The color of the spinner, as either a `QColor` or hex code in a string. Defaults to None, in
            which case the color will be set to white.

        parent: The parent to make this spinner a child of, or None to set no parent. Defaults to None.
    """

    def __init__(
        self,
        size: int,
        interval_ms: int = 20,
        color: QColor | str | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.interval_ms: int = interval_ms

        # Convert from string to QColor if needed or set to white if no color provided
        self.color: QColor = QColor(color) if color is not None else QColor("#fff")

        self._angle: int = 0

        # Set size of spinner
        self.setFixedSize(size, size)

        self._setup_timer()

    def _setup_timer(self) -> None:
        """
        Internal method. Sets up the `QTimer` needed to rotate the spinner, with the interval configured
        based on the interval attribute. This method should only be run once, preferably in the initialization
        logic.

        Returns:
            None.
        """
        self.timer = QTimer(self)
        self.timer.setInterval(self.interval_ms)
        self.timer.timeout.connect(self._rotate)

    def start(self) -> None:
        """
        Starts rotating the spinner, if it has not already started.

        Returns:
            None.
        """
        # Only start spinner if it hasn't started yet
        if not self.timer.isActive():
            self.timer.start()

    def stop(self) -> None:
        """
        Stop rotating the spinner, freezing the spinner in place from when it was stopped. This method should
        be run when the spinner is no longer visible to reduce CPU usage.

        Returns:
            None.
        """
        self.timer.stop()

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Called automatically by PyQt when the widget needs repainting. Repaints the widget to reflect any angle
        changes. If this method is wanted to be invoked, `update()` should be called instead.

        Arguments:
            event: An argument passed automatically by PyQt upon this method being run. This attribute is not
                utilized, but is required to be specified to prevent the app from crashing.

        Returns:
            None.
        """
        # Antialiasing to remove jagged edges on spinner
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Set thickness to be a minimum of 2 and adapt to the size of the spinner
        thickness = max(2, self.width() // 18)

        # Makes margin slightly larger than the thickness of the spinner to avoid it being clipped
        margin = thickness + 2

        # USe rounded edges rather than square edges for a more modern look
        pen = QPen(self.color, thickness)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        # Spinner bounding box with margins
        rect = self.rect().adjusted(margin, margin, -margin, -margin)

        # 1 degree is 16 units in Qt, hence the multiplication by 16.
        # Draw an arc shape that represents a section of the spinner.
        painter.drawArc(rect, int(self._angle * 16), int(ARC_LENGTH * 16))

    def _rotate(self) -> None:
        """
        Internal method. Intended to be called by the timer timeout. Rotates the spinner by 6 degrees every
        time it is called. Updates the spinner to make it visually 'spin'.

        Returns:
            None.
        """
        # Every frame, minus 6 degrees from angle (within range 0-359, which modulo helps achieve)
        self._angle = (self._angle - 6) % 360
        self.update()
