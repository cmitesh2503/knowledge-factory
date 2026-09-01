from services.composition.knowledge_factory import (
    KnowledgeFactoryApplication,
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


class FakeGenAIModels:
    def embed_content(
        self,
        *,
        model: str,
        contents,
        config: dict,
    ) -> FakeEmbeddingResponse:

        return FakeEmbeddingResponse(
            [0.1] * config[
                "output_dimensionality"
            ]
        )


class FakeGenAIClient:
    def __init__(
        self,
    ) -> None:

        self.models = FakeGenAIModels()


class FakeDocumentReference:
    def __init__(
        self,
        document_id: str,
        storage: dict,
    ) -> None:

        self.document_id = document_id
        self.storage = storage

    def set(
        self,
        data: dict,
    ) -> None:

        self.storage[
            self.document_id
        ] = data


class FakeCollection:
    def __init__(
        self,
    ) -> None:

        self.documents = {}

    def document(
        self,
        document_id: str,
    ) -> FakeDocumentReference:

        return FakeDocumentReference(
            document_id,
            self.documents,
        )


class FakeFirestoreClient:
    def __init__(
        self,
    ) -> None:

        self.collections = {}

    def collection(
        self,
        name: str,
    ) -> FakeCollection:

        if name not in self.collections:

            self.collections[name] = (
                FakeCollection()
            )

        return self.collections[name]


def test_knowledge_factory_application_wires_services():

    application = (
        KnowledgeFactoryApplication(
            firestore_client=(
                FakeFirestoreClient()
            ),
            genai_client=(
                FakeGenAIClient()
            ),
        )
    )

    assert (
        application.embedding_provider
        is not None
    )

    assert (
        application.vector_index
        is not None
    )

    assert (
        application.vector_indexing_service
        is not None
    )

    assert (
        application.knowledge_search_service
        is not None
    )

    assert (
        application.knowledge_retrieval_service
        is not None
    )

    assert (
        application.mathverse_retrieval_adapter
        is not None
    )