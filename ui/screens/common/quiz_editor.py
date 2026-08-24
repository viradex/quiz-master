"""
quiz_editor.py

The quiz editor UI screen. Allows editing the questions of a quiz. This screen is responsible for
managing the question editors individually; however, it does not create the code for individual
question editors or sidebar cards itself.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from core.app.screen_ids import Screen
from models.payloads import QuestionPayload
from models.question import Question
from models.quiz import Quiz
from ui.components.card import QuestionCard
from ui.components.question_editor import QuestionEditor
from ui.screens.base_screen import BaseScreen

# The warning to show on tooltips if the quiz is in read-only mode
READ_ONLY_WARNING = "Cannot edit read-only quiz"


class CommonQuizEditorScreen(BaseScreen):
    """
    Creates the quiz editor screen, inheriting BaseScreen. This screen is part of the 'common' category.

    This screen is responsible for showing the quiz editor screen, allowing the user to edit questions,
    as well as reordering, deletion, and previewing.

    Attributes:
        title_text: The default text of the screen when entered. A string is used as that is what the
            title changing code requires.

        blank_question_requested: A `pyqtSignal` that emits when the user clicks the Add button on the sidebar
            to request creation of a new blank question. No arguments are provided.

        duplicate_requested: A `pyqtSignal` that emits when the user clicks the duplicate button on a question.
            The Question to duplicate is provided as an argument.

        delete_requested: A `pyqtSignal` that emits when the user clicks the delete button on a question. The
            Question to delete is provided as an argument.

        question_reorder_requested: A `pyqtSignal` that emits when the user wishes to reorder a question. The
            Question to reorder and the new question index to move to as an integer are both provided as
            arguments.

        discard_requested: A `pyqtSignal` that emits when the user wishes to discard all changes that were made
            during this editing session. No arguments are provided.

        save_requested: A `pyqtSignal` that emits when the user wishes to manually save all changes that were made
            during this editing session. No arguments are provided.

    Arguments:
        parent: The parent of this screen, or None. Typically, this is the MainWindow.
    """

    title_text = "Quiz Master – Quiz Editor"

    blank_question_requested = pyqtSignal()
    duplicate_requested = pyqtSignal(Question)
    delete_requested = pyqtSignal(Question)
    question_reorder_requested = pyqtSignal(Question, int)  # New question index

    discard_requested = pyqtSignal()
    save_requested = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # When doing methods on self.quiz, avoid running methods that mutate the quiz
        # Good: self.quiz.get_total_questions()
        # Bad: self.quiz.remove_question(question.question_id)
        self.quiz: Quiz | None = None

        # Whether the quiz can be edited or not
        self.read_only: bool = False

        # Whether the screen should reset when shown or not
        self.returning_from_preview: bool = False

        # The dictionaries are expected to reflect each other in terms of keys.
        # A dictionary is used as it provides a simple lookup that does not change
        # if quizzes edit their position or are deleted.
        # Quiz ID -> Widget
        self.cards: dict[str, QuestionCard] = {}
        self.editors: dict[str, QuestionEditor] = {}

        self._setup_ui()

    def _setup_ui(self) -> None:
        """
        Internal method. Sets up the screen UI for the first time. This method should only be called once,
        preferably in the initialization logic.

        Returns:
            None.
        """
        self._setup_widgets()
        self._setup_layouts()

    def _setup_widgets(self) -> None:
        """
        Internal method. Sets up all widgets used by the screen, including styling and slots, if needed. These
        widgets are not added to any global layout in this method, however.

        Returns:
            None.
        """
        # Question card sidebar
        self.sidebar = QFrame()
        self.sidebar.setMinimumWidth(160)
        self.sidebar.setMaximumWidth(500)

        # Explicitly specify QFrame to ensure children do not inherit background color
        self.sidebar.setStyleSheet("QFrame { background-color: #252526; }")

        # All question cards container
        self.question_container = QWidget()
        self.question_container.setStyleSheet("background-color: #252526;")

        # Question list sidebar
        self.question_list = QVBoxLayout(self.question_container)
        self.question_list.setSpacing(15)
        self.question_list.setContentsMargins(5, 5, 5, 5)
        self.question_list.addStretch()

        self.question_scroll = QScrollArea()
        self.question_scroll.setWidget(self.question_container)

        # Makes the scroll area resize to fill its available space instead of
        # remaining at its fixed initial size.
        self.question_scroll.setWidgetResizable(True)

        # Removes the frame around the scroll area to make it blend into
        # the surrounding UI.
        self.question_scroll.setFrameShape(QFrame.Shape.NoFrame)

        # Action buttons (at bottom of sidebar)
        # Size policies allow buttons to expand to fill space horizontally
        # but have fixed height.
        self.add_btn = QPushButton("+ Add")
        self.add_btn.setFixedHeight(40)
        self.add_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.add_btn.clicked.connect(self.blank_question_requested.emit)
        self.add_btn.setStyleSheet("font-size: 18px;")

        # Acts as the Return button in read-only mode
        self.discard_btn = QPushButton("Discard")
        self.discard_btn.setFixedHeight(30)
        self.discard_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.discard_btn.clicked.connect(self.discard_requested.emit)
        self.discard_btn.setStyleSheet("font-size: 14px;")

        self.save_btn = QPushButton("Save")
        self.save_btn.setFixedHeight(30)
        self.save_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.save_btn.clicked.connect(self.save_requested.emit)
        self.save_btn.setStyleSheet("font-size: 14px;")

        # Main screen editor where question editors are stored. A QStackedWidget
        # is used so screens can be easily shown and hidden without destroying
        # and recreating on demand.
        self.editor_stack = QStackedWidget()

        # Allow resizing the width of the sidebar to question editor ratio
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.sidebar)
        self.splitter.addWidget(self.editor_stack)

        # 1:4 starting ratio, allowing question editor to stretch
        self.splitter.setSizes([200, 800])
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)

        # Prevents the sidebar or question editor from being fully collapsed
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setHandleWidth(2)
        self.splitter.setStyleSheet("""
            QSplitter::handle {
                background: #3a3a3a;
            }

            QSplitter::handle:hover {
                background: #5a5a5a;
            }
        """)

    def _setup_layouts(self) -> None:
        """
        Internal method. Sets up all the layouts on this screen, adding widgets and controlling alignment, spacing,
        and stretching. The main layout is also applied as this screen's primary layout via `setLayout()`.

        Returns:
            None.
        """
        sidebar_btn_hbox = QHBoxLayout()
        sidebar_btn_hbox.addWidget(self.discard_btn)
        sidebar_btn_hbox.addWidget(self.save_btn)

        sidebar_vbox = QVBoxLayout(self.sidebar)
        sidebar_vbox.addWidget(self.question_scroll, stretch=1)
        sidebar_vbox.addWidget(self.add_btn)
        sidebar_vbox.addLayout(sidebar_btn_hbox)

        # Set no margins to prevent sidebar from 'floating'
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(self.splitter)

        self.setLayout(hbox)

    def set_quiz(self, quiz: Quiz, read_only: bool) -> None:
        """
        Sets the quiz to edit internally. Also set the quiz to read-only mode or not, meaning the quiz
        cannot be edited in any way. This is typically True when the quiz is a pre-made quiz.

        On the UI, clears all existing questions, if any, and adds all the questions from the quiz provided,
        if any are available. If there are no questions, a blank new question is automatically shown.

        If the quiz is read-only the Add and Save buttons are disabled and a tooltip is shown displaying why.
        The Discard button acts as a Return button and does not attempt to alter the quiz state.

        Arguments:
            quiz: The Quiz to set the internal state to. This quiz is used to base the question editor off of.
                Typically, this should be a shared reference between the logic and screen.

            read_only: A boolean specifying whether or not the quiz can be edited or not. If True, the quiz is
                not allowed to be edited via the UI. Otherwise, the quiz can be edited.

        Returns:
            None.
        """
        # Remove all questions from UI in case
        self.clear_questions()

        # Update and reset internal properties
        self.quiz = quiz
        self.read_only = read_only
        self.returning_from_preview = False

        self.set_window_title()

        # Change button states if in read-only mode
        self.add_btn.setDisabled(self.read_only)
        self.save_btn.setDisabled(self.read_only)

        # Set tooltips if in read-only mode, and change Discard button to Return if read-only
        self.add_btn.setToolTip(READ_ONLY_WARNING if self.read_only else "")
        self.save_btn.setToolTip(READ_ONLY_WARNING if self.read_only else "")
        self.discard_btn.setText("Return" if self.read_only else "Discard")

        questions = self.quiz.questions

        # If editing existing quiz, prefills quiz editor with all of the widgets immediately
        if questions:
            for i, question in enumerate(questions, start=1):
                self.add_question(question, i)

            # Show the first question when entering
            # Since this can only happen while editing an existing quiz, it is not the first time
            first_question = questions[0]
            self.display_question(first_question, first_time=False)

    def set_window_title(self) -> None:
        """
        Automatically sets the application window title depending on if the quiz is in read-only mode or not as
        determined by the `read_only` attribute.

        Returns:
            None.
        """
        if self.read_only:
            self.set_title(f"Quiz Master – Viewing {self.quiz.quiz_title}")
        else:
            self.set_title(f"Quiz Master – Editing {self.quiz.quiz_title}")

    def add_question(
        self, question: Question, question_num: int, first_time: bool = True
    ) -> None:
        """
        Adds a question to the UI. A QuestionCard is added to represent the question on the sidebar and allow
        the user to click on the card to show the respective question editor. The QuestionEditor is also added
        and is part of a `QStackedWidget`, meaning it can be shown when needed.

        The question that is added has its card automatically selected, and the question editor shown. If the
        question already exists, it is simply displayed and not added to the UI separately.

        Arguments:
            question: The Question to add to the UI. This question will be modified directly by the individual
                question editor.

            question_num: An integer representing the question number of the question to add, which is used for
                UI purposes. An integer is used as it easily represents a whole number position.

            first_time: Whether or not this is the first time the editor is being shown in this session. A
                boolean is used as it gives an easy yes/no value for whether this is the first time or not.
                Default is True.

        Returns:
            None.
        """
        # If question is already shown, only show it
        if question.question_id in self.editors:
            self.display_question(question)
            return

        total_questions = self.quiz.get_total_questions()

        # Initialize editor and card
        editor = QuestionEditor(question, question_num, total_questions, self.read_only)
        card = QuestionCard(question, question_num)

        # Save and show editor on stacked widget
        self.editors[question.question_id] = editor
        self.editor_stack.addWidget(editor)
        self._show_editor(editor, first_time)

        # Save and show card on sidebar (as last element)
        self.cards[question.question_id] = card
        self.question_list.insertWidget(self.question_list.count() - 1, card)
        card.select()

        # Connect signals from the question editor to this parent window. Using
        # signals adds decoupling, ensuring the child widget does not know about
        # this screen directly, and only actions that affect the quiz as a whole
        # are delegated here.
        editor.error_results.connect(self._on_error_results)
        editor.question_reordered.connect(self.question_reorder_requested.emit)
        editor.question_text_changed.connect(self._on_question_text)
        editor.global_time_requested.connect(self._on_global_time)
        editor.preview_requested.connect(self._on_preview_requested)
        editor.duplicate_requested.connect(self.duplicate_requested.emit)
        editor.delete_requested.connect(self.delete_requested.emit)

        # Connect signals from card to here
        card.clicked.connect(lambda q: self.display_question(q, first_time=False))

        # Checks if the question(s) can be deleted
        self._update_delete_state()

    def remove_question(self, question: Question, next_question: Question) -> None:
        """
        Removes a question from the UI, and displays the next question after deletion. Both the QuestionCard
        and its respective QuestionEditor are removed from the UI and their respective parents.

        If the question does not exist, they are ignored. However, the next question provided is still displayed.
        The editor and cards are also removed separately. For example, if a QuestionEditor exists but a
        QuestionCard doesn't, the QuestionEditor is removed and the QuestionCard is ignored. However, this should
        never occur in normal operation as both are assumed to always reflect each other.

        Arguments:
            question: The Question to remove from the UI. The actual Question object is not destroyed itself, however.

            next_question: The next Question to show on the UI. This assumes it already has a relevant QuestionCard
                and QuestionEditor.

        Returns:
            None.
        """
        # Remove editor and card from dictionaries, if they exist
        editor = self.editors.pop(question.question_id, None)
        card = self.cards.pop(question.question_id, None)

        # If editor existed, remove it from UI and Qt
        if editor is not None:
            self.editor_stack.removeWidget(editor)
            editor.deleteLater()

        # If card existed, remove it from UI and Qt
        if card is not None:
            self.question_list.removeWidget(card)
            card.deleteLater()

        # Update UI states
        self._update_question_numbers()
        self._update_delete_state()

        # Do not use _show_editor(), as that method won't call on_enter() for the
        # question editor and thus won't inform it that it isn't the first time
        next_editor = self.editors.get(next_question.question_id)
        next_card = self.cards.get(next_question.question_id)

        if next_editor is not None and next_card is not None:
            self.editor_stack.setCurrentWidget(next_editor)

            next_card.select()
            next_editor.on_enter(self.quiz.get_total_questions(), is_first=False)

    def clear_questions(self) -> None:
        """
        Removes all questions from the UI and internal dictionaries, if any. This does not destroy any
        Question objects.

        Returns:
            None.
        """
        # Remove all editors from UI and Qt
        for editor in self.editors.values():
            self.editor_stack.removeWidget(editor)
            editor.deleteLater()

        # Remove all editors from UI and Qt
        for card in self.cards.values():
            self.question_list.removeWidget(card)
            card.deleteLater()

        # Delete all references from dictionaries
        self.editors.clear()
        self.cards.clear()

    def display_question(self, question: Question, first_time: bool = True) -> None:
        """
        Displays a specific question on the UI, highlighting the card respective to the editor, and showing the
        question editor in the `QStackedWidget`. If the question doesn't have a corresponding QuestionEditor
        or QuestionCard, the question is not displayed in the UI.

        Arguments:
            question: The Question to display on the UI. This should correspond to existing UI widgets created
                by `add_question()`.

            first_time: Whether or not this is the first time the editor is being shown in this session. A
                boolean is used as it gives an easy yes/no value for whether this is the first time or not.
                Default is True.

        Returns:
            None.
        """
        # Get editor and card widgets, if they exist
        editor = self.editors.get(question.question_id)
        card = self.cards.get(question.question_id)

        # Ensure early return if either doesn't exist, to avoid crashes later
        if editor is None or card is None:
            return

        # If selecting the card related to the editor that is currently shown,
        # don't show it again, but select the card.
        if self.editor_stack.currentWidget() is editor:
            card.select()
            return

        self._show_editor(editor, first_time)
        card.select()

    def update_question_order(self) -> None:
        """
        Updates the order of the question cards on the sidebar and their numbers, to reflect the current internal
        state. The question editors also have their question numbers edited.

        Returns:
            None.
        """
        self._refresh_card_order()
        self._update_question_numbers()

    def _show_editor(self, editor: QuestionEditor, first_time: bool = False) -> None:
        """
        Internal method. Shows the current question editor from the `QStackedWidget` and brings it to the front
        in the user's view. This does not update any QuestionCard styling or positioning.

        If the current screen is not the newly-requested screen, the `on_leave()` lifecycle method is called,
        allowing the question editor an opportunity to clean up. Then, the new editor is set as the shown
        widget and has its `on_enter()` lifecycle called.

        Arguments:
            editor: The QuestionEditor widget to show in place of the old one.

            first_time: Whether or not this is the first time the editor is being shown in this session. This is
                passed directly into the new QuestionEditor to be utilized however it wishes. A boolean is used
                as it gives an easy yes/no value for whether this is the first time or not. Default is False.

        Returns:
            None.
        """
        old = self.editor_stack.currentWidget()

        # Notify the old widget it is about to be hidden, only if the current
        # editor is not the same as the new one.
        if old is not None and old is not editor:
            old.on_leave()

        self.editor_stack.setCurrentWidget(editor)

        # Notify the new widget that it is visible, with relevant information
        editor.on_enter(self.quiz.get_total_questions(), first_time)

    def _refresh_card_order(self) -> None:
        """
        Internal method. Refreshes all question cards in the sidebar by removing and re-adding all to reflect
        any changes made in the Quiz object itself, as defined in `self.quiz`. The question editors are not
        affected.

        Returns:
            None.
        """
        # Remove every card
        for card in self.cards.values():
            self.question_list.removeWidget(card)

        # Reinsert in proper order
        for i, question in enumerate(self.quiz.questions):
            self.question_list.insertWidget(i, self.cards[question.question_id])

    def _update_question_numbers(self) -> None:
        """
        Internal method. Updates the question number on all question cards and question editors, based on the
        position of questions in the Quiz object itself, as defined in `self.quiz`.

        Returns:
            None.
        """
        total_questions = self.quiz.get_total_questions()

        for i, question in enumerate(self.quiz.questions, start=1):
            # Update cards
            if question.question_id in self.cards:
                self.cards[question.question_id].update_question_num(i)

            # Update editors
            if question.question_id in self.editors:
                self.editors[question.question_id].update_question_number(
                    i, total_questions
                )

    def _update_delete_state(self) -> None:
        """
        Internal method. Checks if the question editor(s) can be deleted. Currently, they can only not be
        deleted if the quiz is in read-only mode, or there is one or less question in the quiz.

        Returns:
            None.
        """
        for editor in self.editors.values():
            if self.quiz.get_total_questions() > 1 and not self.read_only:
                # If there is more than one question and not read-only mode
                editor.enable_delete()
            elif self.read_only:
                editor.disable_delete(READ_ONLY_WARNING)
            else:
                editor.disable_delete("Cannot delete the only question")

    def _on_error_results(self, question: Question, error_occurred: bool) -> None:
        """
        Internal method. Typically called when a question editor is left. Colors its respective card depending
        on whether the question has an validation error or not. Otherwise, it is colored normally.

        Arguments:
            question: The Question to display on the UI. This should correspond to an existing QuestionCard.

            error_occurred: A boolean specifying whether or not validation errors occurred while validating
                the question. A boolean is used as it gives an easy yes/no value for whether an error occurred.

        Returns:
            None.
        """
        card = self.cards[question.question_id]

        if error_occurred:
            card.error()
        else:
            card.deselect()

    def _on_preview_requested(self, payload: QuestionPayload) -> None:
        """
        Internal method. Previews a question by opening the `ClientMultiQuestionScreen` with a payload provided
        containing information about the question. This screen is also aware that the user is in a preview, and
        sets a flag for that information so it does not reset the quiz UI when re-entering.

        Arguments:
            payload: A QuestionPayload containing the data needed to preview the question. The data is assumed
                to have been validated. The `is_preview` and `read_only_quiz` properties can be filled in,
                however, they are set in this method as well.

        Returns:
            None.
        """
        # Sets attributes on payload signifying it is a preview in case the
        # caller did not set them.
        payload.is_preview = True
        payload.read_only_quiz = self.read_only

        self.returning_from_preview = True
        self.go_to(Screen.CLIENT_MULTI_QUESTION, payload)

    def _on_global_time(self, seconds: int, text: str) -> None:
        """
        Internal method. Sets the provided time limit to all available question editors in the quiz, if the user
        confirms to setting the time limit for all questions.

        Arguments:
            seconds: The number of seconds to set the time limit to for all questions. An integer is used as it
                represents the number of seconds well without floats, and the question data uses an integer to
                represent seconds, creating consistency.

            text: The user-friendly text to show the user in the confirmation dialog. This is typically the same
                as shown in the time selection for the question. A string is used as it is a set of characters
                with a prefix at the end, such as 'seconds', which require a string rather than an integer, for
                example.

        Returns:
            None.
        """
        confirm = self.show_question(
            "Set Time for All Questions?",
            f"Are you sure you want to change the time limit for all questions to {text}?",
        )

        if confirm:
            # Set time limit for all question editors
            for editor in self.editors.values():
                editor.set_time_limit(seconds)

    def _on_question_text(self, question: Question) -> None:
        """
        Internal method. Updates the question text of the question's respective card to match that of the Question
        provided.

        Arguments:
            question: The Question to retrieve the question text from, and to identify its respective card
                to edit.

        Returns:
            None.
        """
        self.cards[question.question_id].update_question_text(question.question_text)

    def on_enter(self, payload: dict | None = None) -> None:
        # Ensures a quiz exists, as set_window_title() depends on it. Also, do
        # not reset returning_from_preview from here, as the logic does that.
        if self.returning_from_preview and self.quiz is not None:
            self.set_window_title()
