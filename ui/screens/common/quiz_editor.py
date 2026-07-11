from PyQt6.QtWidgets import (
    QWidget,
    QFrame,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal

from core.app.screen_ids import Screens
from ui.screens.base_screen import BaseScreen
from ui.components.card import QuestionCard
from ui.components.question_editor import SingleQuestionEditor


class CommonQuizEditorScreen(BaseScreen):
    title_text = "Quiz Master – Quiz Editor (Quiz Name)"

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setup_ui()

    def setup_ui(self) -> None:
        ## WIDGETS SETUP ##
        sidebar = QFrame()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #252526;
            }
        """)

        # All questions
        question_container = QWidget()
        question_container.setStyleSheet("background-color: #252526;")

        self.question_list = QVBoxLayout(question_container)
        self.question_list.setSpacing(15)
        self.question_list.setContentsMargins(5, 5, 5, 5)

        card_one = QuestionCard(1, "What is the largest planet in the solar system?")
        card_one.toggle_selected()

        card_two = QuestionCard(2, "What is 2 + 2?")

        self.question_list.addWidget(card_one)
        self.question_list.addWidget(card_two)
        self.question_list.addStretch()

        question_scroll = QScrollArea()
        question_scroll.setWidgetResizable(True)
        question_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        question_scroll.setWidget(question_container)
        question_scroll.setFrameShape(QFrame.Shape.NoFrame)

        # Action buttons
        self.add_btn = QPushButton("+ Add")
        self.add_btn.setFixedHeight(40)
        self.add_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.add_btn.setStyleSheet("font-size: 18px;")

        self.discard_btn = QPushButton("Discard")
        self.discard_btn.setFixedHeight(30)
        self.discard_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.discard_btn.clicked.connect(
            lambda: self.go_to(Screens.COMMON_QUIZ_MANAGER)
        )
        self.discard_btn.setStyleSheet("font-size: 14px;")

        self.save_btn = QPushButton("Save")
        self.save_btn.setFixedHeight(30)
        self.save_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.save_btn.setStyleSheet("font-size: 14px;")

        # Main screen editor
        editor = SingleQuestionEditor()

        ## LAYOUTS SETUP ##
        sidebar_btn_hbox = QHBoxLayout()
        sidebar_btn_hbox.addWidget(self.discard_btn)
        sidebar_btn_hbox.addWidget(self.save_btn)

        sidebar_vbox = QVBoxLayout(sidebar)
        sidebar_vbox.addWidget(question_scroll, stretch=1)
        sidebar_vbox.addWidget(self.add_btn)
        sidebar_vbox.addLayout(sidebar_btn_hbox)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(sidebar)
        hbox.addWidget(editor, stretch=1)

        self.setLayout(hbox)
