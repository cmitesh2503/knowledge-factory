"""
Knowledge Factory

Generic Example Detector
"""

from __future__ import annotations

import re


class ExampleDetector:
    """
    Detect explicit worked-example markers.

    Supports canonical OCR text such as:

        Example 20
        Example 20 If
        Example 21 If A=...
        Solved Example 1
        Illustration 2
    """

    PATTERNS = (
        re.compile(
            r"^\s*example\s+(\d+(?:\.\d+)*)\b(.*)$",
            re.IGNORECASE,
        ),
        re.compile(
            r"^\s*solved\s+example\s+(\d+(?:\.\d+)*)\b(.*)$",
            re.IGNORECASE,
        ),
        re.compile(
            r"^\s*illustration\s+(\d+(?:\.\d+)*)\b(.*)$",
            re.IGNORECASE,
        ),
    )

    @classmethod
    def detect(
        cls,
        text: str,
    ) -> tuple[str | None, str] | None:
        """
        Detect an explicit example marker.

        Returns:

            (number, title)

        Examples:

            Example 20
                -> ("20", "")

            Example 21 If A=...
                -> ("21", "If A=...")

        Returns None when no marker is detected.
        """

        text = str(text or "").strip()

        if not text:
            return None

        for pattern in cls.PATTERNS:

            match = pattern.match(text)

            if not match:
                continue

            number = match.group(1)

            remainder = (
                match.group(2) or ""
            ).strip()

            return number, remainder

        return None
