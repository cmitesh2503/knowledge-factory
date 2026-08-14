"""
Knowledge Factory

Generic Exercise Extractor
"""

from __future__ import annotations

from services.extractors.base_extractor import BaseExtractor
from services.extractors.exercise_detector import (
    ExerciseDetector,
)
from services.extractors.section_number_parser import (
    SectionNumberParser,
)
from services.models import (
    Exercise,
    ExerciseCandidate,
    ExerciseQuestion,
    ExerciseQuestionCandidate,
)

class ExerciseExtractor(
    BaseExtractor[
        ExerciseCandidate,
        Exercise,
    ]
):
    """
    Generic deterministic exercise extractor.

    BaseExtractor owns orchestration:

        find_candidates()
              ↓
        validate_candidates()
              ↓
        build()
    """

    def find_candidates(
        self,
        canonical_document: dict,
    ) -> list[ExerciseCandidate]:

        candidates: list[ExerciseCandidate] = []

        current_section: str | None = None
        current_exercise: ExerciseCandidate | None = None

        def flush_exercise() -> None:
            nonlocal current_exercise

            if current_exercise is not None:
                candidates.append(current_exercise)

            current_exercise = None

        for page in canonical_document.get(
            "pages",
            [],
        ):

            page_number = page.get("page_number")

            for block in page.get(
                "blocks",
                [],
            ):

                text = str(
                    block.get(
                        "text",
                        "",
                    )
                ).strip()

                if not text:
                    continue

                # Section boundary
                parsed = SectionNumberParser.parse(text)

                if parsed is not None:

                    flush_exercise()

                    section_number, _ = parsed

                    current_section = (
                        section_number.number
                    )

                    continue

                detected = ExerciseDetector.detect(text)

                if detected is None:
                    continue

                marker_type, number, content = detected

                # New exercise container
                if marker_type == "exercise":

                    flush_exercise()

                    current_exercise = ExerciseCandidate(
                        block_id=block["id"],
                        page_number=page_number,
                        number=number,
                        section_number=current_section,
                    )

                    continue

                # Question belonging to current exercise
                if (
                    marker_type == "question"
                    and current_exercise is not None
                ):

                    current_exercise.questions.append(
                        ExerciseQuestionCandidate(
                            block_id=block["id"],
                            page_number=page_number,
                            text=content,
                            number=number,
                        )
                    )

        flush_exercise()

        return candidates
    def validate_candidates(
        self,
        candidates: list[ExerciseCandidate],
    ) -> list[ExerciseCandidate]:

        validated: list[ExerciseCandidate] = []

        for candidate in candidates:

            # Exercise must have an identifier.
            if not candidate.number:
                continue

            # Exercise must contain at least one question.
            if not candidate.questions:
                continue

            # Remove empty questions.
            candidate.questions = [
                question
                for question in candidate.questions
                if question.text.strip()
            ]

            if not candidate.questions:
                continue

            validated.append(candidate)

        return validated

    def build(
        self,
        candidates: list[ExerciseCandidate],
    ) -> list[Exercise]:

        exercises: list[Exercise] = []

        for index, candidate in enumerate(
            candidates
        ):

            questions = [
                ExerciseQuestion(
                    number=question.number,
                    question=question.text,
                    block_id=question.block_id,
                    page=question.page_number,
                )
                for question in candidate.questions
            ]

            exercises.append(
                Exercise(
                    id=f"exercise-{index + 1:03}",
                    number=candidate.number,
                    section_number=(
                        candidate.section_number
                    ),
                    page=candidate.page_number,
                    block_id=candidate.block_id,
                    questions=questions,
                )
            )

        return exercises