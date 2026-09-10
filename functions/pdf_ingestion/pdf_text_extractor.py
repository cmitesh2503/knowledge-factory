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
    Extract text directly from a PDF.

    Used as a fallback when the primary extraction provider
    does not produce sufficient document coverage.

    The extractor creates line-level canonical blocks instead
    of one large block per page so downstream structural
    extractors can identify chapters, sections, formulas,
    examples, and exercises.
    """

    def extract_blocks(
        self,
        file_path: str | Path,
    ) -> list[dict]:
        """
        Extract line-level canonical text blocks from a PDF.

        Each non-empty extracted line becomes a canonical
        text block.
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

            page_text = (
                page.extract_text()
                or ""
            )

            lines = [
                line.strip()
                for line in page_text.splitlines()
                if line.strip()
            ]

            for line in lines:

                blocks.append(
                    {
                        "type": "text",
                        "text": line,
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