from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class TableCandidate:
    """
    Intermediate candidate discovered during table extraction.
    """

    id: str

    page: int | None = None

    rows: int = 0

    columns: int = 0

    cells: list[dict[str, Any]] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )