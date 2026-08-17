from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Table:
    """
    Provider-independent educational table.
    """

    id: str

    rows: int = 0

    columns: int = 0

    cells: list[dict[str, Any]] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "rows": self.rows,
            "columns": self.columns,
            "cells": self.cells,
            "metadata": self.metadata,
        }