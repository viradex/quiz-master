from PyQt6.QtWidgets import QMessageBox, QWidget


def confirm_warning(parent: QWidget | None, title: str, desc: str) -> bool:
    """Creates a custom warning confirmation box. Returns True if the user selected Yes."""
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
