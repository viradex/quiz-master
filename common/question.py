from dataclasses import dataclass


# TODO is this gonna be used or not??
@dataclass
class Question:
    question: str
    choices: list[str]
    answer_index: int
