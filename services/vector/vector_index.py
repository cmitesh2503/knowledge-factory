from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class VectorIndex(ABC):
    """
    Provider-independent abstraction for storing
    and searching vectorized knowledge chunks.
    """

    @abstractmethod
    def upsert(
        self,
        records: list[dict[str, Any]],
    ) -> None:
        """
        Insert or update vector records.
        """

        raise NotImplementedError

    @abstractmethod
    def search(
        self,
        vector: list[float],
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Search for the nearest vector records.
        """

        raise NotImplementedError