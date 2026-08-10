"""
dialog.py

Contains methods for displaying custom `QMessageBox` dialogs.
"""

from PyQt6.QtWidgets import QMessageBox, QWidget


def confirm_warning(parent: QWidget | None, title: str, desc: str) -> bool:
    """
    Creates and displays a custom warning confirmation box, with Yes and No options. The default selected
    value is No.

    Arguments:
        parent: The parent to make this message box a child of, or None to set no parent.

        title: The title of the message box. A string is used as it easily displays text and is supported
            by the message box.

        desc: The description of the message box. A string is used as it easily displays text and is
            supported by the message box.

    Returns:
        True if Yes was selected, else False if No was selected. A boolean is used as it can be easily
        used in conditionals and represents the value chosen well rather than a `QMessageBox` enum.
    """

    # Set warning icon
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Icon.Warning)

    msg.setWindowTitle(title)
    msg.setText(desc)

    # Set Yes and No buttons and make default No
    msg.setStandardButtons(
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    msg.setDefaultButton(QMessageBox.StandardButton.No)

    # Display message box
    result = msg.exec()

    return result == QMessageBox.StandardButton.Yes
