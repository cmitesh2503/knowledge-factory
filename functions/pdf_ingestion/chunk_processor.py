"""
Document AI chunk processor.

Processes each prepared PDF independently through
the existing Document AI service.

This component does NOT merge results.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ChunkProcessingResult:
    """
    Result of processing one PDF chunk.
    """

    chunk_path: Path
    chunk_index: int
    start_page: int
    end_page: int
    document_ai_result: object


class DocumentAIChunkProcessor:
    """
    Sends prepared PDF chunks to Document AI.

    Responsibilities
    ----------------
    - Process each PDF independently
    - Track chunk ordering
    - Track original page range
    - Return Document AI results

    Does NOT:
    - Merge results
    - Build canonical documents
    - Write Firestore
    - Build Knowledge Packages
    """

    def __init__(
        self,
        document_ai,
        max_pages: int = 25,
    ) -> None:

        if max_pages < 1:
            raise ValueError(
                "max_pages must be greater than zero."
            )

        self.document_ai = document_ai
        self.max_pages = max_pages

    def process(
        self,
        chunk_paths: list[Path],
    ) -> list[ChunkProcessingResult]:
        """
        Process every prepared PDF chunk through Document AI.

        Chunk ordering is determined by the order of
        chunk_paths supplied by IngestionCoordinator.
        """

        results: list[ChunkProcessingResult] = []

        for index, chunk_path in enumerate(
            chunk_paths,
            start=1,
        ):

            path = Path(chunk_path)

            if not path.exists():
                raise FileNotFoundError(
                    f"Chunk PDF not found: {path}"
                )

            start_page = (
                (index - 1) * self.max_pages
            ) + 1

            end_page = (
                start_page
                + self._page_count(path)
                - 1
            )

            document_ai_result = (
                self.document_ai.process_file(
                    path
                )
            )

            results.append(
                ChunkProcessingResult(
                    chunk_path=path,
                    chunk_index=index,
                    start_page=start_page,
                    end_page=end_page,
                    document_ai_result=document_ai_result,
                )
            )

        return results

    @staticmethod
    def _page_count(
        pdf_path: Path,
    ) -> int:

        from pypdf import PdfReader

        reader = PdfReader(
            str(pdf_path)
        )

        return len(reader.pages)