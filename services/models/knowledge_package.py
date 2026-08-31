from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from services.models.chapter import Chapter
from services.models.section import Section
from services.models.concept import Concept
from services.models.formula import Formula
from services.models.example import Example
from services.models.exercise import (
    Exercise,
    ExerciseQuestion,
)
from services.models.figure import Figure
from services.models.table import Table


@dataclass(slots=True)
class KnowledgePackage:
    """
    Unified provider-independent knowledge representation.
    """

    schema_version: str

    document_id: str

    chapters: list[Chapter] = field(
        default_factory=list
    )

    sections: list[Section] = field(
        default_factory=list
    )

    concepts: list[Concept] = field(
        default_factory=list
    )

    formulas: list[Formula] = field(
        default_factory=list
    )

    examples: list[Example] = field(
        default_factory=list
    )

    exercises: list[Exercise] = field(
        default_factory=list
    )

    figures: list[Figure] = field(
        default_factory=list
    )
    tables: list[Table] = field(
        default_factory=list
    )

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
            "figures": [
                item.to_dict()
                for item in self.figures
            ],
            "tables": [
                item.to_dict()
                for item in self.tables
            ],
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "KnowledgePackage":
        """
        Reconstruct a KnowledgePackage from its
        provider-independent dictionary representation.
        """

        exercises = []

        for item in data.get(
            "exercises",
            [],
        ):
            questions = [
                ExerciseQuestion(
                    number=question.get(
                        "number"
                    ),
                    question=question.get(
                        "question",
                        "",
                    ),
                    block_id=question.get(
                        "block_id",
                        "",
                    ),
                    page=question.get(
                        "page",
                        1,
                    ),
                    metadata=question.get(
                        "metadata",
                        {},
                    ),
                )
                for question in item.get(
                    "questions",
                    [],
                )
            ]

            exercises.append(
                Exercise(
                    id=item.get(
                        "id",
                        "",
                    ),
                    number=item.get(
                        "number"
                    ),
                    section_number=item.get(
                        "section_number"
                    ),
                    page=item.get(
                        "page",
                        1,
                    ),
                    block_id=item.get(
                        "block_id",
                        "",
                    ),
                    questions=questions,
                    metadata=item.get(
                        "metadata",
                        {},
                    ),
                )
            )

        return cls(
            schema_version=data.get(
                "schema_version",
                "1.0",
            ),
            document_id=data.get(
                "document_id",
                "",
            ),
            chapters=[
                Chapter(
                    id=item.get("id", ""),
                    title=item.get(
                        "title",
                        "",
                    ),
                    number=item.get(
                        "number"
                    ),
                    start_page=item.get(
                        "start_page",
                        1,
                    ),
                    end_page=item.get(
                        "end_page",
                        1,
                    ),
                    block_ids=item.get(
                        "block_ids",
                        [],
                    ),
                    metadata=item.get(
                        "metadata",
                        {},
                    ),
                )
                for item in data.get(
                    "chapters",
                    [],
                )
            ],
            sections=[
                Section(
                    id=item.get("id", ""),
                    number=item.get(
                        "number",
                        "",
                    ),
                    title=item.get(
                        "title",
                        "",
                    ),
                    level=item.get(
                        "level",
                        1,
                    ),
                    parent_number=item.get(
                        "parent_number"
                    ),
                    page=item.get(
                        "page",
                        1,
                    ),
                    block_id=item.get(
                        "block_id",
                        "",
                    ),
                    metadata=item.get(
                        "metadata",
                        {},
                    ),
                )
                for item in data.get(
                    "sections",
                    [],
                )
            ],
            concepts=[
                Concept(
                    id=item.get("id", ""),
                    name=item.get(
                        "name",
                        "",
                    ),
                    section_number=item.get(
                        "section_number"
                    ),
                    page=item.get(
                        "page",
                        1,
                    ),
                    block_id=item.get(
                        "block_id",
                        "",
                    ),
                    metadata=item.get(
                        "metadata",
                        {},
                    ),
                )
                for item in data.get(
                    "concepts",
                    [],
                )
            ],
            formulas=[
                Formula(
                    id=item.get("id", ""),
                    expression=item.get(
                        "expression",
                        "",
                    ),
                    section_number=item.get(
                        "section_number"
                    ),
                    page=item.get(
                        "page",
                        1,
                    ),
                    block_id=item.get(
                        "block_id",
                        "",
                    ),
                    metadata=item.get(
                        "metadata",
                        {},
                    ),
                )
                for item in data.get(
                    "formulas",
                    [],
                )
            ],
            examples=[
                Example(
                    id=item.get("id", ""),
                    number=item.get(
                        "number"
                    ),
                    title=item.get(
                        "title"
                    ),
                    content=item.get(
                        "content",
                        [],
                    ),
                    section_number=item.get(
                        "section_number"
                    ),
                    page=item.get(
                        "page",
                        1,
                    ),
                    block_id=item.get(
                        "block_id",
                        "",
                    ),
                    metadata=item.get(
                        "metadata",
                        {},
                    ),
                )
                for item in data.get(
                    "examples",
                    [],
                )
            ],
            exercises=exercises,
            figures=[
                Figure(
                    id=item.get("id", ""),
                    caption=item.get(
                        "caption"
                    ),
                    description=item.get(
                        "description"
                    ),
                    related_concepts=item.get(
                        "related_concepts",
                        [],
                    ),
                    metadata=item.get(
                        "metadata",
                        {},
                    ),
                )
                for item in data.get(
                    "figures",
                    [],
                )
            ],
            tables=[
                Table(
                    id=item.get(
                        "id",
                        "",
                    ),
                    rows=item.get(
                        "rows",
                        0,
                    ),
                    columns=item.get(
                        "columns",
                        0,
                    ),
                    cells=list(
                        item.get(
                            "cells",
                            [],
                        )
                    ),
                    metadata=item.get(
                        "metadata",
                        {},
                    ),
                )
                for item in data.get(
                    "tables",
                    [],
                )
            ],
            metadata=data.get(
                "metadata",
                {},
            ),
        )