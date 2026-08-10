"""
Knowledge Factory

Extraction Result

Standard result returned by all Knowledge Factory extractors.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

T = TypeVar("T")


@dataclass(slots=True)
class ExtractionResult(Generic[T]):
    """
    Standard result produced by an extractor.
    """

    items: list[T] = field(default_factory=list)

    warnings: list[str] = field(default_factory=list)

    errors: list[str] = field(default_factory=list)

    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def success(self) -> bool:
        return len(self.errors) == 0

    @property
    def count(self) -> int:
        return len(self.items)

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)

    def add_error(self, message: str) -> None:
        self.errors.append(message)

    def to_dict(self) -> dict[str, Any]:
        return {
            "count": self.count,
            "success": self.success,
            "warnings": self.warnings,
            "errors": self.errors,
            "metadata": self.metadata,
            "items": [
                item.to_dict() if hasattr(item, "to_dict") else item
                for item in self.items
            ],
        }