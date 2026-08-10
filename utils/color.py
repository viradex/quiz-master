"""
color.py

Contains utility functions related to color in UI.
"""

from pathlib import Path

from PyQt6.QtGui import QColor

from core.config.constants import RTT_GOOD_THRESHOLD_MS, RTT_WARNING_THRESHOLD_MS
from utils.paths import get_icons_dir


def darken_color(color_str: str, factor: float) -> str:
    """
    Changes the hex code of a color to be darker, as determined by the factor.

    - `0.0`: Color remains the same.
    - `0.5`: Color is slightly darker.
    - `1.0`: Color is darkened significantly.

    Arguments:
        color_str: The hex color code of the color to darken. A string is used as it represents a hex
            color code well.

        factor: A float determining the darkness of the new color, within the range of [0.0, 1.0]. If
            it is outside this range, it is clamped back to the range. A float is used as it represents
            a percentage well, making it more intuitive.

    Returns:
        A string containing the hex code of the darkened color. A string is used as it represents a hex
        color code well.
    """
    # Clamps factor to range [0.0, 1.0]
    factor = max(0.0, min(1.0, factor))

    # Convert factor to a value 100-200 for PyQt
    color = QColor(color_str)
    strength = int(factor * 100 + 100)

    # Returns hex code with .name()
    return color.darker(strength).name()


def get_ping_color(rtt_ms: float | None = None) -> Path:
    """
    Gets the resource location of the image that best represents the round-trip time provided, within
    the threshold, as a `pathlib.Path`.

    The current colors that can be given are:
    - Gray: If round-trip time is None.
    - Green: If round-trip time is below 50ms.
    - Yellow: If round-trip time is between 50ms to 150ms.
    - Red: If round-trip time is above 150ms.

    Arguments:
        rtt_ms: The round-trip time to derive the color from, or None if the time is unknown. A float is
            used as it represents the round-trip time well from its original derived value. Defaults to
            None.

    Returns:
        A Path object that points to the asset location that best represents the round-trip time provided.
    """
    icons_path = get_icons_dir()

    if rtt_ms is None:
        return icons_path / "ping_gray.png"
    elif rtt_ms < RTT_GOOD_THRESHOLD_MS:
        return icons_path / "ping_green.png"
    elif rtt_ms < RTT_WARNING_THRESHOLD_MS:
        return icons_path / "ping_yellow.png"
    else:
        return icons_path / "ping_red.png"
