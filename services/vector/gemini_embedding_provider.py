from __future__ import annotations

from google import genai

from services.vector.embedding_provider import (
    EmbeddingProvider,
)


class GeminiEmbeddingProvider(
    EmbeddingProvider
):
    """
    Google Gemini implementation of EmbeddingProvider.

    Generates embeddings without exposing Gemini-specific
    details to indexing or search services.
    """

    def __init__(
        self,
        client: genai.Client | None = None,
        embedding_model: str = (
            "gemini-embedding-001"
        ),
        embedding_dimensions: int = 768,
    ) -> None:

        self.client = (
            client
            if client is not None
            else genai.Client()
        )

        self.embedding_model = (
            embedding_model
        )

        self.embedding_dimensions = (
            embedding_dimensions
        )

    def embed(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        Generate embeddings for a batch of texts.
        """

        if not texts:
            return []

        embeddings: list[list[float]] = []

        for text in texts:

            if not text.strip():
                raise ValueError(
                    "Embedding text cannot be empty."
                )

            response = (
                self.client.models.embed_content(
                    model=self.embedding_model,
                    contents=text,
                    config={
                        "output_dimensionality": (
                            self.embedding_dimensions
                        ),
                    },
                )
            )

            if not response.embeddings:
                raise RuntimeError(
                    "Embedding API returned no embeddings."
                )

            values = (
                response.embeddings[0].values
            )

            if values is None:
                raise RuntimeError(
                    "Embedding API returned empty vector."
                )

            embeddings.append(
                list(values)
            )

        return embeddings