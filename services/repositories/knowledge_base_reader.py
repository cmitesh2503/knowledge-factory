from abc import ABC, abstractmethod

from services.models.knowledge_package import KnowledgePackage


class KnowledgeBaseReader(ABC):
    """
    Provider-independent read boundary for the Knowledge Base.

    Consumers such as MathVerse should depend on this
    interface rather than directly depending on Firestore.
    """

    @abstractmethod
    def get_package(
        self,
        document_id: str,
    ) -> KnowledgePackage | None:
        """
        Retrieve a KnowledgePackage by document ID.

        Returns None when the package does not exist.
        """
        raise NotImplementedError