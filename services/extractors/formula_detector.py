"""
Knowledge Factory

Generic Formula Detector
"""

from __future__ import annotations

import re


class FormulaDetector:
    """
    Conservative detector for formula-like mathematical text.

    This class detects expressions only.
    It does not interpret or solve them.
    """

    FORMULA_PATTERNS = (
        re.compile(r"^[A-Za-z]\s*=\s*.+$"),
        re.compile(r"^[A-Za-z]\s*[\+\-\*/]\s*[A-Za-z].+$"),
        re.compile(r".*\b[A-Za-z]\s*=\s*[^.]+$"),
        re.compile(r".*[²³⁴⁵].*"),
        re.compile(r".*√.*"),
        re.compile(r".*∑.*"),
        re.compile(r".*∏.*"),
        re.compile(r".*≤.*"),
        re.compile(r".*≥.*"),
        re.compile(r".*≠.*"),
    )

    @classmethod
    def is_formula(
        cls,
        text: str,
    ) -> bool:

        text = text.strip()

        if not text:
            return False

        return any(
            pattern.match(text)
            for pattern in cls.FORMULA_PATTERNS
        )