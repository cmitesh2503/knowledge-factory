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

    Supported forms:

        3.1 Introduction
        3.2 Matrix
        3.2.1 Order of a matrix

    Also supports punctuation after the section number:

        3.5. Transpose of a Matrix
        3.5.1. Properties of transpose

    The punctuation is not part of the section number.
    """

    PATTERN = re.compile(
        r"^(\d+(?:\.\d+)+)\.?\s+(.+?)\s*$"
    )

    @classmethod
    def parse(
        cls,
        text: str,
    ) -> tuple[ParsedSectionNumber, str] | None:

        text = text.strip()

        if not text:
            return None

        match = cls.PATTERN.match(text)

        if match is None:
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