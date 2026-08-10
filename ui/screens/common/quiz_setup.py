"""
quiz_setup.py

The quiz setup UI screen. Allows configuring the title and certain options of a quiz for a new or
existing quiz, and then allows saving it, discarding changes, or also editing questions.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.app.screen_ids import Screen
from core.config.constants import MAX_QUIZ_TITLE_LENGTH
from ui.components.button import create_return_button
from ui.components.input import CharacterCountLineEdit
from ui.screens.base_screen import BaseScreen


class CommonQuizSetupScreen(BaseScreen):
    """
    Creates the quiz setup screen, inheriting BaseScreen. This screen is part of the 'common' category.

    This screen is responsible for allowing users to edit the main configuration of a quiz as a whole,
    by editing or creating a new quiz, and then editing questions and/or returning to the quiz manager.

    Attributes:
        title_text: The default text of the screen when entered. A string is used as that is what the
            title changing code requires.

        save_requested: A `pyqtSignal` that emits when the user wishes to save changes made. The relevant
            quiz data to edit is given as a dictionary, along with a boolean specifying whether or not to
            open the quiz editor (True to open quiz editor, False to go back to quiz manager). Both are given
            as arguments in the specified order.

    Arguments:
        parent: The parent of this screen, or None. Typically, this is the MainWindow.
    """

    title_text = "Quiz Master – Create New Quiz"

    # First is relevant quiz data
    # Second is whether to edit questions (True for quiz editor, False for quiz manager)
    save_requested = pyqtSignal(dict, bool)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # The quiz ID can also be used to identify if the screen is in Create or Edit mode:
        # - If None, create mode
        # - If string, edit mode
        self.quiz_id: str | None = None

        self._setup_ui()

    def _setup_ui(self) -> None:
        """
        Internal method. Sets up the screen UI for the first time. This method should only be called once,
        preferably in the initialization logic.

        Returns:
            None.
        """
        self._setup_fonts()
        self._setup_widgets()
        self._setup_layouts()

    def _setup_fonts(self) -> None:
        """
        Internal method. Sets up all `QFont` instances and their properties that the widgets will utilize. If
        a font is modified via QSS stylesheets, they are not included here.

        Returns:
            None.
        """
        self.title_font = QFont()
        self.title_font.setPointSize(20)

        self.form_font = QFont()
        self.form_font.setPointSize(14)

    def _setup_widgets(self) -> None:
        """
        Internal method. Sets up all widgets used by the screen, including styling and slots, if needed. These
        widgets are not added to any global layout in this method, however.

        Returns:
            None.
        """
        # Title of screen
        self.title = QLabel()
        self.title.setFont(self.title_font)

        # Title entry field
        self.title_lbl = QLabel("Quiz title:")
        self.title_lbl.setFont(self.form_font)

        self.title_counter = CharacterCountLineEdit(MAX_QUIZ_TITLE_LENGTH)
        self.title_counter.line_edit.returnPressed.connect(self._on_enter_pressed)
        self.title_counter.line_edit.setFont(self.form_font)

        # Shuffle checkbox
        self.shuffle_check = QCheckBox("Shuffle questions")
        self.shuffle_check.setFont(self.form_font)
        self.shuffle_check.setStyleSheet("spacing: 15px;")

        # Action buttons
        self.return_btn = create_return_button(
            "Discard and Return", btn_width=200, btn_font_size=16
        )
        self.return_btn.setFixedHeight(45)
        self.return_btn.clicked.connect(lambda: self.go_to(Screen.COMMON_QUIZ_MANAGER))

        # Acts as the "Create" button in Create mode and "Edit Questions" button in Edit mode
        # Either case, it opens the main quiz editor program
        self.create_btn = QPushButton()
        self.create_btn.setFixedSize(200, 50)
        self.create_btn.clicked.connect(self._on_create)
        self.create_btn.setStyleSheet("font-size: 18px;")

        # This button is not shown when in Create mode
        # In Edit mode, returns to the quiz manager without opening the editor
        self.save_btn = QPushButton("Save and Return")
        self.save_btn.setFixedSize(200, 50)
        self.save_btn.clicked.connect(self._on_save)
        self.save_btn.setStyleSheet("font-size: 18px;")

        # Needed due to the Save and Create button appearing/disappearing depending on the mode
        # Can show/hide depends on the buttons shown
        self.btn_spacer = QWidget()
        self.btn_spacer.setFixedWidth(2)

    def _setup_layouts(self) -> None:
        """
        Internal method. Sets up all the layouts on this screen, adding widgets and controlling alignment, spacing,
        and stretching. The main layout is also applied as this screen's primary layout via `setLayout()`.

        Returns:
            None.
        """
        # Title form field
        title_hbox = QHBoxLayout()
        title_hbox.addWidget(self.title_lbl)
        title_hbox.addSpacing(25)
        title_hbox.addWidget(self.title_counter)

        # Buttons column
        btn_hbox = QHBoxLayout()
        btn_hbox.addWidget(self.return_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        btn_hbox.addStretch()
        btn_hbox.addWidget(self.create_btn, alignment=Qt.AlignmentFlag.AlignRight)
        btn_hbox.addWidget(self.btn_spacer)
        btn_hbox.addWidget(self.save_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        # Ensures entire screen contents does not exceed 1000px width
        vbox_wrapper = QWidget()
        vbox_wrapper.setMaximumWidth(1000)

        # Adds 1:2 ratio for contents to align with brain's perceived center
        # rather than actual geometric center
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

        # HBox wrapper to ensure contents don't get too wide and stay at certain ratio
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(vbox_wrapper, stretch=6)
        hbox.addStretch(1)

        self.setLayout(hbox)

    def create_mode(self) -> None:
        """
        Sets the screen to Create mode. This is intended to be run when the screen is shown.

        The fields are all reset, and only the Create and Return buttons are shown (the Save button is hidden).
        The user is forced to open the quiz editor upon creation.

        Returns:
            None.
        """
        self.set_title("Quiz Master – Create New Quiz")

        self.title.setText("Enter new quiz details:")
        self.create_btn.setText("Create")

        # Hide buttons that are not needed for creation
        self.save_btn.hide()
        self.btn_spacer.hide()

        # Reset all form fields
        self.title_counter.line_edit.setText("")
        self.shuffle_check.setChecked(False)

    def edit_mode(self, quiz_title: str, do_shuffle: bool) -> None:
        """
        Sets the screen to Edit mode. This is intended to be run when the screen is shown.

        The fields are all set to the data as provided in the arguments, and the Save, Edit Questions, and
        Return buttons are shown. The user can either save and return to the quiz manager upon saving, or
        save and edit questions to go to the quiz editor upon saving.

        Arguments:
            quiz_title: The quiz title to pre-fill the input field with. A string is used as that is what the
                input field supports.

            do_shuffle: Whether or not to check the shuffle questions checkbox. A boolean is used as a checkbox
                is either in on or off state, which a boolean represents well.

        Returns:
            None.
        """
        self.set_title("Quiz Master – Edit Quiz")

        self.title.setText("Edit quiz details:")
        self.create_btn.setText("Edit Questions")

        # Show buttons that are exclusive to editing
        self.save_btn.show()
        self.btn_spacer.show()

        # Prefill all form fields from existing quiz
        self.title_counter.line_edit.setText(quiz_title)
        self.shuffle_check.setChecked(do_shuffle)

    def get_data_entered(self) -> dict[str, str | bool]:
        """
        Get all data entered from the form, identified by a `quiz_id` property.

        Data returned:
        - quiz_id: The quiz ID of the quiz that was edited, or None if this is a new quiz.
        - quiz_title: The quiz title entered by the user. The text is stripped of leading and trailing whitespace.
        - do_shuffle: A boolean representing whether or not the user wishes to shuffle questions.

        Returns:
            A dictionary with the data entered by the user, identified by a `quiz_id` that is a string when in edit
            mode, or None if in create mode. The values in the dictionary are documented above. A dictionary
            is used as it provides simple identifiable key-value pairs for each value entered.
        """
        return {
            "quiz_id": self.quiz_id,
            "quiz_title": self.title_counter.line_edit.text().strip(),
            "do_shuffle": self.shuffle_check.isChecked(),
        }

    def validate_data(self, data: dict) -> bool:
        """
        Validate the data given, showing an error message box if the data does not fulfill the requirements.
        The data is expected to be given directly from `get_data_entered()`.

        Arguments:
            data: A dictionary with all the data entered by the user. The dictionary is expected to follow the same
                structure as the data provided from `get_data_entered()`. A dictionary is used as it provides multiple
                values in a single argument for multiple data fields provided by the user.

        Returns:
            A boolean identifying if validation passed or failed. Returns True if validation passed, else, returns
            False. A boolean is used as it allows for simple boolean logic checks for if validation passed or failed.
        """
        title = data["quiz_title"]

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

        # All tests passed
        return True

    def _on_save(self) -> None:
        """
        Internal method. Intended to be called upon pressing the Save and Return button in Edit mode. This should
        not be called in Create mode, however, if it is called, the quiz is not saved, only validated.

        This method validates the data, and if the quiz ID is provided, saves the data, but does not open the
        quiz editor.

        Returns:
            None.
        """
        data = self.get_data_entered()

        # Automatically shows error modal boxes as well
        if not self.validate_data(data):
            return

        # If quiz already exists, save data but do not show quiz editor
        if self.quiz_id is not None:
            self.save_requested.emit(data, False)

    def _on_create(self) -> None:
        """
        Internal method. Intended to be called upon pressing the Create button in Create mode or the Edit Questions
        button in Edit mode.

        This method validates the data, saves the quiz, and opens the quiz editor.

        Returns:
            None.
        """
        data = self.get_data_entered()

        # Automatically shows error modal boxes as well
        if not self.validate_data(data):
            return

        # Save data and open quiz editor
        self.save_requested.emit(data, True)

    def _on_enter_pressed(self) -> None:
        """
        Internal method. Intended to be called upon pressing the Enter key on an input field. Runs a different
        method depending on the mode the screen is in (Create or Edit mode).

        The Enter key on the input field(s) do different actions depending on the mode.
        - Create mode: Saves quiz data and opens quiz editor.
        - Edit mode: Saves quiz data but does not open the editor; instead it returns to the quiz manager.

        Returns:
            None.
        """
        if self.quiz_id is None:
            # Open quiz editor in Create mode
            self._on_create()
        else:
            # Return to quiz manager in Edit mode
            self._on_save()

    def on_enter(self, payload: dict | None = None) -> None:
        if payload is None:
            # If no payload is provided, assume Create mode
            self.quiz_id = None
            self.create_mode()
            return

        # Get the quiz ID, if provided
        self.quiz_id = payload.get("quiz_id")

        if self.quiz_id is None:
            # If quiz ID is not provided, assume Create mode
            self.create_mode()
        else:
            # If quiz ID was provided, get rest of data and assume Edit mode
            self.edit_mode(payload["quiz_title"], payload["do_shuffle"])
