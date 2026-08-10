"""
answer_bar_chart.py

The answer bar chart component. Used to display the frequencies of the answers selected.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QPaintEvent
from PyQt6.QtWidgets import QWidget

from utils.color import darken_color

# Colors for each bar respective to A, B, C, and D
BAR_COLORS: list[str] = [
    "#C94F4F",
    "#4A78C2",
    "#B89B2E",
    "#3E9B68",
]

# Define margins
TOP_MARGIN = 30
BOTTOM_MARGIN = 25
SIDE_MARGIN = 10

# Define bar drawing attributes
BAR_GAP = 24
MIN_BAR_HEIGHT = 3
BAR_CORNER_RADIUS = 4


class AnswerBarChart(QWidget):
    """
    Creates the answer bar chart, inheriting `QWidget`.

    Used to show a visual bar chart representation of the amount of answers for each answer.

    Arguments:
        parent: The parent of this screen, or None.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # Initialize empty attributes
        self.values: list[int] = []
        self.labels: list[str] = []
        self.correct_index: int = 0

        self._setup_fonts()

    def _setup_fonts(self) -> None:
        """
        Internal method. Sets up all `QFont` instances and their properties that the widgets will utilize. If
        a font is modified via QSS stylesheets, they are not included here.

        Returns:
            None.
        """
        self.label_font = QFont()
        self.label_font.setPointSize(12)

        self.value_font = QFont()
        self.value_font.setPointSize(14)
        self.value_font.setBold(True)

    def set_values(self, values: list[int], correct_index: int) -> None:
        """
        Set the values to display on the bar chart, and the correct answer to highlight. Repaints the widget
        when values are set to ensure it remains up-to-date on the UI.

        Arguments:
            values: A list of integers that are respective to the answer labels A, B, C, and D, signifying the
                number of responses for each answer. The length must be between 2 and 4 elements inclusive. A
                list is used as it is ordered, allowing for the positions of the number of responses not to switch.

            correct_index: The correct answer index, zero-based, as an integer. An integer is used as it can be
                easily used to find the position in a list.

        Returns:
            None.

        Raises:
            ValueError: If the length of values provided is not within the valid range of 2-4 inclusive, or if
                the correct index is not within the valid range of minimum 0 and maximum `len(values) - 1`.
        """
        # Perform validation checks to catch errors earlier rather than later execution of the code
        if not 2 <= len(values) <= 4:
            raise ValueError(
                f"Invalid values length; must be between 2 and 4 elements inclusive, but received {len(values)}"
            )

        if not 0 <= correct_index < len(values):
            raise ValueError(
                f"Correct index out of range; must be between 0 and {len(values) - 1} inclusive, but received {correct_index}"
            )

        self.values = values

        # Trim length of labels to only include how many values there are
        self.labels = ["A", "B", "C", "D"]
        self.labels = self.labels[: len(self.values)]

        self.correct_index = correct_index

        # Mark the component as 'dirty' so Qt repaints it whenever possible
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Called automatically by PyQt when the widget needs repainting. If `self.values` has not been set,
        nothing is painted.

        Arguments:
            event: An argument passed automatically by PyQt upon this method being run. This attribute is not
                utilized, but is required to be specified to prevent the app from crashing.

        Returns:
            None.
        """
        # Do not paint yet if nothing has been set
        if not self.values:
            return

        # Anti-aliasing to smooth edges
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background
        painter.fillRect(self.rect(), QColor("#1e1e1e"))

        # Layout calculations for determining drawable area
        chart_width = self.width() - SIDE_MARGIN * 2
        chart_height = self.height() - TOP_MARGIN - BOTTOM_MARGIN

        # Max value to find max height
        max_value = max(self.values)

        # Gets number of bars, and calculates width of each bar mathematically
        num_bars = len(self.values)
        bar_width = (chart_width - BAR_GAP * (num_bars - 1)) / num_bars

        # Loops through each value and adds a new bar
        # zip() will stop when running out of values
        for i, (value, label, color) in enumerate(
            zip(self.values, self.labels, BAR_COLORS)
        ):
            # Calculates height based on bar with max height,
            # and ratio of other bars to that, ensuring 0 values
            # will have a thin sliver
            if value == 0:
                bar_height = MIN_BAR_HEIGHT
            else:
                height_ratio = value / max_value
                bar_height = max(chart_height * height_ratio, MIN_BAR_HEIGHT)

            # Positions bars
            x = SIDE_MARGIN + i * (bar_width + BAR_GAP)
            y = TOP_MARGIN + chart_height - bar_height

            # Darken the color if it isn't the correct answer
            # If it is the correct answer, add a tick beforehand
            if i != self.correct_index:
                color = darken_color(color, factor=0.4)
            else:
                value = f"✔ {value}"

            # Draw rounded rectangle, representing a bar
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(color))
            painter.drawRoundedRect(
                int(x),
                int(y),
                int(bar_width),
                int(bar_height),
                BAR_CORNER_RADIUS,
                BAR_CORNER_RADIUS,
            )

            # Value above bar
            painter.setFont(self.value_font)
            painter.setPen(QColor(color))
            painter.drawText(
                int(x),
                int(y) - 28,
                int(bar_width),
                24,
                Qt.AlignmentFlag.AlignCenter,
                str(value),
            )

            # Label below bar
            painter.setFont(self.label_font)
            painter.setPen(Qt.GlobalColor.white)
            painter.drawText(
                int(x),
                BOTTOM_MARGIN + chart_height + 8,
                int(bar_width),
                30,
                Qt.AlignmentFlag.AlignCenter,
                label,
            )
