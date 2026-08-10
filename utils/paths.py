"""
paths.py

Provides a central location to get certain directories, and other utility functions relating to paths.
"""

from pathlib import Path


def get_base_dir() -> Path:
    """
    Get base directory. Can be used in conjunction with path chaining.

    Returns:
        A Path representing the base directory. A Path is returned rather than a string to allow for further
        path chaining or path manipulation directly.
    """
    return Path(__file__).resolve().parent.parent


def get_icons_dir() -> Path:
    """
    Get icons directory. Can be used in conjunction with path chaining.

    Returns:
        A Path representing the icons directory. A Path is returned rather than a string to allow for further
        path chaining or path manipulation directly.
    """
    return get_base_dir() / "ui" / "assets" / "icons"


def get_quizzes_dir() -> Path:
    """
    Get quizzes directory. Can be used in conjunction with path chaining.

    Returns:
        A Path representing the quizzes directory. A Path is returned rather than a string to allow for further
        path chaining or path manipulation directly.
    """
    return get_base_dir() / "data" / "quizzes"
