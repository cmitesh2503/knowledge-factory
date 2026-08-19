from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class KnowledgeSearchResult:
    """
    Provider-independent result returned by knowledge search.
    """

    document_id: str

    source_id: str

    knowledge_type: str

    text: str

    distance: float | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )