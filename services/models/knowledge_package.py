from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from services.models import (
    Chapter,
    Section,
    Concept,
    Formula,
    Example,
    Exercise,
)


@dataclass(slots=True)
class KnowledgePackage:
    """
    Unified provider-independent knowledge representation.
    """

    schema_version: str

    document_id: str

    chapters: list[Chapter] = field(default_factory=list)

    sections: list[Section] = field(default_factory=list)

    concepts: list[Concept] = field(default_factory=list)

    formulas: list[Formula] = field(default_factory=list)

    examples: list[Example] = field(default_factory=list)

    exercises: list[Exercise] = field(default_factory=list)

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "document_id": self.document_id,
            "chapters": [
                item.to_dict()
                for item in self.chapters
            ],
            "sections": [
                item.to_dict()
                for item in self.sections
            ],
            "concepts": [
                item.to_dict()
                for item in self.concepts
            ],
            "formulas": [
                item.to_dict()
                for item in self.formulas
            ],
            "examples": [
                item.to_dict()
                for item in self.examples
            ],
            "exercises": [
                item.to_dict()
                for item in self.exercises
            ],
            "metadata": self.metadata,
        }