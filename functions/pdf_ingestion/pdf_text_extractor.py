"""
Native PDF text extraction fallback.

Extracts text directly from a PDF using pypdf and converts
the result into Knowledge Factory canonical blocks.

This module does not persist provider-specific data.
"""

from pathlib import Path

from pypdf import PdfReader


class PDFTextExtractor:
    """
    Extract page-level text from PDFs.

    Used as a fallback when the primary extraction provider
    does not produce sufficient document coverage.
    """

    def extract_blocks(
        self,
        file_path: str | Path,
    ) -> list[dict]:
        """
        Extract canonical text blocks from a PDF.

        One canonical paragraph block is produced for each
        page containing extractable text.
        """

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"PDF file not found: {path}"
            )

        reader = PdfReader(path)

        blocks: list[dict] = []

        for page_number, page in enumerate(
            reader.pages,
            start=1,
        ):

            text = (
                page.extract_text()
                or ""
            ).strip()

            if not text:
                continue

            blocks.append(
                {
                    "type": "paragraph",
                    "text": text,
                    "page": page_number,
                    "confidence": None,
                    "geometry": {},
                    "metadata": {
                        "extraction_source": (
                            "pdf_native_text"
                        ),
                    },
                }
            )

        return blocks
    def page_count(
        self,
        file_path: str | Path,
    ) -> int:
        """
        Return the total number of pages in a PDF.

        This is independent of whether individual pages
        contain extractable text.
        """

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"PDF file not found: {path}"
            )

        reader = PdfReader(path)

        return len(reader.pages)