from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QLineEdit,
    QCheckBox,
    QVBoxLayout,
    QHBoxLayout,
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal

from core.app.screen_ids import Screens
from ui.screens.base_screen import BaseScreen

from ui.components.button import create_return_button


class CommonQuizSetupScreen(BaseScreen):
    title_text = "Quiz Master – Create New Quiz"

    submitted = pyqtSignal(dict)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setup_ui()

    def setup_ui(self) -> None:
        ## FONTS SETUP ##
        title_font = QFont()
        title_font.setPointSize(20)

        form_font = QFont()
        form_font.setPointSize(14)

        ## WIDGETS SETUP ##
        title = QLabel("Enter new quiz details:")
        title.setFont(title_font)

        title_lbl = QLabel("Quiz title:")
        title_lbl.setFont(form_font)

        self.title_input = QLineEdit()
        self.title_input.setFont(form_font)
        # self.title_input.returnPressed.connect(self.on_submit)

        self.shuffle_check = QCheckBox("Shuffle questions")
        self.shuffle_check.setFont(form_font)
        self.shuffle_check.setStyleSheet("spacing: 15px;")

        # Action buttons
        self.return_btn = create_return_button(
            "Return to Manager", btn_width=200, btn_font_size=16
        )
        self.return_btn.setFixedHeight(45)
        self.return_btn.clicked.connect(lambda: self.go_to(Screens.COMMON_QUIZ_MANAGER))

        self.create_btn = QPushButton("Create")
        self.create_btn.setFixedSize(240, 50)
        self.create_btn.setStyleSheet("font-size: 22px;")

        ## LAYOUTS SETUP ##
        title_hbox = QHBoxLayout()
        title_hbox.addWidget(title_lbl)
        title_hbox.addSpacing(25)
        title_hbox.addWidget(self.title_input)

        btn_hbox = QHBoxLayout()
        btn_hbox.addWidget(self.return_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        btn_hbox.addWidget(self.create_btn, alignment=Qt.AlignmentFlag.AlignRight)

        vbox_wrapper = QWidget()
        vbox_wrapper.setMaximumWidth(1000)

        vbox = QVBoxLayout(vbox_wrapper)
        vbox.setContentsMargins(20, 20, 20, 20)
        vbox.addStretch(1)
        vbox.addWidget(title)
        vbox.addSpacing(50)
        vbox.addLayout(title_hbox)
        vbox.addSpacing(30)
        vbox.addWidget(self.shuffle_check)
        vbox.addSpacing(40)
        vbox.addLayout(btn_hbox)
        vbox.addStretch(2)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(vbox_wrapper, stretch=6)
        hbox.addStretch(1)

        self.setLayout(hbox)

    def clear_fields(self) -> None:
        """Reset all form fields."""
        self.title_input.setText("")
        self.shuffle_check.setChecked(False)

    def on_leave(self) -> None:
        self.clear_fields()
