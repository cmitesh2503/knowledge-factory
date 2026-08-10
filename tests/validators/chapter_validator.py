"""
Knowledge Factory

Golden Dataset Validator

Validates extracted Chapter objects against the
expected golden dataset.
"""

from services.models.chapter import Chapter


class ChapterValidator:

    def validate(
        self,
        actual: list[Chapter],
        expected: list[dict],
    ) -> list[str]:

        errors = []

        if len(actual) != len(expected):
            errors.append(
                f"Expected {len(expected)} chapters, got {len(actual)}."
            )
            return errors

        for chapter, exp in zip(actual, expected):

            if chapter.title != exp["title"]:
                errors.append(
                    f"Title mismatch: {chapter.title} != {exp['title']}"
                )

            if chapter.number != exp["number"]:
                errors.append(
                    f"Number mismatch: {chapter.number} != {exp['number']}"
                )

            if chapter.start_page != exp["start_page"]:
                errors.append(
                    "Start page mismatch."
                )

            if chapter.end_page != exp["end_page"]:
                errors.append(
                    "End page mismatch."
                )

        return errors