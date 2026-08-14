"""
Knowledge Factory

Generic Example Detector
"""

from __future__ import annotations

import re


class ExampleDetector:
    """
    Detects explicit worked-example markers.

    This detector intentionally uses conservative rules.
    It does not infer examples from arbitrary prose.
    """

    PATTERNS = (
        re.compile(
            r"^\s*example\s+(\d+(?:\.\d+)*)\s*$",
            re.IGNORECASE,
        ),
        re.compile(
            r"^\s*example\s+(\d+(?:\.\d+)*)\s*[:\-]\s*(.+)$",
            re.IGNORECASE,
        ),
        re.compile(
            r"^\s*solved\s+example\s+(\d+(?:\.\d+)*)\s*$",
            re.IGNORECASE,
        ),
        re.compile(
            r"^\s*illustration\s+(\d+(?:\.\d+)*)\s*$",
            re.IGNORECASE,
        ),
    )

    @classmethod
    def detect(
        cls,
        text: str,
    ) -> tuple[str | None, str | None] | None:

        text = text.strip()

        if not text:
            return None

        for pattern in cls.PATTERNS:

            match = pattern.match(text)

            if not match:
                continue

            groups = match.groups()

            number = groups[0]

            title = text

            if len(groups) > 1 and groups[1]:
                title = groups[1].strip()

            return number, title

        return None