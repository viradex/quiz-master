from pathlib import Path
from PyQt6.QtWidgets import QPushButton, QToolButton
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QSize


def create_return_button(
    btn_text: str, btn_width: int = 60, btn_font_size: int = 12
) -> QPushButton:
    """Configure a button that is styled to denote returning or ending the current process for UI consistency."""
    button = QPushButton()

    button.setText(btn_text)
    button.setFixedWidth(btn_width)

    button.setObjectName("return")
    button.setStyleSheet(f"""
        QPushButton#return {{
            background-color: transparent;
            color: #bbb;
            border: 1px solid #444;
            border-radius: 8px;
            padding: 6px;
            font-size: {btn_font_size}px;
        }}

        QPushButton#return:hover {{
            background-color: #333;
            color: white;
        }}

        QPushButton#return:pressed {{
            background-color: #222;
        }}

        QPushButton#return:disabled {{
            background-color: transparent;
            color: #666;
            border: 1px solid #2f2f2f;
        }}
    """)

    return button


def create_tool_icon_button(icon: Path | str, tooltip: str, icon_size: int) -> None:
    tool_button = QToolButton()
    tool_button.setToolTip(tooltip)

    tool_button.setIcon(QIcon(str(icon)))
    tool_button.setIconSize(QSize(icon_size, icon_size))
    tool_button.setFixedSize(icon_size + 4, icon_size + 4)

    tool_button.setCursor(Qt.CursorShape.PointingHandCursor)
    tool_button.setAutoRaise(True)
    tool_button.setStyleSheet("""
        QToolButton {
            background-color: transparent;
            border: none;
            padding: 0px;
        }
                                    
        QToolButton:hover {
            background-color: transparent;
            border: none;
        }
                                    
        QToolButton:pressed {
            background-color: transparent;
            border: none;
        }
    """)

    return tool_button
