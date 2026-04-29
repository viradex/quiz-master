from PyQt6.QtWidgets import QMessageBox


def not_implemented(parent):
    QMessageBox.warning(
        parent,
        "Coming Soon",
        "This feature is under development and will be available soon.",
    )
