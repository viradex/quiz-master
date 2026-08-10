"""
question_editor.py

The question editor child screen (or component). Allows editing a single question.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QRadioButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from core.app.enums import QuestionValidationError
from core.config.constants import MAX_ANSWER_LENGTH, MAX_QUESTION_LENGTH
from models.payloads import QuestionPayload
from models.question import Question
from ui.components.button import create_tool_icon_button
from ui.components.dialog import confirm_warning
from ui.components.input import CharacterCountLineEdit, ClickableLabel, ReversedSpinBox
from utils.error_messages import QUESTION_ERROR_MESSAGES, format_errors
from utils.paths import get_icons_dir

# The warning to show on tooltips if the quiz is in read-only mode
READ_ONLY_WARNING = "Cannot edit read-only quiz"

# Contains data about each answer
ANSWER_DATA: list[dict[str, str | bool]] = [
    {"color": "#C94F4F", "letter": "A", "required": True},
    {"color": "#4A78C2", "letter": "B", "required": True},
    {"color": "#B89B2E", "letter": "C", "required": False},
    {"color": "#3E9B68", "letter": "D", "required": False},
]

# Contains every available time limit a question can be set to
TIME_DATA: dict[int, str] = {
    5: "5 seconds",
    10: "10 seconds",
    15: "15 seconds",
    20: "20 seconds",
    30: "30 seconds",
    45: "45 seconds",
    60: "1 minute",
    90: "1 minute 30 seconds",
    120: "2 minutes",
}


class QuestionEditor(QWidget):
    """
    Creates the question editor component, which acts as a child screen, for editing a single Question.
    Allows editing data about a single Question, previewing the question, and sending requests for actions
    the user requests that requires a higher level of quiz-level modification rather than just relating to
    this one question. Inherits `QWidget`.

    Attributes:
        error_results: A `pyqtSignal` that emits when the question has errors or not, when leaving the
            screen, so that the editor can inform the user that this question has errors. The Question that
            has errors for identification is provided, as well as a boolean that describes whether there
            are errors or not (True if there are errors, else False), are both provided as arguments.

        question_reordered: A `pyqtSignal` that emits when the user wishes to reorder this question. The
            Question to reorder and the new question index to move to as an integer are both provided as
            arguments.

        question_text_changed: A `pyqtSignal` that emits when the question text has been modified. The
            Question that had its text changed is provided as an argument, both as identification and
            also to show the new text, as the text is stored on the Question itself, preventing the need
            for separate arguments.

        global_time_requested: A `pyqtSignal` that emits when the user requests the time of this question
            to be applied to all questions currently in the quiz. The new time, in seconds as an integer
            (as integers represent seconds well without a need for floating-point precision), and the
            user-friendly display time are both provided as arguments.

        preview_requested: A `pyqtSignal` that emits when the user requests a preview of this question.
            A payload of the question data is given as a QuestionPayload, with all the necessary data needed
            for a preview, as an argument.

        duplicate_requested: A `pyqtSignal` that emits when the user requests this question to be duplicated.
            This question is provided as an argument to provide the data needed to make a copy of this question.

        delete_requested: A `pyqtSignal` that emits when the user requests this question to be deleted. The
            question is provided as an argument to provide identification for this question through the ID,
            which is more stable than extracting and sending the ID, in case extra information is needed.

    Arguments:
        question: The Question to base this editor off of. When initializing this class, the data from the
            question provided is used to populate the fields of the screen, if there is any provided. If
            it is an empty question, no fields are populated. This Question is mutated when updating values
            via the editor.

        question_num: The question number of this current question that this editor represents. An integer
            is used as the question number is used for calculations, and for other methods that require an
            integer.

        total_questions: The total number of questions in the current quiz, including this question. An integer
            is used as the total questions number is used for calculations, and other methods that require
            an integer.

        read_only: Whether or not the question, or quiz as a whole, is read-only. When the question is read-only,
            no fields can be updated and can only be viewed. All action buttons are also disabled, except for
            previewing. When True, the question cannot be edited. When False, the editor functions as normal.

        parent: The parent to make this editor a child of, or None to set no parent. Defaults to None.
    """

    error_results = pyqtSignal(Question, bool)

    question_reordered = pyqtSignal(Question, int)
    question_text_changed = pyqtSignal(Question)

    # New time (secs) and display name for time
    global_time_requested = pyqtSignal(int, str)
    preview_requested = pyqtSignal(QuestionPayload)
    duplicate_requested = pyqtSignal(Question)
    delete_requested = pyqtSignal(Question)

    def __init__(
        self,
        question: Question,
        question_num: int,
        total_questions: int,
        read_only: bool,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.question: Question = question
        self.question_num: int = question_num
        self.total_questions: int = total_questions
        self.read_only: bool = read_only

        # Stores issues with the questions, if any
        self.question_validation_errors: set[QuestionValidationError] = set()

        # Whether this is the first time viewing this component
        self.is_first: bool = True

        self._setup_component()

    def _setup_component(self) -> None:
        """
        Internal method. Sets up the component UI for the first time. This method should only be called once,
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
        self.question_num_font = QFont()
        self.question_num_font.setPointSize(18)

        self.answer_input_font = QFont()
        self.answer_input_font.setPointSize(14)

        self.extra_data_font = QFont()
        self.extra_data_font.setPointSize(14)

    def _setup_widgets(self) -> None:
        """
        Internal method. Sets up all widgets used by the screen, including styling and slots, if needed. Some
        widgets are added to global layouts, especially widgets that are created dynamically, such as the
        answer inputs.

        Returns:
            None.
        """
        self._setup_header_widgets()
        self._setup_question_input_widget()
        self._setup_answer_input_widgets()
        self._setup_correct_answer_widgets()
        self._setup_time_widgets()

    def _setup_header_widgets(self) -> None:
        """
        Internal method. Sets up all widgets related to the header, including styling and slots, if needed.
        These widgets are not added to any global layout in this method, however. The widgets created here
        include the question number, and any and all action/toolbar buttons.

        Returns:
            None.
        """
        # Add a space at the end for spacing between the static text and question number
        self.question_num_lbl = QLabel("Question ")
        self.question_num_lbl.setFont(self.question_num_font)

        # Using a spinbox to allow moving the question position. A reversed spinbox
        # is used to make moving it more natural, to reflect what the user sees on
        # the sidebar, where making the number larger would move the question down,
        # and vice versa. Making the keys match that makes the experience more natural.
        self.question_num_input = ReversedSpinBox()
        self.question_num_input.setToolTip(
            "Move question position" if not self.read_only else READ_ONLY_WARNING
        )
        self.question_num_input.setValue(self.question_num)
        self.question_num_input.setMinimum(1)
        self.question_num_input.setMaximum(self.total_questions)
        self.question_num_input.setFont(self.question_num_font)
        self.question_num_input.valueChanged.connect(self._on_question_reorder)

        # Make spinbox disabled if in read-only mode
        self.question_num_input.setDisabled(self.read_only)

        # Do not show any buttons to ensure there is less space between this
        # and total questions for easier readability.
        self.question_num_input.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)

        # Show total questions at end, completing the sentence 'Question [1] / 2', for example
        self.total_question_lbl = QLabel(f"/ {self.total_questions}")
        self.total_question_lbl.setFont(self.question_num_font)

        # Create all icons for tool buttons
        warning_icon = get_icons_dir() / "exclamation.png"
        preview_icon = get_icons_dir() / "preview.png"
        duplicate_icon = get_icons_dir() / "duplicate.png"
        delete_icon = get_icons_dir() / "delete.png"

        # Shown if there are errors in the question
        self.issues_btn = create_tool_icon_button(
            warning_icon,
            "This question has issues. Click to learn more.",
            icon_size=28,
            parent=self,
        )

        # Hidden by default
        self.issues_btn.hide()
        self.issues_btn.clicked.connect(self._show_issues)

        # Used to preview the question
        self.preview_btn = create_tool_icon_button(
            preview_icon, "Preview", icon_size=28
        )
        self.preview_btn.clicked.connect(self._on_preview_clicked)

        # Used to duplicate the question in the quiz
        self.duplicate_btn = create_tool_icon_button(
            duplicate_icon, "Duplicate", icon_size=28
        )
        self.duplicate_btn.clicked.connect(
            lambda: self.duplicate_requested.emit(self.question)
        )

        # Delete the question from the quiz
        self.delete_btn = create_tool_icon_button(delete_icon, "Delete", icon_size=28)
        self.delete_btn.clicked.connect(self._on_delete_clicked)

        # If read-only, disable editing-related buttons by showing different
        # grayed-out icons and disabling them.
        if self.read_only:
            duplicate_disabled_icon = get_icons_dir() / "duplicate_disabled.png"
            self.duplicate_btn.setIcon(QIcon(str(duplicate_disabled_icon)))

            delete_disabled_icon = get_icons_dir() / "delete_disabled.png"
            self.delete_btn.setIcon(QIcon(str(delete_disabled_icon)))

            self.duplicate_btn.setDisabled(True)
            self.duplicate_btn.setToolTip(READ_ONLY_WARNING)

            self.delete_btn.setDisabled(True)
            self.delete_btn.setToolTip(READ_ONLY_WARNING)

    def _setup_question_input_widget(self) -> None:
        """
        Internal method. Sets up the question input field widget, including styling and slots. This widget is
        not added to any global layout in this method, however.

        Returns:
            None.
        """
        # Use a CharacterCountLineEdit to provide visual feedback when surpassing the limit
        self.question_input = CharacterCountLineEdit(MAX_QUESTION_LENGTH)
        self.question_input.line_edit.setPlaceholderText("Enter question...")
        self.question_input.line_edit.setFixedHeight(60)
        self.question_input.line_edit.textChanged.connect(self._on_question_edit)

        # Prefills text if editing existing quiz
        self.question_input.line_edit.setText(self.question.question_text)

        # Make line edit disabled if in read-only mode
        self.question_input.line_edit.setDisabled(self.read_only)

        # Add more padding on the top to ensure the text does not overlap with the character count
        self.question_input.line_edit.setStyleSheet(
            "font-size: 22px;" "padding: 12px 8px 8px 8px;"
        )

    def _setup_answer_input_widgets(self) -> None:
        """
        Internal method. Sets up all widgets related to the answer input fields, including styling and slots,
        if needed. These widgets are dynamically added to a grid layout that contains the answer buttons.

        Returns:
            None.
        """
        # Answer button grid, where the inputs are added dynamically
        self.btn_grid = QGridLayout()
        self.btn_grid.setSpacing(15)

        # Store all answer inputs
        self.answer_inputs: list[CharacterCountLineEdit] = []

        # Dynamically create grid of answer inputs
        for i in range(2):
            for j in range(2):
                # Converts a 2D grid coordinate into a 1D flat list index
                index = i * 2 + j

                # Get answer button data
                data = ANSWER_DATA[index]

                # Get the answer text to prefill if it is already set in the
                # question data, or empty string for a new question.
                answer_text = (
                    self.question.answer_options[index]
                    if index < len(self.question.answer_options)
                    else ""
                )

                # Use a CharacterCountLineEdit to provide visual feedback when surpassing the limit
                answer_input = CharacterCountLineEdit(MAX_ANSWER_LENGTH)
                answer_input.line_edit.setText(answer_text)
                answer_input.line_edit.setFixedHeight(60)
                answer_input.line_edit.setFont(self.answer_input_font)

                # Sets the placeholder to contain the letter, and then suffixed with 'optional' if
                # the field is not required to be filled in. For example: "Answer 'A'" or "Answer 'D' (optional)".
                answer_input.line_edit.setPlaceholderText(
                    f"Answer '{data['letter']}' {'(optional)' if not data['required'] else ''}"
                )

                # Set answer input disabled if in read-only mode
                answer_input.line_edit.setDisabled(self.read_only)

                # The index=index is required, otherwise index passed will be statically set to 3
                answer_input.line_edit.textChanged.connect(
                    lambda text, index=index: self._on_answer_edit(index, text)
                )
                answer_input.line_edit.setStyleSheet(f"""
                    QLineEdit {{
                        border: 2px solid {data["color"]};
                        border-radius: 10px;
                        padding: 8px;
                    }}
                """)

                if self.read_only:
                    answer_input.setToolTip(READ_ONLY_WARNING)

                # Add input to list to store it globally, and dynamically to grid layout
                self.answer_inputs.append(answer_input)
                self.btn_grid.addWidget(answer_input, i, j)

    def _setup_correct_answer_widgets(self) -> None:
        """
        Internal method. Sets up all widgets related to the correct answer input fields, including styling
        and slots, if needed. These widgets are dynamically added to a layout that contains the correct answer
        radio buttons.

        Returns:
            None.
        """
        # Change label depending on if it is read-only or not
        self.correct_answer_lbl = QLabel(
            "Correct answer:" if self.read_only else "Select correct answer:"
        )
        self.correct_answer_lbl.setFont(self.extra_data_font)

        # Make a button group to ensure radio buttons can only be selected exclusively (one at a time)
        self.correct_group = QButtonGroup()
        self.correct_group.idToggled.connect(self._on_correct_answer_changed)

        # Vbox to add radio buttons to dynamically
        self.correct_answer_vbox = QVBoxLayout()
        self.correct_answer_vbox.setContentsMargins(20, 0, 0, 0)
        self.correct_answer_vbox.addWidget(self.correct_answer_lbl)
        self.correct_answer_vbox.addSpacing(10)

        self.correct_radios = []

        # Dynamically create radio buttons
        for i in range(4):
            # Get data relating to its respective answer
            data = ANSWER_DATA[i]

            # Set default text to answer letter
            correct_radio = QRadioButton(f"Answer '{data['letter']}'")
            correct_radio.setStyleSheet(f"""
                QRadioButton {{
                    font-size: 18px; font-weight: 600; color: {data['color']};
                }}                  
            """)

            # Set answer radio button disabled if in read-only mode
            correct_radio.setDisabled(self.read_only)

            if self.read_only:
                self.setToolTip(READ_ONLY_WARNING)

            # Add button to the group with its ID set to the index 0-3, and store it in list
            self.correct_group.addButton(correct_radio, i)
            self.correct_radios.append(correct_radio)

            # Dynamically add to vbox
            self.correct_answer_vbox.addWidget(correct_radio)
            self.correct_answer_vbox.addSpacing(5)

        # Enable/disable last two radio buttons if needed, for example if viewing a pre-existing quiz
        self._update_correct_answer_buttons()

        # Change radio button text to answer text, if needed, for example if viewing a pre-existing quiz
        for i, answer in enumerate(self.question.answer_options):
            self._on_answer_edit(i, answer)

        # Set correct answer set to a radio button if editing pre-existing quiz
        if self.question.correct_answer_index is not None:
            self.correct_group.button(self.question.correct_answer_index).setChecked(
                True
            )

        # Ensure radio buttons do not add their own spacing between each other
        self.correct_answer_vbox.addStretch()

    def _setup_time_widgets(self) -> None:
        """
        Internal method. Sets up all widgets related to the time limit, including styling and slots, if needed.
        These widgets are not added to any global layout in this method, however.

        Returns:
            None.
        """
        # Change label depending on if it is read-only or not
        self.time_lbl = QLabel("Time limit:" if self.read_only else "Set time limit:")
        self.time_lbl.setFont(self.extra_data_font)

        # Selection combobox to select fixed time limits
        self.time_combo = QComboBox()
        self.time_combo.setFixedSize(250, 40)
        self.time_combo.setEditable(False)
        self.time_combo.setFont(self.extra_data_font)

        # Set combobox disabled if in read-only mode
        self.time_combo.setDisabled(self.read_only)

        # Add all default values, with display value and hidden internal
        # data attached (seconds as an integer).
        for seconds, value in TIME_DATA.items():
            self.time_combo.addItem(value, seconds)

        # Pre-set the time limit (the question should always have a time limit, even if brand-new)
        self.set_time_limit(self.question.time_limit)
        self.time_combo.currentIndexChanged.connect(self._on_time_changed)

        # Label that allows applying current time limit to all questions (hidden in read-only mode)
        self.apply_global_time = ClickableLabel("Apply to all questions", self)
        self.apply_global_time.clicked.connect(self._on_apply_global_time)
        self.apply_global_time.setHidden(self.read_only)
        self.apply_global_time.setStyleSheet(
            "font-size: 14px;" "text-decoration: underline;" "color: #9a9a9a;"
        )

    def _setup_layouts(self) -> None:
        """
        Internal method. Sets up all the layouts on this screen, adding widgets and controlling alignment, spacing,
        and stretching. The main layout is also applied as this screen's primary layout via `setLayout()`.

        Returns:
            None.
        """
        # Heading, containing question number and action buttons. Question number
        # and issues button are on the left, and the other action buttons are on the left.
        heading_hbox = QHBoxLayout()
        heading_hbox.addWidget(self.question_num_lbl)
        heading_hbox.addWidget(self.question_num_input)
        heading_hbox.addWidget(self.total_question_lbl)
        heading_hbox.addSpacing(5)
        heading_hbox.addWidget(self.issues_btn)
        heading_hbox.addStretch()
        heading_hbox.addWidget(self.preview_btn)
        heading_hbox.addSpacing(10)
        heading_hbox.addWidget(self.duplicate_btn)
        heading_hbox.addSpacing(10)
        heading_hbox.addWidget(self.delete_btn)
        heading_hbox.addSpacing(5)

        # Adds all time-related widgets together
        time_vbox = QVBoxLayout()
        time_vbox.setContentsMargins(20, 0, 0, 0)
        time_vbox.addWidget(self.time_lbl)
        time_vbox.addSpacing(10)
        time_vbox.addWidget(self.time_combo)
        time_vbox.addSpacing(15)
        time_vbox.addWidget(self.apply_global_time)
        time_vbox.addStretch()

        # Adds correct answer and time selection side-by-side
        extra_grid = QGridLayout()
        extra_grid.addLayout(self.correct_answer_vbox, 0, 0)
        extra_grid.addLayout(time_vbox, 0, 1, alignment=Qt.AlignmentFlag.AlignLeft)

        # Primary layout
        vbox = QVBoxLayout()
        vbox.setContentsMargins(40, 40, 40, 20)
        vbox.addStretch(1)
        vbox.addLayout(heading_hbox)
        vbox.addSpacing(20)
        vbox.addWidget(self.question_input)
        vbox.addSpacing(40)
        vbox.addLayout(self.btn_grid)
        vbox.addSpacing(40)
        vbox.addLayout(extra_grid)
        vbox.addStretch(2)

        self.setLayout(vbox)

    def update_question_number(
        self, question_num: int, total_questions: int | None = None
    ) -> None:
        """
        Update the question number on the UI, as well as changing the values stored internally. Updates the
        value in the question number spinbox, and the total questions label. Also, changes the maximum value
        of the spinbox to match the number of total questions.

        Arguments:
            question_num: The question number of this current question that this editor represents. An integer
                is used as the question number is used for calculations, and for other methods that require an
                integer.

            total_questions: The total number of questions in the current quiz, including this question. An integer
                is used as the total questions number is used for calculations, and other methods that require
                an integer. If None is provided, the current number of total questions is assumed and not changed.
                Defaults to None.

        Returns:
            None.
        """
        # Update question number and total questions, if provided
        self.question_num = question_num
        if total_questions is not None:
            self.total_questions = total_questions

        # Change values and text, and update max of spinbox
        self.question_num_input.setValue(self.question_num)
        self.question_num_input.setMaximum(self.total_questions)
        self.total_question_lbl.setText(f"/ {self.total_questions}")

    def disable_delete(self, reason: str = "Cannot delete question") -> None:
        """
        Disable the delete button, with a specified reason. Changes the icon to be grayed out, and prevents
        the button from being clicked, with the tooltip describing the reason. This method only runs if the
        question is not in read-only mode.

        Arguments:
            reason: The reason for the button being disabled, as a string. This text will appear as a tooltip
                when hovering over the button. A string is used as it can easily display many characters. Defaults
                to "Cannot delete question" when the argument is not explicitly specified.

        Returns:
            None.
        """
        # Do not disable if read-only to avoid overwriting the existing tooltip
        if not self.read_only:
            # Change icon to a grayed-out version
            delete_disabled_icon = get_icons_dir() / "delete_disabled.png"
            self.delete_btn.setIcon(QIcon(str(delete_disabled_icon)))

            self.delete_btn.setToolTip(reason)
            self.delete_btn.setDisabled(True)

    def enable_delete(self) -> None:
        """
        Enable the delete button. Changes the icon to be its regular color, and allows the button to being
        clicked. This method only runs if the question is not in read-only mode.

        Returns:
            None.
        """
        # Do not enable if read-only as read-only strictly denies deletion
        if not self.read_only:
            # Change icon to the regular version
            delete_icon = get_icons_dir() / "delete.png"
            self.delete_btn.setIcon(QIcon(str(delete_icon)))

            self.delete_btn.setToolTip("Delete")
            self.delete_btn.setEnabled(True)

    def set_time_limit(self, seconds: int) -> None:
        """
        Sets the time limit in the dropdown, and also modifies the time limit data of the question to reflect
        the new time limit passed in.

        Arguments:
            seconds: The number of seconds to change the dropdown to, and to change the time limit stored in
                the question to. The value must exist in `TIME_DATA`. An integer is used as it matches the data
                stored in the constant and dropdown.

        Returns:
            None.

        Raises:
            ValueError: If the time limit is invalid, meaning it does not exist in `TIME_DATA` nor does it exist
                in the dropdown.
        """
        index = self.time_combo.findData(seconds)

        # Could not find time limit
        if index == -1:
            raise ValueError(f"Invalid time limit: {seconds}")

        # Set combobox and question data
        self.time_combo.setCurrentIndex(index)
        self.question.time_limit = seconds

        self.validate_question()

    def validate_question(self) -> None:
        """
        Validate this question for question-specific errors. If errors are found, the preview button will be
        disabled until there are no more errors. However, certain errors will be ignored when determining
        whether or not to disable the preview button.

        Ignored error(s) when disabling preview button:
        - `NO_CORRECT_ANSWER`

        If this is the first time this editor is shown, the warning icon will not be shown. Otherwise, when there
        are errors, the warning icon is shown, which can be clicked to gain further user-friendly information
        for why this question has errors.

        Returns:
            None.
        """
        self.question_validation_errors = self.question.validate_question()

        # Preview button will be disabled regardless of first time. The correct
        # answer is not needed to preview the question, hence it is ignored when
        # determining whether or not it is suitable to enable/disable the preview button.
        if self.question_validation_errors - {
            QuestionValidationError.NO_CORRECT_ANSWER
        }:
            # Change icon to the grayed-out version to signify it being disabled visually
            preview_disabled_icon = get_icons_dir() / "preview_disabled.png"
            self.preview_btn.setIcon(QIcon(str(preview_disabled_icon)))

            self.preview_btn.setToolTip("Finish question before previewing")
            self.preview_btn.setDisabled(True)
        else:
            # Change icon to the regular version
            preview_icon = get_icons_dir() / "preview.png"
            self.preview_btn.setIcon(QIcon(str(preview_icon)))

            self.preview_btn.setToolTip("Preview")
            self.preview_btn.setDisabled(False)

        # Do not show warning icon if this screen is shown for the first time
        if self.is_first:
            return

        # Show issues button if there are errors to help user identify them
        if self.question_validation_errors:
            self.issues_btn.show()
        else:
            self.issues_btn.hide()

    def _show_issues(self) -> None:
        """
        Internal method. If there are any validation issues with the question, shows them in a warning modal
        box formatted into a user-friendly list. Re-validates the question before showing warnings.

        Returns:
            None.
        """
        # Validate question in case errors are out-of-date
        self.validate_question()

        if not self.question_validation_errors:
            # This should ordinarily never happen
            QMessageBox.information(
                self,
                "No Issues Detected",
                "No issues were detected with this question.",
            )
            self.issues_btn.hide()
            return

        # Store error messages
        issues: list[str] = []

        # Iterate over dict to preserve order in UI, as sets do not preserve order
        for error in QUESTION_ERROR_MESSAGES:
            if error in self.question_validation_errors:
                issues.append(QUESTION_ERROR_MESSAGES[error])

        # Show errors in a list-like format
        QMessageBox.warning(
            self,
            "Question Issues",
            f"The following issue(s) were detected in this question. These must be fixed before the quiz can be played.\n\n{format_errors(issues)}",
        )

    def _on_preview_clicked(self) -> None:
        """
        Internal method. Intended to be run when the Preview button is clicked. Emits a signal containing a
        QuestionPayload so the multi-question screen knows how to display the question.

        Only works if there are no validation errors, except for the following:
        - `NO_CORRECT_ANSWER`

        Returns:
            None.
        """
        # Correct answer is not needed to preview a question
        if self.question_validation_errors - {
            QuestionValidationError.NO_CORRECT_ANSWER
        }:
            # This should ordinarily never happen
            QMessageBox.critical(
                self,
                "Question is Invalid",
                "Cannot preview a question when there are validation errors.",
            )
            return

        # Temporarily remove blank questions (should only ever remove C and/or D due to validation)
        answers = self.question.remove_empty_answers(mutate_answers=False)

        # Create a payload to inform the ClientMultiQuestionScreen how to display the question
        question_payload = QuestionPayload(
            self.question_num,
            self.total_questions,
            self.question.question_text,
            answers,
            self.question.time_limit,
            is_preview=True,
            read_only_quiz=self.read_only,
        )
        self.preview_requested.emit(question_payload)

    def _on_delete_clicked(self) -> None:
        """
        Internal method. Intended to be run when the Delete button is clicked. If the question is in read-only
        mode, nothing happens. Otherwise, a confirmation prompt is shown for deleting the current question
        before emitting a signal to delete this question if the user accepts.

        Returns:
            None.
        """
        # If this method is somehow run while in read-only mode, prevent it here
        if self.read_only:
            return

        confirm = confirm_warning(
            self,
            "Confirm Deleting Question",
            "Are you sure you want to delete this question? This action is irreversible!",
        )

        if confirm:
            self.delete_requested.emit(self.question)

    def _on_apply_global_time(self) -> None:
        """
        Internal method. Intended to be run when the user wishes to apply the current time set on this question
        to every question in the quiz. If the question is in read-only mode, nothing happens. Otherwise, the
        current selected data is retrieved from the dropdown before emitting a signal requesting the time to be
        set to all questions.

        This method does not show the confirmation prompt for applying the time to all questions.

        Returns:
            None.
        """
        # If this method is somehow run while in read-only mode, prevent it here
        if self.read_only:
            return

        # Get seconds stored in internal data and text
        seconds = self.time_combo.currentData()
        text = self.time_combo.currentText()

        self.global_time_requested.emit(seconds, text)

    def _on_question_reorder(self, new_question_num: int) -> None:
        """
        Internal method. Intended to be called when the question number is changed by using the spin box input.
        If the question is not in read-only mode, and the new question number is within a valid range of 1 to the
        total number of questions, inclusive, a signal is emitted detailing the new question number that this
        question should be changed to.

        Arguments:
            new_question_num: The new question number of this current question. An integer is used as it remains
                the same type as the original question number, reducing inconsistencies.

        Returns:
            None.
        """
        # If this method is somehow run while in read-only mode, prevent it here
        if self.read_only:
            return

        # Ensures the new question range is within a valid range
        if not 0 < new_question_num <= self.total_questions:
            # This should ordinarily never happen
            QMessageBox.critical(
                self,
                "Invalid Question Number",
                f"The question cannot be moved to Question #{new_question_num} as it is out of range.",
            )
            return

        self.question_reordered.emit(self.question, new_question_num)

    def _on_question_edit(self, text: str) -> None:
        """
        Internal method. Intended to be called when the question input field has its text changed. If not in
        read-only mode, saves a stripped version of the question text to the stored Question object, and emits
        a signal informing that the question text has been changed. Also, validates the question.

        Arguments:
            text: The new question text that was entered. A string is used as it can represent a vast number of
                characters easily together.

        Returns:
            None.
        """
        # If this method is somehow run while in read-only mode, prevent it here
        if self.read_only:
            return

        # Save text to Question object
        self.question.question_text = text.strip()

        self.question_text_changed.emit(self.question)
        self.validate_question()

    def _on_answer_edit(self, index: int, text: str) -> None:
        """
        Internal method. Intended to be run when an answer input field is updated. Does not do anything when
        the question is in read-only mode. Otherwise, fills in all answers before the index with blank strings
        if needed to ensure the answer is not saved at the incorrect index, then saves a stripped version to
        the Question object. The question is then validated.

        After saving, the correct answer radio buttons are updated to reflect the answer text in the radio
        button, enabling it if necessary. If the answer was cleared, the radio button text is reset.

        Arguments:
            index: The index of the answer that was edited, from 0-3, respective to an answer input field. An
                integer is used as it is used for indexing.

            text: The new answer text that was entered. A string is used as it can represent a vast number of
                characters easily together.

        Returns:
            None.
        """
        # If this method is somehow run while in read-only mode, prevent it here
        if self.read_only:
            return

        text = text.strip()

        # If there are less answers than the index, adds blank strings before
        # inserting the answer to prevent it from being saved at the wrong position.
        while len(self.question.answer_options) <= index:
            self.question.answer_options.append("")

        # Save to Question object
        self.question.answer_options[index] = text

        # Retrieves correct answer radio button respective to the input field
        answer_radio = self.correct_group.button(index)

        # Changes respective radio button text to reflect answer text, if not empty.
        # Otherwise, resets it to its default state.
        if answer_radio is not None:
            if text:
                answer_radio.setText(text)
            else:
                data = ANSWER_DATA[index]
                answer_radio.setText(f"Answer '{data['letter']}'")

        # Update the state of the radio buttons
        self._update_correct_answer_buttons()
        self.validate_question()

    def _on_correct_answer_changed(self, index: int) -> None:
        """
        Internal method. Intended to be run when a different correct answer radio button is selected. If the
        question is in read-only mode, nothing is saved. Otherwise, the new correct answer is saved in the
        Question object and the question is validated.

        Arguments:
            index: The index of the correct answer radio button that was selected, from 0-3. An integer is
                used as it is used for indexing.

        Returns:
            None.
        """
        # If this method is somehow run while in read-only mode, prevent it here
        if self.read_only:
            return

        # Saves correct answer to the Question object
        self.question.correct_answer_index = index
        self.validate_question()

    def _on_time_changed(self, index: int) -> None:
        """
        Internal method. Intended to be run when the time dropdown has its selection changed. If the question
        is not in read-only mode, the selection is read and saved, and the question is validated (despite it
        not being required for the time currently).

        Arguments:
            index: The index of the new time that was selected in the dropdown. While this argument is unused,
                it is required as PyQt automatically passes in the argument when this method is called.

        Returns:
            None.
        """
        # If this method is somehow run while in read-only mode, prevent it here
        if self.read_only:
            return

        # Get seconds from hidden data connected to the selected value, then saves it
        seconds = self.time_combo.currentData()
        self.question.time_limit = seconds

        self.validate_question()

    def _update_correct_answer_buttons(self) -> None:
        """
        Internal method. Automatically updates the enabled/disabled states of the correct answer radio buttons.
        The first two radio buttons are always enabled, while the last two are only enabled if their respective
        answer fields have text. If one of the last two is selected and then the selected radio button has its
        text removed for it to become disabled, the selection is removed entirely and no radio button becomes
        selected (the Question object is also updated to reflect this).

        If in read-only mode, all buttons are always permanently disabled.

        Returns:
            None.
        """
        for i, radio in enumerate(self.correct_radios):
            # Checks if the respective answer input field has text
            has_text = bool(self.answer_inputs[i].line_edit.text().strip())

            # A and B are always enabled, unless in read-only mode
            if i < 2 and not self.read_only:
                radio.setEnabled(True)
            else:
                # Only enable if respective answer has text and not in read-only mode
                radio.setEnabled(has_text and not self.read_only)

                # If C or D was selected and is now disabled, unselect it
                if not has_text and radio.isChecked():
                    # Must set exclusive to False and then reset it to ensure the radio button can be unchecked
                    self.correct_group.setExclusive(False)
                    radio.setChecked(False)
                    self.correct_group.setExclusive(True)

                    # Ensure the Question object reflects the fact that no answer is currently selected
                    self.question.correct_answer_index = None

    def on_enter(self, total_questions: int, is_first: bool) -> None:
        """
        Called automatically when this editor screen is shown. Updates the data in this component to reflect any
        changes made externally.

        Arguments:
            total_questions: The total number of questions in the current quiz, including this question. An integer
                is used as the total questions number is used for calculations, and other methods that require
                an integer.

            is_first: Whether or not this is the first time the screen has been shown, usually when this question
                has just been freshly created. A boolean is used as this is a yes/no answer, which a boolean
                represents well.

        Returns:
            None.
        """
        # Reflect any possible question number changes
        self.total_questions = total_questions
        self.update_question_number(self.question_num, self.total_questions)

        self.is_first = is_first
        self.validate_question()

    def on_leave(self) -> None:
        """
        Called automatically when this editor is hidden. Validates the question and emits a signal informing the
        parent whether or not this question has errors, to warn the user outside of this screen.

        Returns:
            None.
        """
        self.question_validation_errors = self.question.validate_question()

        # Informs parent if there are any errors in this question to show that to the user
        self.error_results.emit(self.question, bool(self.question_validation_errors))
