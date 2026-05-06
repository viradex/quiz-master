from PyQt6.QtGui import QColor


def darken_color(color_str, factor=0.5):
    factor = max(0.0, min(1.0, factor))
    color = QColor(color_str)
    strength = int(100 + (1 - factor) * 100)

    return color.darker(strength).name()
