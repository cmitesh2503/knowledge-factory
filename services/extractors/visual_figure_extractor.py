"""
Knowledge Factory

Visual Figure Extractor

Provides the Phase B visual extraction boundary for source PDFs.

This component operates on the original PDF rather than the
canonical text document. It prepares provider-independent visual
page information that later figure-detection stages can use.

Responsibilities in Phase B Step 1:

- Open a source PDF.
- Inspect the complete document, not a chapter or section.
- Expose every page as a visual extraction unit.
- Preserve page dimensions.
- Preserve page numbering.
- Preserve source-document provenance.
- Provide rendered page bytes for later visual analysis.
- Avoid figure classification or semantic interpretation.

This component does not:

- depend on Google Document AI or Azure Document Intelligence
- classify figures
- infer geometry
- infer educational relevance
- create Figure objects
- create FigureCandidate objects
- modify the canonical text extraction pipeline

Later Phase B stages can consume the page-level visual units
created here.
"""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Iterator


@dataclass(slots=True)
class VisualPage:
    """
    Provider-independent visual representation of one PDF page.

    Page numbers are one-based to remain consistent with the
    canonical document model and human-readable PDF references.
    """

    page_number: int
    width: float
    height: float
    image_bytes: bytes
    mime_type: str = "image/png"

    @property
    def image_size(self) -> int:
        """Return the rendered image size in bytes."""
        return len(self.image_bytes)


class VisualFigureExtractor:
    """
    Prepare the complete source PDF for visual figure extraction.

    Phase B Step 1 establishes the visual-input boundary only.

    The extractor renders every page independently so later stages
    can detect visual regions without coupling the figure pipeline
    to a particular document-analysis provider.
    """

    def __init__(
        self,
        *,
        dpi: int = 150,
    ) -> None:
        if dpi <= 0:
            raise ValueError("dpi must be greater than zero")

        self.dpi = dpi

    def extract(
        self,
        pdf_path: str | Path,
    ) -> list[VisualPage]:
        """
        Render every page of the source PDF.

        The complete document is processed. No chapter, section,
        or topic-specific filtering is performed.
        """
        path = Path(pdf_path)

        if not path.is_file():
            raise FileNotFoundError(
                f"Source PDF not found: {path}"
            )

        try:
            import fitz
        except ImportError as exc:
            raise RuntimeError(
                "PyMuPDF is required for visual PDF extraction."
            ) from exc

        pages: list[VisualPage] = []

        with fitz.open(path) as document:
            scale = self.dpi / 72.0
            matrix = fitz.Matrix(scale, scale)

            for index, page in enumerate(document):
                pixmap = page.get_pixmap(
                    matrix=matrix,
                    alpha=False,
                )

                image_bytes = pixmap.tobytes(
                    "png"
                )

                pages.append(
                    VisualPage(
                        page_number=index + 1,
                        width=float(page.rect.width),
                        height=float(page.rect.height),
                        image_bytes=image_bytes,
                    )
                )

        return pages

    def iter_pages(
        self,
        pdf_path: str | Path,
    ) -> Iterator[VisualPage]:
        """
        Lazily render pages from the complete source PDF.

        This is useful for production documents because callers do
        not need to hold every rendered page in memory at once.
        """
        path = Path(pdf_path)

        if not path.is_file():
            raise FileNotFoundError(
                f"Source PDF not found: {path}"
            )

        try:
            import fitz
        except ImportError as exc:
            raise RuntimeError(
                "PyMuPDF is required for visual PDF extraction."
            ) from exc

        with fitz.open(path) as document:
            scale = self.dpi / 72.0
            matrix = fitz.Matrix(scale, scale)

            for index, page in enumerate(document):
                pixmap = page.get_pixmap(
                    matrix=matrix,
                    alpha=False,
                )

                yield VisualPage(
                    page_number=index + 1,
                    width=float(page.rect.width),
                    height=float(page.rect.height),
                    image_bytes=pixmap.tobytes(
                        "png"
                    ),
                )