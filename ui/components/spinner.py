from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QPen, QColor


class Spinner(QWidget):
    def __init__(
        self,
        parent=None,
        size=120,
        color=QColor(100, 180, 255),
        arc_length=120,
        interval_ms=30,
    ):
        super().__init__(parent)

        self.angle = 0
        self.color = color
        self.arc_length = arc_length

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._rotate)
        self.interval_ms = interval_ms

        self.setFixedSize(size, size)

    def _rotate(self):
        self.angle = (self.angle - 6) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        thickness = max(2, self.width() // 18)
        margin = thickness + 2

        pen = QPen(self.color, thickness)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        rect = self.rect().adjusted(margin, margin, -margin, -margin)
        painter.drawArc(rect, int(self.angle * 16), int(self.arc_length * 16))

    def start(self):
        if not self.timer.isActive():
            self.timer.start(self.interval_ms)

    def stop(self):
        self.timer.stop()
