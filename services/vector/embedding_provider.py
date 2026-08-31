from __future__ import annotations

from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    """
    Provider-independent interface for generating
    vector embeddings.
    """

    @abstractmethod
    def embed(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        Generate embeddings for a batch of texts.
        """

        raise NotImplementedError