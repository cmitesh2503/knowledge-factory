"""
Knowledge Factory

Generic Exercise Detector
"""

from __future__ import annotations

import re


class ExerciseDetector:
    """
    Conservative detector for exercise containers and questions.

    Supports textbook structures such as:

        EXERCISE 3.3
        1. Find the transpose...
        2. If A=...

    and explicit structures such as:

        Exercise 3.3
        Question 1: ...
    """

    EXERCISE_PATTERNS = (
        re.compile(
            r"^\s*exercise\s+(\d+(?:\.\d+)*)\s*$",
            re.IGNORECASE,
        ),
        re.compile(
            r"^\s*exercise\s+(\d+(?:\.\d+)*)\s*[:\-]\s*(.+)$",
            re.IGNORECASE,
        ),
    )

    QUESTION_PATTERNS = (
        # Explicit Question marker
        re.compile(
            r"^\s*question\s+(\d+(?:\.\d+)*)\s*[:\-]\s*(.*)$",
            re.IGNORECASE,
        ),

        # Textbook numbered question:
        # 1. Find ...
        # 2. If ...
        # 10. Express ...
        re.compile(
            r"^\s*(\d+)\.\s+(.+)$",
            re.IGNORECASE,
        ),
    )

    @classmethod
    def detect(
        cls,
        text: str,
    ) -> tuple[str, str | None, str] | None:
        """
        Returns:

            ("exercise", number, title)
            ("question", number, question)

        Returns None when no marker is detected.
        """

        text = text.strip()

        if not text:
            return None

        # --------------------------------------------------
        # Exercise container
        # --------------------------------------------------

        for pattern in cls.EXERCISE_PATTERNS:

            match = pattern.match(text)

            if not match:
                continue

            groups = match.groups()

            number = groups[0]

            title = ""

            if len(groups) > 1 and groups[1]:
                title = groups[1].strip()

            return "exercise", number, title

        # --------------------------------------------------
        # Question
        # --------------------------------------------------

        for pattern in cls.QUESTION_PATTERNS:

            match = pattern.match(text)

            if not match:
                continue

            groups = match.groups()

            number = groups[0]

            question = ""

            if len(groups) > 1 and groups[1]:
                question = groups[1].strip()

            return "question", number, question

        return None