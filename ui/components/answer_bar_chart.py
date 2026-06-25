from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QFont
from PyQt6.QtCore import Qt


class AnswerBarChart(QWidget):
    """Used to show a visual bar chart representation of the amount of answers for each answer."""

    def __init__(self) -> None:
        super().__init__()

        # Define colors for bars
        self.colors: list[str] = [
            "#C94F4F",
            "#4A78C2",
            "#B89B2E",
            "#3E9B68",
        ]

    def set_values(self, values: list[int]) -> None:
        """Set values for bars."""
        if len(values) > 4:
            raise ValueError(
                f"Too many values; expected 4 or less, received {len(values)}"
            )

        self.values = values

        self.labels = ["A", "B", "C", "D"]
        self.labels = self.labels[: len(self.values)]

    def paintEvent(self, event) -> None:
        """Automatically called whenever the widget needs repainting (e.g. due to resizing)."""
        if not self.values:
            return

        # Anti-aliasing to smooth edges
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background
        painter.fillRect(self.rect(), QColor("#1e1e1e"))

        # Layout caluclations for determining drawable area
        top_margin = 30
        bottom_margin = 25
        side_margin = 10

        chart_width = self.width() - side_margin * 2
        chart_height = self.height() - top_margin - bottom_margin

        # Max value to find max height
        max_value = max(self.values)

        # Gets number of bars, and calculates width of each bar mathematically
        gap = 24
        num_bars = len(self.values)

        bar_width = (chart_width - gap * (num_bars - 1)) / num_bars

        label_font = QFont()
        label_font.setPointSize(12)

        value_font = QFont()
        value_font.setPointSize(14)
        value_font.setBold(True)

        # Loops through each value and adds a new bar
        # zip() will stop when running out of values
        for i, (value, label, color) in enumerate(
            zip(self.values, self.labels, self.colors)
        ):
            # Caluculates height based on bar with max height,
            # and ratio of other bars to that
            height_ratio = value / max_value
            bar_height = chart_height * height_ratio

            # Positions bars
            x = side_margin + i * (bar_width + gap)
            y = top_margin + chart_height - bar_height

            # Draw rounded rectangle, representing a bar
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(color))
            painter.drawRoundedRect(
                int(x),
                int(y),
                int(bar_width),
                int(bar_height),
                4,
                4,
            )

            # Value above bar
            painter.setFont(value_font)
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
            painter.setFont(label_font)
            painter.setPen(Qt.GlobalColor.white)
            painter.drawText(
                int(x),
                bottom_margin + chart_height + 8,
                int(bar_width),
                30,
                Qt.AlignmentFlag.AlignCenter,
                label,
            )
