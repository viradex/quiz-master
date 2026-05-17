from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import Qt


def not_implemented(parent):
    QMessageBox.warning(
        parent,
        "Coming Soon",
        "This feature is under development and will be available soon.",
    )


def confirm_warning(parent, title, desc):
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Icon.Warning)
    msg.setWindowTitle(title)
    msg.setText(desc)
    msg.setStandardButtons(
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    msg.setDefaultButton(QMessageBox.StandardButton.No)

    result = msg.exec()
    return result == QMessageBox.StandardButton.Yes
