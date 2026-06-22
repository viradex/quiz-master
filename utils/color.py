from PyQt6.QtGui import QColor


def darken_color(color_str: str, factor: float = 0.5) -> str:
    """
    Makes a color darker, returning a hex color code.
    A higher factor makes the color darker. Factor ranges from 0.0-1.0.
    """
    factor = max(0.0, min(1.0, factor))
    color = QColor(color_str)
    strength = int(100 + (1 - factor) * 100)

    return color.darker(strength).name()
