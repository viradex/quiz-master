from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QSpinBox,
    QRadioButton,
    QButtonGroup,
    QComboBox,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QMessageBox,
)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt, pyqtSignal

from core.app.enums import QuestionValidationError
from ui.components.input import ClickableLabel, CharacterCountInput, ReversedSpinBox
from models.question import Question
from models.payloads import QuestionPayload

from ui.components.button import create_tool_icon_button
from ui.components.dialogs import confirm_warning
from utils.error_messages import format_errors, QUESTION_ERROR_MESSAGES
from core.config.constants import MAX_QUESTION_LENGTH, MAX_ANSWER_LENGTH

ANSWER_DATA = [
    {"color": "#C94F4F", "letter": "A", "required": True},
    {"color": "#4A78C2", "letter": "B", "required": True},
    {"color": "#B89B2E", "letter": "C", "required": False},
    {"color": "#3E9B68", "letter": "D", "required": False},
]

TIME_DATA = {
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
    error_results = pyqtSignal(Question, bool)

    question_reordered = pyqtSignal(Question, int)
    question_text_changed = pyqtSignal(Question)
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
        self.is_first = True

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
        self.issues_btn.hide()
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

        if self.read_only:
            duplicate_disabled_icon = self.icons_path / "duplicate_disabled.png"
            self.duplicate_btn.setIcon(QIcon(str(duplicate_disabled_icon)))

            delete_disabled_icon = self.icons_path / "delete_disabled.png"
            self.delete_btn.setIcon(QIcon(str(delete_disabled_icon)))

            self.duplicate_btn.setDisabled(self.read_only)
            self.duplicate_btn.setToolTip("Cannot edit read-only quiz")

            self.delete_btn.setDisabled(self.read_only)
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

        self._update_correct_answer_buttons()

        for i, answer in enumerate(self.question.answer_options):
            self._on_answer_edit(i, answer)

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
        self.question_num = question_num
        if total_questions is not None:
            self.total_questions = total_questions

        self.question_num_input.setValue(int(self.question_num))
        self.question_num_input.setMaximum(int(self.total_questions))
        self.total_question_lbl.setText(f"/ {self.total_questions}")

    def get_all_data(self) -> None:
        pass

    def disable_delete(self) -> None:
        if not self.read_only:
            delete_disabled_icon = self.icons_path / "delete_disabled.png"
            self.delete_btn.setIcon(QIcon(str(delete_disabled_icon)))
            self.delete_btn.setToolTip("Cannot delete the only question")
            self.delete_btn.setDisabled(True)

    def enable_delete(self) -> None:
        if not self.read_only:
            delete_icon = self.icons_path / "delete.png"
            self.delete_btn.setIcon(QIcon(str(delete_icon)))
            self.delete_btn.setToolTip("Delete")
            self.delete_btn.setDisabled(False)

    def set_time_limit(self, seconds: int) -> None:
        index = self.time_combo.findData(seconds)

        if index != -1:
            self.time_combo.setCurrentIndex(index)
            self.question.time_limit = seconds

        self.validate_question()

    def validate_question(self) -> None:
        self.question_validation_results = self.question.validate_question()

        # Preview button will be disabled regardless of first time
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

        if self.is_first:
            return

        # Issues warning button will not show on the first time
        if self.question_validation_results:
            self.issues_btn.show()
        else:
            self.issues_btn.hide()

    def _show_issues(self) -> None:
        self.validate_question()
        issues: list[str] = []

        if not self.question_validation_results:
            # Ordinarily this should never happen
            QMessageBox.information(
                self,
                "No Issues Detected",
                "No issues were detected with this question.",
            )
            return

        # Iterate over dict to preserve order in UI, as sets do not
        for error in QUESTION_ERROR_MESSAGES:
            if error in self.question_validation_results:
                issues.append(QUESTION_ERROR_MESSAGES[error])

        QMessageBox.warning(
            self,
            "Question Issues",
            f"The following issue(s) were detected in this question. These must be fixed before the quiz can be saved.\n\n{format_errors(issues)}",
        )

    def _on_preview_clicked(self) -> None:
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
        confirm = confirm_warning(
            self,
            "Confirm Deleting Question",
            "Are you sure you want to delete this question? This action is irreversable!",
        )

        if confirm:
            self.delete_requested.emit(self.question)

    def _on_apply_global_time(self) -> None:
        seconds = self.time_combo.currentData()
        text = self.time_combo.currentText()

        self.global_time_requested.emit(seconds, text)

    def _on_question_reorder(self, new_question_num: int) -> None:
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
        self.question.question_text = text.strip()

        self.question_text_changed.emit(self.question)
        self.validate_question()

    def _on_answer_edit(self, index: int, text: str) -> None:
        text = text.strip()

        while len(self.question.answer_options) <= index:
            self.question.answer_options.append("")

        self.question.answer_options[index] = text
        answer_radio = self.correct_group.button(index)

        if answer_radio is not None:
            if text:
                answer_radio.setText(text)
            else:
                data = ANSWER_DATA[index]
                answer_radio.setText(f"Answer '{data['letter']}'")

        self._update_correct_answer_buttons()
        self.validate_question()

    def _on_correct_answer_changed(self, index: int) -> None:
        self.question.correct_answer_index = index
        self.validate_question()

    def _on_time_changed(self, index: int) -> None:
        seconds = self.time_combo.currentData()
        self.question.time_limit = seconds

        self.validate_question()

    def _update_correct_answer_buttons(self):
        for i, radio in enumerate(self.correct_radios):
            has_text = bool(self.answer_counters[i].line_edit.text().strip())

            # A and B are always enabled
            if i < 2 and not self.read_only:
                radio.setEnabled(True)
            else:
                radio.setEnabled(has_text and not self.read_only)

                # If C or D were selected and is now disabled, unselect it
                if not has_text and radio.isChecked():
                    # Must set exclusive to False and then reset it to ensure the radio button can be unchecked
                    self.correct_group.setExclusive(False)
                    radio.setChecked(False)
                    self.correct_group.setExclusive(True)

                    self.question.correct_answer_index = None

    def on_enter(self, total_questions: int, is_first: bool) -> None:
        self.total_questions = total_questions

        self.update_question_num(self.question_num, self.total_questions)

        self.is_first = is_first
        self.validate_question()

    def on_leave(self) -> None:
        self.question_validation_results = self.question.validate_question()
        self.error_results.emit(
            self.question, len(self.question_validation_results) > 0
        )
