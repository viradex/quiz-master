"""
quiz_manager.py

The quiz manager UI screen. Shows a list of all custom and default quizzes, allowing sorting and
filtering through them. Also allows creating a new quiz, editing and deleting existing quizzes, and
previewing default quizzes.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from core.app.enums import QuizSortingOrder
from core.app.screen_ids import Screen
from models.quiz import Quiz
from ui.components.button import create_return_button
from ui.components.card import Card, QuizCard
from ui.components.dialog import confirm_warning
from ui.screens.base_screen import BaseScreen
from utils.paths import get_icons_dir

# Contains sorting data for the UI, with the internal enum value and the
# respective string to show to the UI, allowing the program to easily convert
# a user-given value to the internal value.
SORT_BY_DATA: dict[QuizSortingOrder, str] = {
    QuizSortingOrder.NEWEST: "Newest",
    QuizSortingOrder.OLDEST: "Oldest",
    QuizSortingOrder.NAME_ASC: "Name (A-Z)",
    QuizSortingOrder.NAME_DESC: "Name (Z-A)",
}


class CommonQuizManagerScreen(BaseScreen):
    """
    Creates the quiz manager screen, inheriting BaseScreen. This screen is part of the 'common' category.

    This screen is responsible for showing users all the saved quizzes on their device, as well as allowing
    sorting and searching through the quizzes. It also allows editing and deleting quizzes, and creating new
    ones.

    Attributes:
        title_text: The default text of the screen when entered. A string is used as that is what the
            title changing code requires.

        edit_requested: A `pyqtSignal` that emits when the user clicks the edit button on a quiz card. The
            Quiz model selected is provided as an argument.

        delete_requested: A `pyqtSignal` that emits when the user clicks the delete button on a quiz card. The
            Quiz model selected is provided as an argument.

        invalid_quiz_info_requested: A `pyqtSignal` that emits when the user requests information on why certain
            quizzes are hidden. No arguments are provided.

        search_requested: A `pyqtSignal` that emits when the user edits the search box. The search query as a
            string is provided as an argument.

        sort_requested: A `pyqtSignal` that emits when the user edits the sort selection dropdown box. The
            sorting criteria as a QuizSortingOrder is provided as an argument.

    Arguments:
        parent: The parent of this screen, or None. Typically, this is the MainWindow.
    """

    title_text = "Quiz Master – Manage Quizzes"

    edit_requested = pyqtSignal(Quiz)
    delete_requested = pyqtSignal(Quiz)
    invalid_quiz_info_requested = pyqtSignal()

    # Search query
    search_requested = pyqtSignal(str)
    sort_requested = pyqtSignal(QuizSortingOrder)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

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
        self.list_mod_font = QFont()
        self.list_mod_font.setPointSize(10)

        self.invalid_quizzes_font = QFont()
        self.invalid_quizzes_font.setPointSize(10)

    def _setup_widgets(self) -> None:
        """
        Internal method. Sets up all widgets used by the screen, including styling and slots, if needed. These
        widgets are not added to any global layout in this method, however.

        Returns:
            None.
        """
        self._setup_header_widgets()
        self._setup_list_mod_widgets()
        self._setup_quiz_list_widgets()

    def _setup_header_widgets(self) -> None:
        """
        Internal method. Sets up all widgets related to the header, including styling and slots, if needed.
        These widgets are not added to any global layout in this method, however.

        Returns:
            None.
        """
        self.heading = QLabel("Manage Quizzes")
        self.heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.heading.setStyleSheet("font-size: 36px;" "font-weight: 600;")

        self.return_btn = create_return_button("Return to Menu", btn_width=120)
        self.return_btn.clicked.connect(lambda: self.go_to(Screen.COMMON_MENU))

        self.create_btn = QPushButton("Create New Quiz")
        self.create_btn.setFixedSize(180, 40)
        self.create_btn.clicked.connect(lambda: self.go_to(Screen.COMMON_QUIZ_SETUP))
        self.create_btn.setStyleSheet("font-size: 14px;")

        # Contains number of total and custom quizzes when screen loaded
        self.num_quizzes = QLabel()
        self.num_quizzes.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.num_quizzes.setStyleSheet("font-size: 16px;" "color: #A0A0A0;")

    def _setup_list_mod_widgets(self) -> None:
        """
        Internal method. Sets up all widgets related to modifying the list of quizzes, including styling
        and slots, if needed. These widgets are not added to any global layout in this method, however.

        Returns:
            None.
        """
        # Allows filtering through quizzes by searching by title
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search quizzes...")
        self.search_input.setFixedHeight(35)
        self.search_input.textChanged.connect(self._on_search_change)
        self.search_input.setFont(self.list_mod_font)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e1e;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                padding: 4px 8px;
            }
                                        
            QLineEdit::placeholder {
                color: #888;
            }
        """)

        # Adds a search icon to the beginning of the search box
        search_icon = get_icons_dir() / "search.png"
        self.search_input.addAction(
            QIcon(str(search_icon)), QLineEdit.ActionPosition.LeadingPosition
        )

        # Sort by instructional label to accompany the dropdown
        self.sort_by_lbl = QLabel("Sort by:")
        self.sort_by_lbl.setStyleSheet("font-size: 14px;" "color: #888;")

        # Allows sorting quizzes by certain criteria
        self.sort_by_combo = QComboBox()
        self.sort_by_combo.setFixedSize(200, 35)

        # Prevent combobox from being edited like a textbox to add invalid values
        self.sort_by_combo.setEditable(False)
        self.sort_by_combo.activated.connect(self._on_sort_changed)
        self.sort_by_combo.setFont(self.list_mod_font)

        # Must add custom chevron icon as styling since the combobox removes it.
        # The .as_posix() method is required rather than !s or str() for
        # cross-platform usage as on Windows, the backslashes that it converts
        # to are used in PyQt as escape sequences, which break the path.
        chevron_down_icon = get_icons_dir() / "chevron_down.png"
        self.sort_by_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: #1e1e1e;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                padding: 4px 8px;
            }}
        
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
        
            QComboBox::down-arrow {{
                image: url("{chevron_down_icon.as_posix()}");
                width: 12px;
                height: 12px;
            }}
        """)

        # Add all values to combobox dynamically, with the display value and
        # internal QuizSortingOrder value added to each entry.
        for order, text in SORT_BY_DATA.items():
            self.sort_by_combo.addItem(text, order)

    def _setup_quiz_list_widgets(self) -> None:
        """
        Internal method. Sets up all widgets related to the actual list of quizzes, including styling and
        slots, if needed. These widgets are not added to any global layout in this method, however.

        Returns:
            None.
        """
        # Card for visually separating quiz list from rest of the UI
        self.card = Card(radius=10)

        # Scroll area for all the cards
        self.scroll_area = QScrollArea()

        # Makes the scroll area resize to fill its available space instead of
        # remaining at its fixed initial size.
        self.scroll_area.setWidgetResizable(True)

        # Removes the frame around the scroll area to make it blend into
        # the surrounding UI.
        self.scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)

        # Wrapper for all quiz items, and set scroll area as the scroller
        self.scroll_contents = QWidget()
        self.scroll_area.setWidget(self.scroll_contents)

        # Empty quizzes card (when no quizzes are shown); hidden by default
        self.empty_quizzes = QFrame()
        self.empty_quizzes.hide()

        # Set custom object name to ensure the styles don't apply to any children QFrames
        self.empty_quizzes.setObjectName("empty")
        self.empty_quizzes.setStyleSheet("""
            QFrame#empty {
                background-color: transparent;
                border: 2px dotted #5C5C5C;
                border-radius: 10px;
            }
        """)

        # Set up widgets that the 'no quizzes' card contains
        self.empty_title_lbl = QLabel("No Quizzes Found")
        self.empty_title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_title_lbl.setStyleSheet(
            "font-size: 20px;" "font-weight: 600;" "color: #8A8A8A"
        )

        self.empty_desc_lbl = QLabel("Try a different search, or create a new quiz.")
        self.empty_desc_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_desc_lbl.setStyleSheet("font-size: 14px;" "color: #8A8A8A")

        # Enable rich text on this QLabel to allow the interactive "Learn more" link
        # while keeping link handling on the same line as non-interactive text, rather
        # than using a ClickableLabel, which would make the entire text clickable.
        self.invalid_quizzes = QLabel(
            '1 quiz could not be loaded. <a href="learnmore">Learn more</a>', self
        )
        self.invalid_quizzes.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.invalid_quizzes.setFont(self.invalid_quizzes_font)

        # Supports HTML
        self.invalid_quizzes.setTextFormat(Qt.TextFormat.RichText)

        # Hidden by default
        self.invalid_quizzes.hide()

        # Allows link to be clicked and also interacted with by keyboard
        self.invalid_quizzes.setTextInteractionFlags(
            Qt.TextInteractionFlag.LinksAccessibleByMouse
            | Qt.TextInteractionFlag.LinksAccessibleByKeyboard
        )

        # Prevents PyQt from opening links in the default web browser
        self.invalid_quizzes.setOpenExternalLinks(False)
        self.invalid_quizzes.linkActivated.connect(
            lambda _: self.invalid_quiz_info_requested.emit()
        )

    def _setup_layouts(self) -> None:
        """
        Internal method. Sets up all the layouts on this screen, adding widgets and controlling alignment, spacing,
        and stretching. The main layout is also applied as this screen's primary layout via `setLayout()`.

        Returns:
            None.
        """
        # Create child layouts, and set them up if they don't return a layout
        header_layout = self._create_header_layout()
        list_mod_layout = self._create_list_mod_layout()

        self._setup_quiz_list_layouts()

        # Set up main layout
        vbox = QVBoxLayout()
        vbox.setContentsMargins(20, 20, 20, 10)
        vbox.addLayout(header_layout)
        vbox.addLayout(list_mod_layout)
        vbox.addSpacing(10)

        # Quiz list, that takes up the remaining screen space
        vbox.addWidget(self.card, stretch=1)

        # Footer for errors, by default hidden
        vbox.addSpacing(10)
        vbox.addWidget(self.invalid_quizzes)

        self.setLayout(vbox)

    def _create_header_layout(self) -> QVBoxLayout:
        """
        Internal method. Creates the header layout, adding widgets and controlling alignment, spacing,
        and stretching.

        Returns:
            The layout to add to the main layout.
        """
        # Create header using grid layout to ensure buttons and heading are aligned evenly
        nav_grid = QGridLayout()
        nav_grid.addWidget(self.return_btn, 0, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        nav_grid.addWidget(self.heading, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        nav_grid.addWidget(self.create_btn, 0, 2, alignment=Qt.AlignmentFlag.AlignRight)
        nav_grid.setColumnStretch(0, 1)
        nav_grid.setColumnStretch(1, 0)
        nav_grid.setColumnStretch(2, 1)

        vbox_header = QVBoxLayout()
        vbox_header.addLayout(nav_grid)
        vbox_header.addSpacing(2)
        vbox_header.addWidget(self.num_quizzes)
        vbox_header.addSpacing(10)

        return vbox_header

    def _create_list_mod_layout(self) -> QHBoxLayout:
        """
        Internal method. Creates the quiz list modification control layout, adding widgets and controlling
        alignment, spacing, and stretching.

        Returns:
            The layout to add to the main layout.
        """
        # Add label and sort by combobox next to each other
        sort_by_hbox = QHBoxLayout()
        sort_by_hbox.addStretch()
        sort_by_hbox.addWidget(self.sort_by_lbl)
        sort_by_hbox.addSpacing(5)
        sort_by_hbox.addWidget(self.sort_by_combo)

        # Allow 2:3:2 ratio for stretching
        list_mod_hbox = QHBoxLayout()
        list_mod_hbox.addWidget(self.search_input, stretch=2)
        list_mod_hbox.addStretch(3)
        list_mod_hbox.addLayout(sort_by_hbox, stretch=2)

        return list_mod_hbox

    def _setup_quiz_list_layouts(self) -> None:
        """
        Internal method. Sets up the quiz list layout, adding widgets and controlling alignment, spacing,
        and stretching.

        Returns:
            None.
        """
        card_vbox = QVBoxLayout(self.card)
        card_vbox.addWidget(self.scroll_area)

        # Layout for 'no quizzes' card
        self.empty_vbox = QVBoxLayout(self.empty_quizzes)
        self.empty_vbox.setContentsMargins(16, 12, 16, 12)
        self.empty_vbox.addWidget(self.empty_title_lbl)
        self.empty_vbox.addWidget(self.empty_desc_lbl)

        # By default, show 'no quizzes'
        self.quiz_vbox = QVBoxLayout(self.scroll_contents)
        self.quiz_vbox.setSpacing(10)
        self.quiz_vbox.addWidget(self.empty_quizzes)

    def add_quizzes(self, quizzes: list[Quiz]) -> None:
        """
        Adds a list of quizzes to the UI. This method does not remove any quizzes from the UI; to do that,
        run `remove_all_quizzes()`. This method can be used to refresh the UI upon a search or sorting
        change as well as upon first entering the screen.

        If no quizzes are entered, the 'no quizzes' card is shown by itself. Otherwise, all the quizzes
        provided are displayed in their own quiz cards. **The quizzes list must be ordered by custom
        quizzes first, then default quizzes.** This allows the UI code that separates the custom quizzes from
        the default quizzes to function properly without breaking the UI.

        If there are no custom quizzes (which is checked by if the list begins with a default quiz), no
        separator is shown. Only after all custom quizzes are displayed is the separator and then the
        default quizzes are shown.

        Arguments:
            quizzes: A list of Quiz instances to add to the UI. This list is assumed to be sorted by custom
                quizzes first, then default quizzes. A list is used as it is an ordered collection of
                items, allowing for easier sorting and usage in the UI.

        Returns:
            None.
        """
        if not quizzes:
            # Show only empty quizzes card if no quizzes are provided
            self.empty_quizzes.show()
            self.quiz_vbox.addStretch()
            return
        else:
            self.empty_quizzes.hide()

        # Whether the quiz list has started showing default quizzes
        default_started = False

        # Whether the quiz list begins with a default (meaning it only has default quizzes)
        starts_with_default = quizzes[0].is_premade

        for quiz in quizzes:
            # If this is the first default quiz and the list doesn't start with a default quiz,
            # add a separator between defaults and custom quizzes.
            if quiz.is_premade and not default_started and not starts_with_default:
                default_started = True

                # Add physical line divider and padding around the line
                divider = QFrame()
                divider.setFrameShape(QFrame.Shape.HLine)
                divider.setFrameShadow(QFrame.Shadow.Plain)
                divider.setStyleSheet("color: #3C3C3C;")

                self.quiz_vbox.addSpacing(10)
                self.quiz_vbox.addWidget(divider)
                self.quiz_vbox.addSpacing(10)

            quiz_card = QuizCard(quiz)

            # Connect signals from the card, allowing decoupling so the card doesn't
            # know how to delete or edit a quiz itself.
            quiz_card.edit_quiz_requested.connect(self._on_edit_quiz)
            quiz_card.delete_quiz_requested.connect(self._on_delete_quiz)

            self.quiz_vbox.addWidget(quiz_card)

        # Add stretch after all cards, if required, to ensure there is no extra
        # spacing between individual cards.
        self.quiz_vbox.addStretch()

    def remove_all_quizzes(self) -> None:
        """
        Remove all quiz cards from the UI, including any separators. This leaves the quiz list completely blank.
        This does not add the 'no quizzes' special card after removal of all cards. This method can be
        paired with the `add_quizzes()` method to refresh the quiz list.

        Returns:
            None.
        """
        # Iterate through widgets in reversed order, as removing indices while
        # starting from 0 can cause some to be skipped, due to the indexes being
        # updated as the removal occurs for widgets. Starting from the end
        # prevents that.
        for i in reversed(range(self.quiz_vbox.count())):
            # Get widget at specified position
            item = self.quiz_vbox.itemAt(i)
            widget = item.widget()

            if widget is None:
                # Remove stretchers and spacers
                self.quiz_vbox.removeItem(item)
            elif widget is self.empty_quizzes:
                # Ensure the 'no quizzes' card does not get removed in case it is
                # needed for future use
                continue
            else:
                # Remove all other widgets (mainly quiz cards and line separators)
                self.quiz_vbox.removeWidget(widget)
                widget.deleteLater()

    def set_quizzes_number(self, total: int | str, custom: int | str) -> None:
        """
        Set the total number of quizzes in the UI, as well as the number of custom quizzes created by the
        user. In normal usage, the number of total quizzes is expected to be greater than or equal to the
        normal of custom quizzes, however, this is not enforced.

        Arguments:
            total: An integer or string stating the number of total quizzes. An integer is allowed for
                easier method calling as calculations for the total quizzes would typically be done via
                integers. A string is allowed as the parameters are inevitably converted to a string, and
                it reduces overhead for if the total quizzes were a string.

            custom: An integer or string stating the number of custom quizzes. An integer is allowed for
                easier method calling as calculations for the custom quizzes would typically be done via
                integers. A string is allowed as the parameters are inevitably converted to a string, and
                it reduces overhead for if the custom quizzes were a string.

        Returns:
            None.
        """
        self.num_quizzes.setText(f"Your quizzes: {custom} • Total quizzes: {total}")

    def set_invalid_quizzes_visibility(
        self, visible: bool, total_invalid: int | None = None
    ) -> None:
        """
        Set whether or not the 'invalid quizzes' label can be seen or not. If the label should be visible, the
        total number of invalid quizzes must also be provided.

        Arguments:
            visible: Whether or not the label should be visible. The label should only be visible if there are
                currently any invalid quizzes. If set to True, the label is not hidden. Otherwise, it is hidden.

            total_invalid: The total number of invalid quizzes. This should only be filled in if the quizzes
                should be visible. Otherwise, it can be set to None. If the quizzes are visible, this value should
                be an integer, as the total invalid quizzes is typically a whole number. Defaults to None.

        Returns:
            None.
        """
        self.invalid_quizzes.setHidden(not visible)

        if visible:
            self.invalid_quizzes.setText(
                f'{total_invalid} {'quiz' if total_invalid == 1 else 'quizzes'} could not be loaded. <a href="learnmore">Learn more</a>'
            )

    def _on_search_change(self, query: str) -> None:
        """
        Internal method. Intended to be called when the search query is modified. Emits a signal that signals
        that a search has been requested, with the provided query.

        The query is not modified at all.

        Arguments:
            query: A string containing the user's search query. A string is used as the search requested
                requires a string, and a search consists of several characters which a string can naturally
                represent.

        Returns:
            None.
        """
        self.search_requested.emit(query)

    def _on_sort_changed(self, index: int) -> None:
        """
        Internal method. Intended to be called when the sort criteria is modified. Emits a signal that signals
        that the sorting criteria has been changed, with the provided new sorting order as a QuizSortingOrder.

        The internal sorting order is retrieved directly from the combobox. The index provided is unused.

        Arguments:
            index: An integer that describes the index the user selected from the dropdown. An integer is used
                as the index is easily represented as a zero-index whole number for calculations. This argument
                is unused in this method, however, and is only added as an argument as PyQt automatically passes
                it, to prevent a crash.

        Returns:
            None.
        """
        # Get the internal sorting order as a QuizSortingOrder
        sort_order = self.sort_by_combo.currentData()
        self.sort_requested.emit(sort_order)

    def _on_edit_quiz(self, quiz: Quiz) -> None:
        """
        Internal method. Intended to be called when a quiz has been requested to be edited by the user. Emits
        a signal that signals the quiz that the user wishes to edit, with the provided Quiz.

        Arguments:
            quiz: The Quiz instance of the quiz that the user wishes to edit.

        Returns:
            None.
        """
        self.edit_requested.emit(quiz)

    def _on_delete_quiz(self, quiz: Quiz) -> None:
        """
        Internal method. Intended to be called when a quiz has been requested to be deleted by the user. Emits
        a signal that signals the quiz that the user wishes to delete, with the provided Quiz.

        The user is asked to confirm deleting the quiz before the action is emitted. If the user declines, the
        operation is cancelled.

        Arguments:
            quiz: The Quiz instance of the quiz that the user wishes to delete.

        Returns:
            None.
        """
        confirm = confirm_warning(
            self,
            "Confirm Deleting Quiz",
            f'Are you sure you want to permanently delete the quiz "{quiz.quiz_title}"? This cannot be undone!',
        )

        if confirm:
            self.delete_requested.emit(quiz)

    def on_leave(self) -> None:
        # Reset quiz list modification inputs
        self.search_input.setText("")

        # Set combobox to first element in dropdown
        self.sort_by_combo.setCurrentIndex(0)

        # Reset quiz list
        self.remove_all_quizzes()
        self.num_quizzes.setText("")
