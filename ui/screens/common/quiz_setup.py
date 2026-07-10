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

    save_requested = pyqtSignal(dict)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        # If None, create mode
        # If str, edit mode
        self.quiz_id: str | None = None

        self.setup_ui()

    def setup_ui(self) -> None:
        ## FONTS SETUP ##
        title_font = QFont()
        title_font.setPointSize(20)

        form_font = QFont()
        form_font.setPointSize(14)

        ## WIDGETS SETUP ##
        self.title = QLabel()
        self.title.setFont(title_font)

        title_lbl = QLabel("Quiz title:")
        title_lbl.setFont(form_font)

        self.title_input = QLineEdit()
        self.title_input.setFont(form_font)
        self.title_input.returnPressed.connect(self.on_create)

        self.shuffle_check = QCheckBox("Shuffle questions")
        self.shuffle_check.setFont(form_font)
        self.shuffle_check.setStyleSheet("spacing: 15px;")

        # Action buttons
        self.return_btn = create_return_button(
            "Discard and Return", btn_width=200, btn_font_size=16
        )
        self.return_btn.setFixedHeight(45)
        self.return_btn.clicked.connect(lambda: self.go_to(Screens.COMMON_QUIZ_MANAGER))

        self.create_btn = QPushButton()
        self.create_btn.setFixedSize(200, 50)
        self.create_btn.clicked.connect(self.on_create)
        self.create_btn.setStyleSheet("font-size: 18px;")

        self.save_btn = QPushButton("Save and Return")
        self.save_btn.setFixedSize(200, 50)
        self.save_btn.clicked.connect(self.on_save)
        self.save_btn.setStyleSheet("font-size: 18px;")

        self.btn_spacer = QWidget()
        self.btn_spacer.setFixedWidth(2)

        ## LAYOUTS SETUP ##
        title_hbox = QHBoxLayout()
        title_hbox.addWidget(title_lbl)
        title_hbox.addSpacing(25)
        title_hbox.addWidget(self.title_input)

        btn_hbox = QHBoxLayout()
        btn_hbox.addWidget(self.return_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        btn_hbox.addStretch()
        btn_hbox.addWidget(self.create_btn, alignment=Qt.AlignmentFlag.AlignRight)
        btn_hbox.addWidget(self.btn_spacer)
        btn_hbox.addWidget(self.save_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        vbox_wrapper = QWidget()
        vbox_wrapper.setMaximumWidth(1000)

        vbox = QVBoxLayout(vbox_wrapper)
        vbox.setContentsMargins(20, 20, 20, 20)
        vbox.addStretch(1)
        vbox.addWidget(self.title)
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

    def create_mode(self) -> None:
        self.set_title("Quiz Master – Create New Quiz")

        self.title.setText("Enter new quiz details:")
        self.create_btn.setText("Create")
        self.save_btn.hide()
        self.btn_spacer.hide()

        # TODO only for easier accessibility to quiz editor screen
        # set to "" when done
        self.title_input.setText("Temporary Quiz")
        self.shuffle_check.setChecked(False)

    def edit_mode(self, quiz_title: str, do_shuffle: bool) -> None:
        self.set_title("Quiz Master – Edit Quiz")

        self.title.setText("Edit quiz details:")
        self.create_btn.setText("Edit Questions")
        self.save_btn.show()
        self.btn_spacer.show()

        self.title_input.setText(quiz_title)
        self.shuffle_check.setChecked(do_shuffle)

    def get_data_entered(self) -> dict[str, str | bool]:
        return {
            "quiz_id": self.quiz_id,
            "quiz_title": self.title_input.text().strip(),
            "do_shuffle": self.shuffle_check.isChecked(),
        }

    def on_save(self) -> None:
        if self.quiz_id is not None:
            self.save_requested.emit(self.get_data_entered())

        self.go_to(Screens.COMMON_QUIZ_MANAGER)

    def on_create(self) -> None:
        data = self.get_data_entered()

        if not data["quiz_title"]:
            self.show_error(
                "Empty Title",
                "Please ensure the title is filled in and try again.",
            )
            return

        self.save_requested.emit(data)

    def on_enter(self, payload: dict | None = None):
        self.quiz_id = payload.get("quiz_id")

        if self.quiz_id is None:
            self.create_mode()
        else:
            self.edit_mode(payload["quiz_title"], payload["do_shuffle"])
