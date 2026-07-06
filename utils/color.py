from PyQt6.QtGui import QColor


def darken_color(color_str: str, factor: float = 0.5) -> str:
    """
    Makes a color darker, returning a hex color code.
    Factor ranges from 0.0-1.0, where 0.0 produces the darkest result and 1.0 leaves the color the same.
    """
    # Clamps factor to range [0.0, 1.0]
    factor = max(0.0, min(1.0, factor))

    # Convert factor to a value 100-200 for PyQt
    color = QColor(color_str)
    strength = int((1 - factor) * 100 + 100)

    # Returns hex code with .name()
    return color.darker(strength).name()
