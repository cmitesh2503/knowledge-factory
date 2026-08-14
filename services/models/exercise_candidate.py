"""
Knowledge Factory

Exercise Candidate
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ExerciseQuestionCandidate:
    """
    Candidate question belonging to an exercise.
    """

    block_id: str

    page_number: int

    text: str

    number: str | None


@dataclass(slots=True)
class ExerciseCandidate:
    """
    Candidate exercise container.
    """

    block_id: str

    page_number: int

    number: str | None

    section_number: str | None

    questions: list[ExerciseQuestionCandidate] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )