from services.models.concept import Concept
from services.models.knowledge_package import KnowledgePackage
from services.repositories.firestore_knowledge_vector_index import (
    FirestoreKnowledgeVectorIndex,
)


class FakeDocumentReference:
    def __init__(
        self,
        document_id: str,
        storage: dict,
    ) -> None:
        self.document_id = document_id
        self.storage = storage

    def set(self, data: dict) -> None:
        self.storage[self.document_id] = data


class FakeSnapshot:
    def __init__(
        self,
        document_id: str,
        data: dict,
    ) -> None:
        self.id = document_id
        self._data = data

    def to_dict(self) -> dict:
        return self._data


class FakeVectorQuery:
    def __init__(
        self,
        documents: list[FakeSnapshot],
    ) -> None:
        self.documents = documents
        self.find_nearest_called = True
        self.where_calls = []
        self.stream_called = False

    def where(
        self,
        *,
        filter,
    ):
        self.where_calls.append(filter)
        return self

    def stream(self):
        self.stream_called = True
        return iter(self.documents)


class FakeCollection:
    def __init__(self) -> None:
        self.documents = {}
        self.vector_query = None

    def document(
        self,
        document_id: str,
    ) -> FakeDocumentReference:
        return FakeDocumentReference(
            document_id,
            self.documents,
        )

    def find_nearest(
        self,
        *,
        vector_field: str,
        query_vector: list[float],
        distance_measure,
        limit: int,
        distance_result_field: str,
    ) -> FakeVectorQuery:

        assert vector_field == "embedding"
        assert len(query_vector) == 768
        assert limit == 5
        assert distance_result_field == (
            "vector_distance"
        )

        self.vector_query = FakeVectorQuery(
            [
                FakeSnapshot(
                    "vec-001",
                    {
                        "document_id": "doc-001",
                        "source_id": "concept-001",
                        "knowledge_type": "concept",
                        "text": "What is a matrix?",
                        "metadata": {
                            "section_number": "3.1",
                        },
                        "vector_distance": 0.12,
                    },
                )
            ]
        )

        return self.vector_query


class FakeFirestoreClient:
    def __init__(self) -> None:
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


class FakeEmbeddingResponse:
    def __init__(
        self,
        values: list[float],
    ) -> None:
        self.embeddings = [
            type(
                "Embedding",
                (),
                {"values": values},
            )()
        ]


class FakeGenAIModels:
    def embed_content(
        self,
        *,
        model: str,
        contents: str,
        config: dict,
    ) -> FakeEmbeddingResponse:

        assert model == "gemini-embedding-001"
        assert contents

        assert (
            config["output_dimensionality"]
            == 768
        )

        return FakeEmbeddingResponse(
            [0.1] * 768
        )


class FakeGenAIClient:
    def __init__(self) -> None:
        self.models = FakeGenAIModels()


def create_package() -> KnowledgePackage:

    concept = Concept(
        id="concept-001",
        name="Matrices",
        section_number="3.1",
        page=10,
        block_id="block-001",
        metadata={
            "description": (
                "A matrix is a rectangular "
                "array of numbers."
            )
        },
    )

    return KnowledgePackage(
        schema_version="1.0",
        document_id="doc-001",
        concepts=[concept],
    )


def create_index():

    firestore_client = (
        FakeFirestoreClient()
    )

    embedding_client = (
        FakeGenAIClient()
    )

    index = FirestoreKnowledgeVectorIndex(
        client=firestore_client,
        genai_client=embedding_client,
        embedding_model=(
            "gemini-embedding-001"
        ),
        embedding_dimensions=768,
    )

    return index, firestore_client


def test_index_creates_vector_document():

    index, firestore_client = (
        create_index()
    )

    package = create_package()

    index.index(package)

    collection = (
        firestore_client.collections[
            "knowledge_vectors"
        ]
    )

    assert len(
        collection.documents
    ) == 1

    vector_document = next(
        iter(collection.documents.values())
    )

    assert (
        vector_document["document_id"]
        == "doc-001"
    )

    assert (
        vector_document["source_id"]
        == "concept-001"
    )

    assert (
        vector_document["knowledge_type"]
        == "concept"
    )

    assert (
        vector_document["text"]
        == (
            "Matrices "
            "A matrix is a rectangular "
            "array of numbers."
        )
    )

    assert len(
        vector_document["embedding"]
    ) == 768


def test_index_uses_deterministic_document_id():

    index, firestore_client = (
        create_index()
    )

    package = create_package()

    index.index(package)

    first_ids = set(
        firestore_client.collections[
            "knowledge_vectors"
        ].documents.keys()
    )

    index.index(package)

    second_ids = set(
        firestore_client.collections[
            "knowledge_vectors"
        ].documents.keys()
    )

    assert first_ids == second_ids
    assert len(second_ids) == 1


def test_index_rejects_empty_document_id():

    index, _ = create_index()

    package = KnowledgePackage(
        schema_version="1.0",
        document_id="",
    )

    try:
        index.index(package)

        assert False, (
            "Expected ValueError"
        )

    except ValueError as exc:
        assert "document_id" in str(exc)


def test_search_calls_firestore_vector_query():

    index, firestore_client = (
        create_index()
    )

    results = index.search(
        "What is a matrix?",
        top_k=5,
    )

    collection = (
        firestore_client.collections[
            "knowledge_vectors"
        ]
    )

    vector_query = collection.vector_query

    assert vector_query is not None
    assert vector_query.find_nearest_called
    assert vector_query.stream_called

    assert len(results) == 1

    result = results[0]

    assert result.document_id == "doc-001"
    assert result.source_id == "concept-001"
    assert result.knowledge_type == "concept"
    assert result.text == "What is a matrix?"
    assert result.distance == 0.12


def test_search_rejects_empty_query():

    index, _ = create_index()

    try:
        index.search("")

        assert False, (
            "Expected ValueError"
        )

    except ValueError as exc:
        assert "query" in str(exc)


def test_search_rejects_invalid_top_k():

    index, _ = create_index()

    try:
        index.search(
            "matrices",
            top_k=0,
        )

        assert False, (
            "Expected ValueError"
        )

    except ValueError as exc:
        assert "top_k" in str(exc)