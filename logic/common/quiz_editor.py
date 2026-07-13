from copy import deepcopy

from ui.screens.common.quiz_editor import CommonQuizEditorScreen
from logic.base_logic import BaseLogic
from core.services.app_context import Services
from models.quiz import Quiz
from models.question import Question


class CommonQuizEditorLogic(BaseLogic):
    def __init__(self, screen, services) -> None:
        super().__init__()
        self.screen: CommonQuizEditorScreen = screen
        self.services: Services = services

        self.quiz: Quiz | None = None
        self.mode: str | None = None

        self.screen.blank_question_requested.connect(self.on_blank_question_requested)
        self.screen.duplicate_requested.connect(self.on_duplicate_requested)
        self.screen.delete_requested.connect(self.on_delete_requested)
        self.screen.question_reorder_requested.connect(
            self.on_question_reorder_requested
        )

    def on_blank_question_requested(self) -> None:
        question = Question(Question.generate_random_id(), "", [], None, 20)
        index = self.quiz.add_question(question)

        self.screen.add_question_widgets(question, index + 1)

    def on_duplicate_requested(self, question: Question) -> None:
        duplicate = deepcopy(question)
        duplicate.question_id = Question.generate_random_id()

        index = self.quiz.get_question_index(question.question_id)

        # Internal question indexes are 0-based, but UI is 1-based
        # We want the new question to be one ahead of the original
        self.quiz.add_question(duplicate, index + 1)
        self.screen.add_question_widgets(duplicate, index + 2)

        self.screen.update_question_order()

    def on_delete_requested(self, question: Question) -> None:
        if len(self.quiz.get_all_questions()) == 1:
            # Ordinarily, this should never happen
            self.show_error(
                "Cannot Delete Question", "Cannot delete the only question."
            )
            return

        questions = self.quiz.get_all_questions()

        next_question = None
        index = questions.index(question)

        # Prefer the next question, otherwise the previous one if ending question was removed
        if index < len(questions) - 1:
            next_question = questions[index + 1]
        else:
            next_question = questions[index - 1]

        self.quiz.remove_question(question.question_id)
        self.screen.remove_question_widgets(question, next_question)

    def on_question_reorder_requested(
        self, question: Question, new_question_num: int
    ) -> None:
        self.quiz.move_question(question.question_id, new_question_num - 1)
        self.screen.update_question_order()

    def on_enter(self, payload=None):
        if self.screen.returning_from_preview:
            return

        self.quiz = payload["quiz"]
        self.mode = "edit" if self.quiz.get_all_questions() else "create"

        self.screen.set_quiz(self.quiz, deepcopy(self.quiz), self.mode)

        if self.mode == "create":
            self.on_blank_question_requested()
