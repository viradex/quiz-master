"""
multi_question.py

The client multi-question UI screen. Allows answering a question provided by the server, or previewing
a question provided by the quiz editor.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QCloseEvent, QFont
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from core.app.enums import AnswerButtonGridMode
from core.app.screen_ids import Screen
from models.payloads import QuestionPayload
from ui.components.answer_button_grid import AnswerButtonGrid
from ui.components.button import create_return_button
from ui.components.dialog import confirm_warning
from ui.components.question_timer import QuestionTimer
from ui.screens.base_screen import BaseScreen


class ClientMultiQuestionScreen(BaseScreen):
    """
    Creates the client multi-question screen, inheriting BaseScreen. This screen is part of the 'client' category.

    This screen is responsible for allowing users to select an answer to a question given, or for previewing
    a question.

    Attributes:
        title_text: The default text of the screen when entered. A string is used as that is what the
            title changing code requires.

        answer_submitted: A `pyqtSignal` that emits when the user submits an answer. This signal is only emitted
            when the screen is not in preview mode. An integer is provided that represents the answer selected,
            zero-indexed.

        left_server: A `pyqtSignal` that emits when the user wishes to leave the server. No arguments are
            provided.

    Arguments:
        parent: The parent of this screen, or None. Typically, this is the MainWindow.
    """

    title_text = "Quiz Master – Question"

    answer_submitted = pyqtSignal(int)
    left_server = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # Whether this screen is showing a preview rather than in a live game
        self.is_preview: bool = False

        # Whether this screen is showing a read-only preview
        self.read_only_quiz: bool = False

        self._setup_ui()

    def _setup_ui(self) -> None:
        """
        Internal method. Sets up the screen UI, including fonts, widgets, and layouts, for the first time.
        This method should only be called once, preferably in the initialization logic.

        Returns:
            None.
        """
        ## FONTS SETUP ##
        question_num_font = QFont()
        question_num_font.setPointSize(12)

        question_font = QFont()
        question_font.setPointSize(26)
        question_font.setBold(True)

        ## WIDGETS SETUP ##
        # Left side (main section)
        self.question_num = QLabel()
        self.question_num.setFont(question_num_font)

        # Set word wrap to ensure question does not extend beyond view and overflow
        self.question_lbl = QLabel()
        self.question_lbl.setWordWrap(True)
        self.question_lbl.setFont(question_font)

        self.answer_button_grid = AnswerButtonGrid(AnswerButtonGridMode.LIVE)
        self.answer_button_grid.answer_select.connect(self._on_answer_select)

        # Right side column
        self.leave_btn = create_return_button("Leave")
        self.leave_btn.clicked.connect(self._on_leave_game)

        self.question_timer = QuestionTimer()

        ## LAYOUTS SETUP ##
        vbox_left = QVBoxLayout()
        vbox_left.addSpacing(20)
        vbox_left.addWidget(self.question_num)
        vbox_left.addSpacing(10)
        vbox_left.addWidget(self.question_lbl)
        vbox_left.addSpacing(20)

        # Ensure button grid takes up majority of screen
        vbox_left.addWidget(self.answer_button_grid, stretch=1)
        vbox_left.addSpacing(20)

        # Makes question timer take up rest of column
        vbox_right = QVBoxLayout()
        vbox_right.addWidget(
            self.leave_btn, stretch=0, alignment=Qt.AlignmentFlag.AlignRight
        )
        vbox_right.addWidget(
            self.question_timer, stretch=1, alignment=Qt.AlignmentFlag.AlignRight
        )

        # Left side takes up the rest of the space that right side doesn't use
        hbox = QHBoxLayout()
        hbox.setContentsMargins(50, 20, 20, 20)
        hbox.addLayout(vbox_left, stretch=1)
        hbox.addSpacing(40)
        hbox.addLayout(vbox_right)

        self.setLayout(hbox)

    def _on_answer_select(self, index: int) -> None:
        """
        Internal method. Intended to be run when the user selects an answer in the answer button grid. The
        answer selected is sent to the server and the question timer is visually locked.

        The answer is not sent to the server if in preview mode, but the question timer is still visually
        locked.

        Arguments:
            index: An integer that represents the answer selected, zero-indexed. An integer is used as it
                easily represents the position of an element in a list, which is what answers are stored in.

        Returns:
            None.
        """
        # Do not send answer to server if in preview mode
        if not self.is_preview:
            self.answer_submitted.emit(index)

        self.question_timer.lock()

    def _on_leave_game(self) -> None:
        """
        Internal method. Intended to be run when the user clicks the Leave button. If the screen is in preview
        mode, the screen immediately goes to the quiz editor without a confirmation dialog. Otherwise, displays
        a warning confirmation dialog to ensure the user wishes to leave the server, then disconnects from the
        server.

        Returns:
            None.
        """
        if self.is_preview:
            self.go_to(Screen.COMMON_QUIZ_EDITOR)
            return

        # Show warning to leave server as if screen is not in preview mode,
        # it is in a live server game.
        confirm = confirm_warning(
            self,
            "Confirm Leaving",
            "Are you sure you want to disconnect and return to menu? You won't be able to reconnect and your progress in the game will be lost.",
        )

        if confirm:
            self.left_server.emit()

    def on_enter(self, payload: QuestionPayload) -> None:
        # Set global attributes from payload
        self.is_preview = payload.is_preview
        self.read_only_quiz = payload.read_only_quiz

        question_progress = f"{payload.question_num} / {payload.total_questions}"

        # Set unique title if in preview mode
        if self.is_preview:
            self.set_title(f"Quiz Master – Question {question_progress} (Preview)")
        else:
            self.set_title(f"Quiz Master – Question {question_progress}")

        # Set all UI elements to reflect payload data
        self.question_num.setText(f"Question {question_progress}")
        self.question_lbl.setText(payload.question_text)

        self.answer_button_grid.set_answers(payload.answer_options)

        # Changes text of Leave/Return button depending on if in preview mode
        self.leave_btn.setText("Return" if self.is_preview else "Leave")

        # Set time limit in milliseconds from seconds, and start timer immediately
        self.question_timer.set_duration(payload.time_limit * 1000)
        self.question_timer.start()

    def on_leave(self) -> None:
        # Reset all dynamic UI elements
        self.set_title("Quiz Master – Question")

        self.question_num.setText("")
        self.question_lbl.setText("")

        self.answer_button_grid.reset_buttons()

        # Stop timer to prevent CPU usage
        self.question_timer.stop()

    def on_window_close(self, event: QCloseEvent) -> None:
        # Only show confirmation dialog if in preview mode. No warning is shown
        # if the quiz is read-only as there is no risk of data being lost if
        # the user couldn't have changed anything. If the quiz is a live quiz,
        # the app controller should show a warning itself, so it's not needed here.
        if self.is_preview and not self.read_only_quiz:
            confirm = confirm_warning(
                self,
                "Confirm Closing",
                "Are you sure you want to close the preview window? Any unsaved changes in the quiz editor will be lost.",
            )

            if confirm:
                event.accept()
            else:
                event.ignore()
