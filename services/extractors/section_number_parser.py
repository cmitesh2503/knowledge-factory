"""
Knowledge Factory

Generic Section Number Parser
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ParsedSectionNumber:
    number: str
    level: int
    parent_number: str | None


class SectionNumberParser:
    """
    Parses hierarchical numeric section numbers.

    Examples:

        3.1
        3.2
        3.2.1
        3.2.1.1
    """

    PATTERN = re.compile(
        r"^(\d+(?:\.\d+)+)\s+(.+?)\s*$"
    )

    @classmethod
    def parse(
        cls,
        text: str,
    ) -> tuple[ParsedSectionNumber, str] | None:

        text = text.strip()

        match = cls.PATTERN.match(text)

        if not match:
            return None

        number = match.group(1)
        title = match.group(2).strip()

        parts = number.split(".")

        level = len(parts) - 1

        parent_number = None

        if level > 1:
            parent_number = ".".join(parts[:-1])

        return (
            ParsedSectionNumber(
                number=number,
                level=level,
                parent_number=parent_number,
            ),
            title,
        )