from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QRadioButton,
    QButtonGroup,
    QComboBox,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal

from ui.components.label import ClickableLabel
from ui.components.button import create_tool_icon_button


class SingleQuestionEditor(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.base_dir = Path(__file__).resolve().parent.parent
        self.icons_path = self.base_dir / "assets" / "icons"

        self.answer_data = [
            {"color": "#C94F4F", "letter": "A", "required": True},
            {"color": "#4A78C2", "letter": "B", "required": True},
            {"color": "#B89B2E", "letter": "C", "required": False},
            {"color": "#3E9B68", "letter": "D", "required": False},
        ]

        self.time_data = {
            "options": {
                5: "5 seconds",
                10: "10 seconds",
                15: "15 seconds",
                20: "20 seconds",
                30: "30 seconds",
                45: "45 seconds",
                60: "1 minute",
                90: "1 minute 30 seconds",
                120: "2 minutes",
                180: "3 minutes",
                240: "4 minutes",
            },
            "default": 3,  # index of default time 0-based
        }

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
        # Question number and helper btns with question text
        self.question_num = QLabel("Question 1 / 10")
        self.question_num.setFont(question_num_font)

        preview_icon = self.icons_path / "preview.png"
        delete_icon = self.icons_path / "delete.png"

        self.preview_btn = create_tool_icon_button(
            preview_icon, "Preview", icon_size=28
        )
        self.delete_btn = create_tool_icon_button(delete_icon, "Delete", icon_size=28)

        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText("Enter question...")
        self.question_input.setFixedHeight(45)
        self.question_input.setStyleSheet("font-size: 22px; padding: 8px;")

        # Answer button grid
        btn_grid = QGridLayout()
        btn_grid.setSpacing(15)

        self.answer_inputs = []

        for i in range(2):
            for j in range(2):
                index = i * 2 + j
                data = self.answer_data[index]

                answer_input = QLineEdit()
                answer_input.setFixedHeight(80)
                answer_input.setPlaceholderText(
                    f"Answer '{data['letter']}' {'(optional)' if not data['required'] else ''}"
                )
                answer_input.setFont(answer_input_font)

                answer_input.setStyleSheet(f"""
                    QLineEdit {{
                        border: 2px solid {data["color"]};
                        border-radius: 10px;
                        padding: 8px;
                    }}
                """)

                self.answer_inputs.append(answer_input)
                btn_grid.addWidget(answer_input, i, j)

        # Correct answer selection
        correct_answer_lbl = QLabel("Select correct answer:")
        correct_answer_lbl.setFont(extra_data_font)

        self.correct_group = QButtonGroup()

        correct_answer_vbox = QVBoxLayout()
        correct_answer_vbox.setContentsMargins(20, 0, 0, 0)
        correct_answer_vbox.addWidget(correct_answer_lbl)
        correct_answer_vbox.addSpacing(10)

        self.correct_radios = []

        for i in range(4):
            data = self.answer_data[i]

            correct_radio = QRadioButton(f"Answer '{data['letter']}'")
            correct_radio.setStyleSheet(f"""
                QRadioButton {{
                    font-size: 18px; font-weight: 600; color: {data['color']};
                }}                  
            """)

            self.correct_group.addButton(correct_radio, i)
            self.correct_radios.append(correct_radio)

            correct_answer_vbox.addWidget(correct_radio)
            correct_answer_vbox.addSpacing(5)

        correct_answer_vbox.addStretch()

        # Time limit selection
        time_lbl = QLabel("Set time limit:")
        time_lbl.setFont(extra_data_font)

        self.time_combo = QComboBox()
        self.time_combo.setFixedSize(250, 40)
        self.time_combo.setEditable(False)
        self.time_combo.setFont(extra_data_font)

        for seconds, value in self.time_data["options"].items():
            self.time_combo.addItem(value, seconds)

        self.time_combo.setCurrentIndex(self.time_data["default"])

        self.apply_global_time = ClickableLabel("Apply to all questions")
        self.apply_global_time.setStyleSheet(
            "font-size: 14px;" "text-decoration: underline;" "color: #9A9A9A;"
        )

        ## LAYOUTS SETUP ##
        heading_hbox = QHBoxLayout()
        heading_hbox.addWidget(self.question_num, stretch=1)
        heading_hbox.addWidget(self.preview_btn)
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
        vbox.addWidget(self.question_input)
        vbox.addSpacing(40)
        vbox.addLayout(btn_grid)
        vbox.addSpacing(40)
        vbox.addLayout(extra_grid)
        vbox.addStretch(2)

        self.setLayout(vbox)
