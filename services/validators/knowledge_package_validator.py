"""
Knowledge Factory

Knowledge Package Validator
"""

from __future__ import annotations

from services.models import KnowledgePackage


class KnowledgePackageValidator:
    """
    Validates structural integrity and relationships
    inside a KnowledgePackage.
    """

    def validate(
        self,
        package: KnowledgePackage,
    ) -> list[str]:

        errors: list[str] = []

        # -------------------------------------------------
        # Basic package validation
        # -------------------------------------------------

        if not package.schema_version:
            errors.append(
                "Missing schema_version."
            )

        if not package.document_id:
            errors.append(
                "Missing document_id."
            )

        # -------------------------------------------------
        # Chapter validation
        # -------------------------------------------------

        chapter_numbers = {
            str(chapter.number)
            for chapter in package.chapters
        }

        if not chapter_numbers:
            errors.append(
                "KnowledgePackage contains no chapters."
            )

        # -------------------------------------------------
        # Section validation
        # -------------------------------------------------

        section_numbers = set()

        for section in package.sections:

            if not section.number:
                errors.append(
                    "Section missing number."
                )
                continue

            section_numbers.add(
                section.number
            )

            chapter_number = section.number.split(
                "."
            )[0]

            if chapter_number not in chapter_numbers:
                errors.append(
                    f"Section {section.number} "
                    f"does not belong to a known chapter."
                )

            # Validate parent relationship.
            if section.parent_number:

                if (
                    section.parent_number
                    not in section_numbers
                ):
                    errors.append(
                        f"Section {section.number} "
                        f"has unknown parent "
                        f"{section.parent_number}."
                    )

        # -------------------------------------------------
        # Concept relationships
        # -------------------------------------------------

        for concept in package.concepts:

            if (
                concept.section_number
                and concept.section_number
                not in section_numbers
            ):
                errors.append(
                    f"Concept {concept.id} references "
                    f"unknown section "
                    f"{concept.section_number}."
                )

        # -------------------------------------------------
        # Formula relationships
        # -------------------------------------------------

        for formula in package.formulas:

            if (
                formula.section_number
                and formula.section_number
                not in section_numbers
            ):
                errors.append(
                    f"Formula {formula.id} references "
                    f"unknown section "
                    f"{formula.section_number}."
                )

        # -------------------------------------------------
        # Example relationships
        # -------------------------------------------------

        for example in package.examples:

            if (
                example.section_number
                and example.section_number
                not in section_numbers
            ):
                errors.append(
                    f"Example {example.id} references "
                    f"unknown section "
                    f"{example.section_number}."
                )

        # -------------------------------------------------
        # Exercise relationships
        # -------------------------------------------------

        for exercise in package.exercises:

            if (
                exercise.section_number
                and exercise.section_number
                not in section_numbers
            ):
                errors.append(
                    f"Exercise {exercise.id} references "
                    f"unknown section "
                    f"{exercise.section_number}."
                )

            if not exercise.questions:
                errors.append(
                    f"Exercise {exercise.id} "
                    f"contains no questions."
                )

        return errors