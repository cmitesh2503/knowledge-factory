"""
Knowledge Factory

Educational Heading Classifier

Determines whether a canonical block is an educational heading.

This component is provider-independent and reusable by all extractors.
"""

from __future__ import annotations


class HeadingClassifier:

    HEADING_TYPES = {
        "heading",
    }

    KEYWORDS = {
        "chapter",
        "exercise",
        "example",
        "activity",
        "summary",
        "review",
        "theorem",
        "definition",
    }

    def is_heading(self, block: dict) -> bool:
        """
        Determine whether a canonical block should be treated as
        an educational heading.
        """

        if not block:
            return False

        # -------------------------------------------------
        # Rule 1
        # Canonical heading block
        # -------------------------------------------------

        if block.get("type") in self.HEADING_TYPES:
            return True

        text = str(block.get("text", "")).strip()

        if not text:
            return False

        # -------------------------------------------------
        # Rule 2
        # Very long text is not a heading
        # -------------------------------------------------

        if len(text) > 120:
            return False

        # -------------------------------------------------
        # Rule 3
        # Keyword detection
        # -------------------------------------------------

        lower = text.lower()

        for keyword in self.KEYWORDS:
            if lower.startswith(keyword):
                return True

        # -------------------------------------------------
        # Rule 4
        # All uppercase headings
        # -------------------------------------------------

        if text.isupper() and len(text.split()) <= 8:
            return True

        # -------------------------------------------------
        # Rule 5
        # Short title
        # -------------------------------------------------

        if (
            len(text.split()) <= 8
            and text[0].isupper()
            and not text.endswith(".")
        ):
            return True

        return False