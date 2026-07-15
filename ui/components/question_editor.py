from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QRadioButton,
    QButtonGroup,
    QComboBox,
    QSpinBox,
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout,
    QMessageBox,
)

from core.app.enums import QuestionValidationError
from models.payloads import QuestionPayload
from models.question import Question
from ui.components.input import CharacterCountInput, ClickableLabel, ReversedSpinBox

from ui.components.button import create_tool_icon_button
from ui.components.dialogs import confirm_warning
from utils.error_messages import format_errors, QUESTION_ERROR_MESSAGES
from core.config.constants import MAX_ANSWER_LENGTH, MAX_QUESTION_LENGTH

ANSWER_DATA: list[dict[str, str | bool]] = [
    {"color": "#C94F4F", "letter": "A", "required": True},
    {"color": "#4A78C2", "letter": "B", "required": True},
    {"color": "#B89B2E", "letter": "C", "required": False},
    {"color": "#3E9B68", "letter": "D", "required": False},
]

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
    """Editor for a single question of a quiz."""

    # bool is for whether question has error
    error_results = pyqtSignal(Question, bool)

    question_reordered = pyqtSignal(Question, int)  # New question number
    question_text_changed = pyqtSignal(Question)

    # New time (secs) and display name for time
    global_time_requested = pyqtSignal(int, str)
    preview_requested = pyqtSignal(QuestionPayload)
    duplicate_requested = pyqtSignal(Question)
    delete_requested = pyqtSignal(Question)

    def __init__(
        self,
        question: Question,
        question_num: int | str,
        total_questions: int | str,
        read_only: bool,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.question = question
        self.question_num = question_num
        self.total_questions = total_questions
        self.read_only = read_only

        self.question_validation_results: set[QuestionValidationError] = set()
        self.is_first: bool = True

        self.base_dir = Path(__file__).resolve().parent.parent
        self.icons_path = self.base_dir / "assets" / "icons"

        self.setup_component()

    def setup_component(self) -> None:
        ## FONTS SETUP ##
        question_num_font = QFont()
        question_num_font.setPointSize(18)

        answer_input_font = QFont()
        answer_input_font.setPointSize(14)

        extra_data_font = QFont()
        extra_data_font.setPointSize(14)

        ## WIDGETS SETUP ##
        # Question nums and helper btns
        question_num_lbl = QLabel("Question ")
        question_num_lbl.setFont(question_num_font)

        # Spinbox to allow moving question
        # Reversed spinbox is more natural due to sidebar
        self.question_num_input = ReversedSpinBox()
        self.question_num_input.setToolTip(
            "Move question position"
            if not self.read_only
            else "Cannot edit read-only quiz"
        )
        self.question_num_input.setValue(int(self.question_num))
        self.question_num_input.setMinimum(1)
        self.question_num_input.setMaximum(int(self.total_questions))
        self.question_num_input.setDisabled(self.read_only)
        self.question_num_input.setFont(question_num_font)
        self.question_num_input.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.question_num_input.valueChanged.connect(self._on_question_reorder)

        self.total_question_lbl = QLabel(f"/ {self.total_questions}")
        self.total_question_lbl.setFont(question_num_font)

        warning_icon = self.icons_path / "exclamation.png"
        preview_icon = self.icons_path / "preview.png"
        duplicate_icon = self.icons_path / "duplicate.png"
        delete_icon = self.icons_path / "delete.png"

        self.issues_btn = create_tool_icon_button(
            warning_icon, "This question has issues. Click to learn more", icon_size=28
        )
        self.issues_btn.hide()  # Hidden by default
        self.issues_btn.clicked.connect(self._show_issues)

        self.preview_btn = create_tool_icon_button(
            preview_icon, "Preview", icon_size=28
        )
        self.preview_btn.clicked.connect(self._on_preview_clicked)

        self.duplicate_btn = create_tool_icon_button(
            duplicate_icon, "Duplicate", icon_size=28
        )
        self.duplicate_btn.clicked.connect(
            lambda: self.duplicate_requested.emit(self.question)
        )

        self.delete_btn = create_tool_icon_button(delete_icon, "Delete", icon_size=28)
        self.delete_btn.clicked.connect(self._on_delete_clicked)

        # If read-only, disable editing-related buttons
        if self.read_only:
            duplicate_disabled_icon = self.icons_path / "duplicate_disabled.png"
            self.duplicate_btn.setIcon(QIcon(str(duplicate_disabled_icon)))

            delete_disabled_icon = self.icons_path / "delete_disabled.png"
            self.delete_btn.setIcon(QIcon(str(delete_disabled_icon)))

            self.duplicate_btn.setDisabled(True)
            self.duplicate_btn.setToolTip("Cannot edit read-only quiz")

            self.delete_btn.setDisabled(True)
            self.delete_btn.setToolTip("Cannot edit read-only quiz")

        # Question input
        self.question_counter = CharacterCountInput(MAX_QUESTION_LENGTH)
        self.question_counter.line_edit.setText(self.question.question_text)
        self.question_counter.line_edit.setPlaceholderText("Enter question...")
        self.question_counter.line_edit.setDisabled(self.read_only)
        self.question_counter.line_edit.setFixedHeight(60)
        self.question_counter.line_edit.textChanged.connect(self._on_question_edit)
        self.question_counter.line_edit.setStyleSheet(
            "font-size: 22px;" "padding: 8px;" "padding-top: 12px;"
        )

        # Answer button grid
        btn_grid = QGridLayout()
        btn_grid.setSpacing(15)

        self.answer_counters = []

        # Dynamically create grid of answer buttons
        for i in range(2):
            for j in range(2):
                index = i * 2 + j
                data = ANSWER_DATA[index]

                answer_text = (
                    self.question.answer_options[index]
                    if index < len(self.question.answer_options)
                    else ""
                )

                counter = CharacterCountInput(MAX_ANSWER_LENGTH)
                counter.line_edit.setText(answer_text)
                counter.line_edit.setPlaceholderText(
                    f"Answer '{data['letter']}' {'(optional)' if not data['required'] else ''}"
                )
                counter.line_edit.setDisabled(self.read_only)
                counter.line_edit.setFixedHeight(60)
                counter.line_edit.setFont(answer_input_font)

                # index=index required, otherwise index passed will be statically set to 3
                counter.line_edit.textChanged.connect(
                    lambda text, index=index: self._on_answer_edit(index, text)
                )
                counter.line_edit.setStyleSheet(f"""
                    QLineEdit {{
                        border: 2px solid {data["color"]};
                        border-radius: 10px;
                        padding: 8px;
                    }}
                """)

                if self.read_only:
                    counter.setToolTip("Cannot edit read-only quiz")

                self.answer_counters.append(counter)
                btn_grid.addWidget(counter, i, j)

        # Correct answer selection
        correct_answer_lbl = QLabel("Select correct answer:")
        correct_answer_lbl.setFont(extra_data_font)

        self.correct_group = QButtonGroup()
        self.correct_group.idToggled.connect(self._on_correct_answer_changed)

        correct_answer_vbox = QVBoxLayout()
        correct_answer_vbox.setContentsMargins(20, 0, 0, 0)
        correct_answer_vbox.addWidget(correct_answer_lbl)
        correct_answer_vbox.addSpacing(10)

        self.correct_radios = []

        # Dynamically create radio buttons
        for i in range(4):
            data = ANSWER_DATA[i]

            correct_radio = QRadioButton(f"Answer '{data['letter']}'")
            correct_radio.setDisabled(self.read_only)
            correct_radio.setStyleSheet(f"""
                QRadioButton {{
                    font-size: 18px; font-weight: 600; color: {data['color']};
                }}                  
            """)

            if self.read_only:
                self.setToolTip("Cannot edit read-only quiz")

            self.correct_group.addButton(correct_radio, i)
            self.correct_radios.append(correct_radio)

            correct_answer_vbox.addWidget(correct_radio)
            correct_answer_vbox.addSpacing(5)

        # Enable/disable last two radio buttons if needed
        self._update_correct_answer_buttons()

        # Change radio button text to answer text, if needed
        for i, answer in enumerate(self.question.answer_options):
            self._on_answer_edit(i, answer)

        # Set correct answer set to a radio button if editing pre-existing quiz
        if self.question.correct_answer_index is not None:
            self.correct_group.button(self.question.correct_answer_index).setChecked(
                True
            )

        correct_answer_vbox.addStretch()

        # Time limit selection
        time_lbl = QLabel("Set time limit:")
        time_lbl.setFont(extra_data_font)

        self.time_combo = QComboBox()
        self.time_combo.setFixedSize(250, 40)
        self.time_combo.setEditable(False)
        self.time_combo.setDisabled(self.read_only)
        self.time_combo.setFont(extra_data_font)

        for seconds, value in TIME_DATA.items():
            self.time_combo.addItem(value, seconds)

        # Pre-set the time limit
        self.set_time_limit(self.question.time_limit)
        self.time_combo.currentIndexChanged.connect(self._on_time_changed)

        self.apply_global_time = ClickableLabel("Apply to all questions", self)
        self.apply_global_time.clicked.connect(self._on_apply_global_time)
        self.apply_global_time.setHidden(self.read_only)
        self.apply_global_time.setStyleSheet(
            "font-size: 14px;" "text-decoration: underline;" "color: #9A9A9A;"
        )

        ## LAYOUTS SETUP ##
        heading_hbox = QHBoxLayout()
        heading_hbox.addWidget(question_num_lbl)
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

        time_vbox = QVBoxLayout()
        time_vbox.setContentsMargins(20, 0, 0, 0)
        time_vbox.addWidget(time_lbl)
        time_vbox.addSpacing(10)
        time_vbox.addWidget(self.time_combo)
        time_vbox.addSpacing(15)
        time_vbox.addWidget(self.apply_global_time)
        time_vbox.addStretch()

        extra_grid = QGridLayout()
        extra_grid.addLayout(correct_answer_vbox, 0, 0)
        extra_grid.addLayout(time_vbox, 0, 1, alignment=Qt.AlignmentFlag.AlignLeft)

        vbox = QVBoxLayout()
        vbox.setContentsMargins(40, 40, 40, 20)
        vbox.addStretch(1)
        vbox.addLayout(heading_hbox)
        vbox.addSpacing(20)
        vbox.addWidget(self.question_counter)
        vbox.addSpacing(40)
        vbox.addLayout(btn_grid)
        vbox.addSpacing(40)
        vbox.addLayout(extra_grid)
        vbox.addStretch(2)

        self.setLayout(vbox)

    def update_question_num(
        self, question_num: int | str, total_questions: int | str | None = None
    ) -> None:
        """Update the question number spin box display, and the total questions if provided. If the total
        questions are not provided, assumes the previous value."""
        self.question_num = question_num
        if total_questions is not None:
            self.total_questions = total_questions

        self.question_num_input.setValue(int(self.question_num))
        self.question_num_input.setMaximum(int(self.total_questions))
        self.total_question_lbl.setText(f"/ {self.total_questions}")

    def disable_delete(self) -> None:
        """Disable the delete button (typically for if this question is the last remaining)."""
        if not self.read_only:
            delete_disabled_icon = self.icons_path / "delete_disabled.png"
            self.delete_btn.setIcon(QIcon(str(delete_disabled_icon)))

            # TODO This tooltip message should be customizable
            self.delete_btn.setToolTip("Cannot delete the only question")
            self.delete_btn.setDisabled(True)

    def enable_delete(self) -> None:
        """Enable the delete button."""
        if not self.read_only:
            delete_icon = self.icons_path / "delete.png"
            self.delete_btn.setIcon(QIcon(str(delete_icon)))
            self.delete_btn.setToolTip("Delete")
            self.delete_btn.setDisabled(False)

    def set_time_limit(self, seconds: int) -> None:
        """Set the time limit on the dropdown and within the question's internal data."""
        index = self.time_combo.findData(seconds)

        if index != -1:
            self.time_combo.setCurrentIndex(index)
            self.question.time_limit = seconds

        self.validate_question()

    def validate_question(self) -> None:
        """
        Validate the question for question-specific errors. If errors are found, with the exception
        of a few, the preview button will be enabled or disabled. If this is not the first time this editor
        is shown, the warning icon will be shown, which can be clicked to gain information for why this
        question has errors.
        """
        self.question_validation_results = self.question.validate_question()

        # Preview button will be disabled regardless of first time
        # Correct answer is not needed to preview
        if self.question_validation_results - {
            QuestionValidationError.NO_CORRECT_ANSWER
        }:
            preview_disabled_icon = self.icons_path / "preview_disabled.png"
            self.preview_btn.setIcon(QIcon(str(preview_disabled_icon)))
            self.preview_btn.setToolTip("Finish question before previewing")
            self.preview_btn.setDisabled(True)
        else:
            preview_icon = self.icons_path / "preview.png"
            self.preview_btn.setIcon(QIcon(str(preview_icon)))
            self.preview_btn.setToolTip("Preview")
            self.preview_btn.setDisabled(False)

        # Do not show warning icon if this screen is shown for the first time
        if self.is_first:
            return

        # Show issues button if there are errors to help user identify them
        if self.question_validation_results:
            self.issues_btn.show()
        else:
            self.issues_btn.hide()

    def _show_issues(self) -> None:
        """If there are validation issues, groups all errors in the question and displays
        them in a warning modal box as a user-friendly list."""
        self.validate_question()
        issues: list[str] = []

        if not self.question_validation_results:
            # Ordinarily this should never happen
            QMessageBox.information(
                self,
                "No Issues Detected",
                "No issues were detected with this question.",
            )
            self.issues_btn.hide()
            return

        # Iterate over dict to preserve order in UI, as sets do not preverse order
        for error in QUESTION_ERROR_MESSAGES:
            if error in self.question_validation_results:
                issues.append(QUESTION_ERROR_MESSAGES[error])

        # Show errors in a list-like format
        QMessageBox.warning(
            self,
            "Question Issues",
            f"The following issue(s) were detected in this question. These must be fixed before the quiz can be played.\n\n{format_errors(issues)}",
        )

    def _on_preview_clicked(self) -> None:
        """Emits a signal containing a QuestionPayload so the screen knows how to display the question.
        Only works if there are no validation errors, except for a select few."""
        # Correct answer is not needed to preview a question
        if self.question_validation_results - {
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
        answers = [a for a in self.question.answer_options if a.strip() != ""]

        question_payload = QuestionPayload(
            int(self.question_num),
            int(self.total_questions),
            self.question.question_text,
            answers,
            self.question.time_limit,
            is_preview=True,
        )
        self.preview_requested.emit(question_payload)

    def _on_delete_clicked(self) -> None:
        """Shows a confirmation prompt for deleting the current question before delegating it."""
        confirm = confirm_warning(
            self,
            "Confirm Deleting Question",
            "Are you sure you want to delete this question? This action is irreversable!",
        )

        if confirm:
            self.delete_requested.emit(self.question)

    def _on_apply_global_time(self) -> None:
        """Gets seconds requested before delegating it. Does not show the confirmation prompt."""
        seconds = self.time_combo.currentData()
        text = self.time_combo.currentText()

        self.global_time_requested.emit(seconds, text)

    def _on_question_reorder(self, new_question_num: int) -> None:
        """Request the reorder of this question, if it is within a valid range 1-total questions, inclusive."""
        if not 0 < new_question_num <= int(self.total_questions):
            # Should ordinarily never happen
            QMessageBox.critical(
                self,
                "Invalid Question Number",
                "The question cannot be moved to the requested value as it is out of range.",
            )
            return

        self.question_reordered.emit(self.question, new_question_num)

    def _on_question_edit(self, text: str) -> None:
        """Whenever the question text changes. Saves a stripped version of the text."""
        self.question.question_text = text.strip()

        self.question_text_changed.emit(self.question)
        self.validate_question()

    def _on_answer_edit(self, index: int, text: str) -> None:
        """Whenever an answer is edited. Saves a stripped version and updates the respective radio
        button with the answer text, enabling it if necessary. If the answer is cleared, resets the
        radio button text."""
        text = text.strip()

        # Fills in answers before the edited one with a blank string
        # to ensure the answer is not saved at the wrong index
        while len(self.question.answer_options) <= index:
            self.question.answer_options.append("")

        self.question.answer_options[index] = text
        answer_radio = self.correct_group.button(index)

        # Changes respective radio button text to reflect answer text, if not empty
        if answer_radio is not None:
            if text:
                answer_radio.setText(text)
            else:
                data = ANSWER_DATA[index]
                answer_radio.setText(f"Answer '{data['letter']}'")

        self._update_correct_answer_buttons()
        self.validate_question()

    def _on_correct_answer_changed(self, index: int) -> None:
        """Whenever a different correct answer radio button is selected."""
        self.question.correct_answer_index = index
        self.validate_question()

    def _on_time_changed(self, index: int) -> None:
        """Whenever the time selection changed."""
        seconds = self.time_combo.currentData()
        self.question.time_limit = seconds

        self.validate_question()

    def _update_correct_answer_buttons(self) -> None:
        """
        Update the enabled/disabled state of the correct answer radio buttons.
        The first two buttons are always enabled, while the last two are only enabled
        if their respective answers have text. If in read-only mode, all buttons are disabled.
        """
        for i, radio in enumerate(self.correct_radios):
            # Checks if the respective answer input field has text
            has_text = bool(self.answer_counters[i].line_edit.text().strip())

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

                    self.question.correct_answer_index = None

    def on_enter(self, total_questions: int, is_first: bool) -> None:
        """Called when this editor is shown. `is_first` is True if the screen is shown
        upon creating the question for the first time."""
        self.total_questions = total_questions

        self.update_question_num(self.question_num, self.total_questions)

        self.is_first = is_first
        self.validate_question()

    def on_leave(self) -> None:
        """Called when this editor is hidden."""
        self.question_validation_results = self.question.validate_question()

        # Informs parent if there are any errors in this question to show that to the user
        self.error_results.emit(
            self.question, len(self.question_validation_results) > 0
        )
