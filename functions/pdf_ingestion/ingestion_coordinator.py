"""
PDF ingestion coordinator.

Coordinates PDF inspection and splitting before
Document AI processing.

This module does NOT call Document AI.
It only determines which PDF files should be processed.
"""

from pathlib import Path

from functions.pdf_ingestion.pdf_inspector import (
    inspect_pdf,
)
from functions.pdf_ingestion.pdf_splitter import (
    split_pdf,
)


class IngestionCoordinator:
    """
    Coordinates PDF inspection and splitting.

    Responsibilities
    ----------------
    - Inspect PDF page count
    - Determine whether splitting is required
    - Split oversized PDFs
    - Return PDFs ready for downstream processing

    Does NOT:
    - Call Document AI
    - Store data in Firestore
    - Build Knowledge Packs
    - Perform RAG
    """

    def __init__(
        self,
        max_pages: int = 25,
    ) -> None:

        if max_pages < 1:
            raise ValueError(
                "max_pages must be greater than zero."
            )

        self.max_pages = max_pages

    def prepare(
        self,
        file_path: str | Path,
        output_dir: str | Path | None = None,
    ) -> list[Path]:
        """
        Prepare a PDF for downstream Document AI processing.

        Returns
        -------
        list[Path]
            One or more PDF files ready for processing.
        """

        input_path = Path(file_path)

        inspection = inspect_pdf(
            input_path,
            max_pages=self.max_pages,
        )

        if not inspection.requires_split:

            return [input_path]

        if output_dir is None:

            output_dir = (
                input_path.parent
                / f"{input_path.stem}_chunks"
            )

        chunks = split_pdf(
            input_path,
            output_dir,
            max_pages=self.max_pages,
        )

        return chunks