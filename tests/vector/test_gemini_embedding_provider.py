from services.vector.gemini_embedding_provider import (
    GeminiEmbeddingProvider,
)


class FakeEmbeddingResponse:
    def __init__(
        self,
        values: list[float],
    ) -> None:

        self.embeddings = [
            type(
                "Embedding",
                (),
                {
                    "values": values,
                },
            )()
        ]


class FakeModels:

    def embed_content(
        self,
        *,
        model: str,
        contents: str,
        config: dict,
    ) -> FakeEmbeddingResponse:

        assert model == (
            "gemini-embedding-001"
        )

        assert contents

        assert (
            config[
                "output_dimensionality"
            ]
            == 768
        )

        return FakeEmbeddingResponse(
            [0.1] * 768
        )


class FakeGenAIClient:

    def __init__(self) -> None:

        self.models = FakeModels()


def test_gemini_embedding_provider():

    provider = (
        GeminiEmbeddingProvider(
            client=FakeGenAIClient(),
            embedding_model=(
                "gemini-embedding-001"
            ),
            embedding_dimensions=768,
        )
    )

    embeddings = provider.embed(
        [
            "What is a matrix?",
            "What is a determinant?",
        ]
    )

    assert len(embeddings) == 2

    assert len(
        embeddings[0]
    ) == 768

    assert len(
        embeddings[1]
    ) == 768


def test_gemini_embedding_provider_returns_empty_for_empty_batch():

    provider = (
        GeminiEmbeddingProvider(
            client=FakeGenAIClient(),
        )
    )

    embeddings = provider.embed(
        []
    )

    assert embeddings == []


def test_gemini_embedding_provider_rejects_empty_text():

    provider = (
        GeminiEmbeddingProvider(
            client=FakeGenAIClient(),
        )
    )

    try:

        provider.embed(
            [""]
        )

        assert False, (
            "Expected ValueError"
        )

    except ValueError as exc:

        assert "empty" in str(
            exc
        ).lower()