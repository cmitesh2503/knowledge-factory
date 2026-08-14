"""
Knowledge Factory

Exercise Domain Model
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ExerciseQuestion:
    """
    A question belonging to an exercise.
    """

    number: str | None

    question: str

    block_id: str

    page: int

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "number": self.number,
            "question": self.question,
            "block_id": self.block_id,
            "page": self.page,
            "metadata": self.metadata,
        }


@dataclass(slots=True)
class Exercise:
    """
    Provider-independent textbook exercise.

    An exercise is a container for one or more
    student questions.
    """

    id: str

    number: str | None

    section_number: str | None

    page: int

    block_id: str

    questions: list[ExerciseQuestion] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "number": self.number,
            "section_number": self.section_number,
            "page": self.page,
            "block_id": self.block_id,
            "questions": [
                question.to_dict()
                for question in self.questions
            ],
            "metadata": self.metadata,
        }