from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QPen, QColor


class Spinner(QWidget):
    def __init__(
        self,
        size: int = 120,
        color: QColor = QColor(100, 180, 255),
        arc_length: int = 120,
        interval_ms: int = 30,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.angle: int = 0
        self.color: QColor = color
        self.arc_length: int = arc_length

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._rotate)
        self.interval_ms: int = interval_ms

        self.setFixedSize(size, size)

    def start(self) -> None:
        """Start the spinner."""
        if not self.timer.isActive():
            self.timer.start(self.interval_ms)

    def stop(self) -> None:
        """Stop the spinner. This should be run when
        the spinner is no longer visible to reduce lag."""
        self.timer.stop()

    def paintEvent(self, event) -> None:
        # Run automatically by PyQt
        # Antialiasing to remove jagged edges
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        thickness = max(2, self.width() // 18)
        margin = thickness + 2

        # Rounded edges rather than square
        pen = QPen(self.color, thickness)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        # Spinner bounding box, then draws starting spinner within
        # 1 degree = 16 units, hence the *16
        rect = self.rect().adjusted(margin, margin, -margin, -margin)
        painter.drawArc(rect, int(self.angle * 16), int(self.arc_length * 16))

    def _rotate(self) -> None:
        # Every frame, minus 6 degrees from angle (within range 0-359)
        self.angle = (self.angle - 6) % 360
        self.update()
