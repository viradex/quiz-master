"""
button.py

Contains various unique types of pre-built buttons or buttons with modified logic.
"""

from pathlib import Path

from PyQt6.QtCore import QRectF, QSize, Qt
from PyQt6.QtGui import QIcon, QPaintEvent, QTextOption
from PyQt6.QtWidgets import (
    QPushButton,
    QStyle,
    QStyleOptionButton,
    QStylePainter,
    QToolButton,
    QWidget,
)


class WordWrapButton(QPushButton):
    """
    Creates a `QPushButton` that supports word wrapping on its text. All other functionality about the button
    remains the same as a regular `QPushButton`. Inherits `QPushButton`.
    """

    def paintEvent(self, event: QPaintEvent):
        """
        Called automatically by PyQt when the widget needs repainting. Sets all styles the same as the parent
        button, but enables word wrapping on the text.

        Arguments:
            event: An argument passed automatically by PyQt upon this method being run. This attribute is not
                utilized, but is required to be specified to prevent the app from crashing.

        Returns:
            None.
        """
        # Creates a blank description of a button's styles and fills it in with current styles.
        option = QStyleOptionButton()
        self.initStyleOption(option)

        # Draw the button, without the text (using CE_PushButton would draw the text).
        painter = QStylePainter(self)
        painter.drawControl(QStyle.ControlElement.CE_PushButtonBevel, option)

        # Creates the rectangle that the text can be in, which is the size
        # of the button with 12px padding on all edges.
        rect = self.contentsRect().adjusted(12, 12, -12, -12)

        # Set the color of the text to adapt to the theme.
        painter.setPen(self.palette().buttonText().color())

        # Keeps the same properties of the font in the QSS specified for the parent button.
        painter.setFont(self.font())

        # Create a new text option with word wrap and align it to center.
        text_option = QTextOption()
        text_option.setWrapMode(QTextOption.WrapMode.WordWrap)
        text_option.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Draw the text inside the rectangle specified above, with the text set
        # on the button, and the word wrapped text configured above.
        painter.drawText(QRectF(rect), self.text(), text_option)


def create_return_button(
    btn_text: str,
    btn_width: int = 60,
    btn_font_size: int = 12,
    parent: QWidget | None = None,
) -> QPushButton:
    """
    Creates a button that is styled to signify returning to the previous screen/menu and/or ending the
    current process. The button is an outlined button that fills itself in when hovered.

    Arguments:
        btn_text: The text to display on the button, as a string. A string is used as it can easily represent
            a variety of characters.

        btn_width: Optional; the width of the button, in pixels. Defaults to 60. An integer is used as it
            represents a whole number which the width requires.

        btn_font_size: Optional; the font size of the text inside the button, in point size. Defaults to 12.
            An integer is used as it represents a whole number which the font size requires.

        parent: The parent to make this button a child of. Defaults to None.

    Returns:
        The QPushButton created.
    """
    button = QPushButton(parent)

    button.setText(btn_text)
    button.setFixedWidth(btn_width)

    button.setStyleSheet(f"""
        QPushButton {{
            background-color: transparent;
            color: #bbb;
            border: 1px solid #444;
            border-radius: 8px;
            padding: 6px;
            font-size: {btn_font_size}px;
        }}

        QPushButton:hover {{
            background-color: #333;
            color: white;
        }}

        QPushButton:pressed {{
            background-color: #222;
        }}

        QPushButton:disabled {{
            background-color: transparent;
            color: #666;
            border: 1px solid #2f2f2f;
        }}
    """)

    return button


def create_tool_icon_button(
    icon: Path | str, tooltip: str, icon_size: int, parent: QWidget | None = None
) -> QToolButton:
    """
    Creates an icon-only tool button, with a tooltip. The icon is always a fixed 1:1 ratio, and the icon size
    provided is repeated on the width and height.

    Arguments:
        icon: The path to the icon, as a Path or string (though the Path is automatically converted to a string).
            A Path is accepted as it allows for easier usage.

        tooltip: The tooltip text to display when hovering over the button, to provide extra information. A string
            is used as it represents text well.

        icon_size: The size of the width and height of the icon. Since the ratio is always 1:1, the value entered
            is reflected on the width and height. An integer is used rather than a tuple as it is repeated
            automatically.

        parent: The parent to make this tool button a child of. Defaults to None.

    Returns:
        The QToolButton created.
    """
    tool_button = QToolButton(parent)
    tool_button.setToolTip(tooltip)

    tool_button.setIcon(QIcon(str(icon)))
    tool_button.setIconSize(QSize(icon_size, icon_size))

    # Click area is 4x4 pixels larger than the icon
    tool_button.setFixedSize(icon_size + 4, icon_size + 4)

    # Make the cursor change when hovering to display that it's clickable
    tool_button.setCursor(Qt.CursorShape.PointingHandCursor)

    # Make the button only show when hovering
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
