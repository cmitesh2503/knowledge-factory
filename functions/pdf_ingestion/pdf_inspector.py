"""
PDF inspection utilities.

Determines whether a PDF must be split before
being submitted to Google Document AI.
"""

from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


DEFAULT_MAX_PAGES = 25


@dataclass(frozen=True)
class PDFInspection:
    """
    Result of inspecting a PDF.
    """

    file_path: str
    page_count: int
    max_pages: int
    requires_split: bool


def inspect_pdf(
    file_path: str | Path,
    max_pages: int = DEFAULT_MAX_PAGES,
) -> PDFInspection:
    """
    Inspect a PDF and determine whether it exceeds
    the configured Document AI page limit.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"PDF file does not exist: {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"PDF path is not a file: {path}"
        )

    if path.suffix.lower() != ".pdf":
        raise ValueError(
            f"Expected a PDF file: {path}"
        )

    if max_pages < 1:
        raise ValueError(
            "max_pages must be greater than zero."
        )

    reader = PdfReader(str(path))

    page_count = len(reader.pages)

    return PDFInspection(
        file_path=str(path),
        page_count=page_count,
        max_pages=max_pages,
        requires_split=page_count > max_pages,
    )