from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QFont
from PyQt6.QtCore import Qt


class AnswerBarChart(QWidget):
    def __init__(self):
        super().__init__()

        self.colors = [
            "#ff4d4d",
            "#4da6ff",
            "#ffd24d",
            "#4dff88",
        ]

        self.setMinimumSize(500, 300)

    def set_values(self, values):
        if len(values) > 4:
            raise ValueError(
                f"Too many values; expected 4 or less, received {len(values)}"
            )

        self.values = values

        self.labels = ["A", "B", "C", "D"]
        self.labels = self.labels[: len(self.values)]

    def paintEvent(self, event):
        if not self.values:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background
        painter.fillRect(self.rect(), QColor("#1e1e1e"))

        margin = 40
        chart_width = self.width() - margin * 2
        chart_height = self.height() - margin * 2

        max_value = max(self.values)

        # Increased spacing
        gap = 24
        num_bars = len(self.values)

        bar_width = (chart_width - gap * (num_bars - 1)) / num_bars

        # Fonts
        label_font = QFont("Segoe UI", 14)
        label_font.setBold(True)

        value_font = QFont("Segoe UI", 12)
        value_font.setBold(False)

        for i, (value, label, color) in enumerate(
            zip(self.values, self.labels, self.colors)
        ):
            height_ratio = value / max_value
            bar_height = chart_height * height_ratio

            x = margin + i * (bar_width + gap)
            y = margin + chart_height - bar_height

            # Draw bar
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
                margin + chart_height + 8,
                int(bar_width),
                30,
                Qt.AlignmentFlag.AlignCenter,
                label,
            )
