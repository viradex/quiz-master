from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QCheckBox,
    QHBoxLayout,
    QVBoxLayout,
)

from core.app.screen_ids import Screens
from ui.components.input import CharacterCountInput
from ui.screens.base_screen import BaseScreen

from ui.components.button import create_return_button
from core.config.constants import MAX_QUIZ_TITLE_LENGTH


class CommonQuizSetupScreen(BaseScreen):
    title_text = "Quiz Master – Create New Quiz"

    # First is quiz data
    # Second is edit_questions (whether to open quiz editor or quiz manager)
    save_requested = pyqtSignal(dict, bool)

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

        self.title_counter = CharacterCountInput(MAX_QUIZ_TITLE_LENGTH)
        self.title_counter.line_edit.returnPressed.connect(self.on_enter_pressed)
        self.title_counter.line_edit.setFont(form_font)

        self.shuffle_check = QCheckBox("Shuffle questions")
        self.shuffle_check.setFont(form_font)
        self.shuffle_check.setStyleSheet("spacing: 15px;")

        # Action buttons
        self.return_btn = create_return_button(
            "Discard and Return", btn_width=200, btn_font_size=16
        )
        self.return_btn.setFixedHeight(45)
        self.return_btn.clicked.connect(lambda: self.go_to(Screens.COMMON_QUIZ_MANAGER))

        # Acts as the "Create" button in Create mode and "Edit Questions" button in Edit mode
        # Either case, it opens the main quiz editor program
        self.create_btn = QPushButton()
        self.create_btn.setFixedSize(200, 50)
        self.create_btn.clicked.connect(self.on_create)
        self.create_btn.setStyleSheet("font-size: 18px;")

        # This button is not shown when in Create mode
        # In Edit mode, returns to the quiz manager without opening the editor
        self.save_btn = QPushButton("Save and Return")
        self.save_btn.setFixedSize(200, 50)
        self.save_btn.clicked.connect(self.on_save)
        self.save_btn.setStyleSheet("font-size: 18px;")

        # Needed due to the Save and Create button appearing/disappearing depending on the mode
        self.btn_spacer = QWidget()
        self.btn_spacer.setFixedWidth(2)

        ## LAYOUTS SETUP ##
        title_hbox = QHBoxLayout()
        title_hbox.addWidget(title_lbl)
        title_hbox.addSpacing(25)
        title_hbox.addWidget(self.title_counter)

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
        """
        Opens the screen in Create mode. Hides the Save button and forces
        the user into the quiz editor when done.
        """
        self.set_title("Quiz Master – Create New Quiz")

        self.title.setText("Enter new quiz details:")
        self.create_btn.setText("Create")
        self.save_btn.hide()
        self.btn_spacer.hide()

        self.title_counter.line_edit.setText("")
        self.shuffle_check.setChecked(False)

    def edit_mode(self, quiz_title: str, do_shuffle: bool) -> None:
        """
        Opens the screen in Edit mode. Allows the user to Save and Exit without
        opening the quiz editor, or edit questions for the quiz by opening the editor.
        """
        self.set_title("Quiz Master – Edit Quiz")

        self.title.setText("Edit quiz details:")
        self.create_btn.setText("Edit Questions")
        self.save_btn.show()
        self.btn_spacer.show()

        # Prefill info from quiz
        self.title_counter.line_edit.setText(quiz_title)
        self.shuffle_check.setChecked(do_shuffle)

    def get_data_entered(self) -> dict[str, str | bool]:
        """Get all data from the input fields as a dictionary."""
        return {
            "quiz_id": self.quiz_id,
            "quiz_title": self.title_counter.line_edit.text().strip(),
            "do_shuffle": self.shuffle_check.isChecked(),
        }

    def validate_data(self) -> bool:
        """Validate the data entered, showing an error message if it does not fulfill the requirements.
        Returns True if the data passes all tests, else False."""
        title = self.title_counter.line_edit.text().strip()

        if not title:
            self.show_error(
                "Empty Title",
                "Please ensure the title is filled in and try again.",
            )
            return False
        elif len(title) > MAX_QUIZ_TITLE_LENGTH:
            self.show_error(
                "Title Too Long",
                f"The title exceeds the maximum length of {MAX_QUIZ_TITLE_LENGTH} characters. Please shorten it and try again.",
            )
            return False

        return True

    def on_save(self) -> None:
        """Called upon saving in Edit mode. Saves the data entered but does not open the quiz editor."""
        # Automatically shows error modal boxes as well
        if not self.validate_data():
            return

        # If quiz already exists, save data but do not show quiz editor
        if self.quiz_id is not None:
            self.save_requested.emit(self.get_data_entered(), False)

    def on_create(self) -> None:
        """Called upon clicking Edit Questions in Edit mode or Create in Create mode.
        Saves the data and opens the editor."""
        data = self.get_data_entered()

        # Automatically shows error modal boxes as well
        if not self.validate_data():
            return

        # Save data and open quiz editor
        self.save_requested.emit(data, True)

    def on_enter_pressed(self) -> None:
        """
        The Enter key on the input field(s) do different actions depending on the mode.
        - Create mode: Saves quiz data and opens quiz editor.
        - Edit mode: Saves quiz data but does not open the editor; instead returns to the quiz manager.
        """
        # If there is no quiz_id, it is in create mode
        if self.quiz_id is None:
            self.on_create()
        else:
            self.on_save()

    def on_enter(self, payload: dict) -> None:
        # If there is no quiz data being passed, assume Create mode
        if payload is None:
            self.quiz_id = None
            self.create_mode()
        else:
            self.quiz_id = payload.get("quiz_id")
            self.edit_mode(payload["quiz_title"], payload["do_shuffle"])
