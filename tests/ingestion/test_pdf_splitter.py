from pathlib import Path
import fitz

from pypdf import PdfReader, PdfWriter

from functions.pdf_ingestion.pdf_splitter import (
    split_pdf,
)
import pymupdf


def create_test_pdf(
    path: Path,
    page_count: int,
) -> None:

    writer = PdfWriter()

    for _ in range(page_count):
        writer.add_blank_page(
            width=612,
            height=792,
        )

    with path.open("wb") as file:
        writer.write(file)


def test_pdf_is_split_into_25_page_chunks(
    tmp_path,
):

    source_pdf = (
        tmp_path / "Matrices.pdf"
    )

    output_dir = (
        tmp_path / "chunks"
    )

    create_test_pdf(
        source_pdf,
        page_count=42,
    )

    chunks = split_pdf(
        source_pdf,
        output_dir,
    )

    assert len(chunks) == 2

    first = PdfReader(
        str(chunks[0])
    )

    second = PdfReader(
        str(chunks[1])
    )

    assert len(first.pages) == 25

    assert len(second.pages) == 17


def test_pdf_under_25_pages_is_not_split(
    tmp_path,
):

    source_pdf = (
        tmp_path / "small.pdf"
    )

    output_dir = (
        tmp_path / "chunks"
    )

    create_test_pdf(
        source_pdf,
        page_count=20,
    )

    chunks = split_pdf(
        source_pdf,
        output_dir,
    )

    assert chunks == [source_pdf]


def test_exactly_25_pages_is_not_split(
    tmp_path,
):

    source_pdf = (
        tmp_path / "exact.pdf"
    )

    output_dir = (
        tmp_path / "chunks"
    )

    create_test_pdf(
        source_pdf,
        page_count=25,
    )

    chunks = split_pdf(
        source_pdf,
        output_dir,
    )

    assert chunks == [source_pdf]
    
def test_pdf_page_continuity_is_preserved(
    tmp_path,
):

    source_pdf = (
        tmp_path / "Matrices.pdf"
    )

    output_dir = (
        tmp_path / "chunks"
    )

    # Create a PDF where every page contains
    # its original page number.
    document = fitz.open()

    for page_number in range(1, 43):

        page = document.new_page()

        page.insert_text(
            (72, 72),
            f"ORIGINAL_PAGE_{page_number}",
        )

    document.save(source_pdf)
    document.close()

    

    chunks = split_pdf(
        source_pdf,
        output_dir,
    )

    assert len(chunks) == 2

    first = PdfReader(
        str(chunks[0])
    )

    second = PdfReader(
        str(chunks[1])
    )

    # -----------------------------------------
    # Chunk 1 = original pages 1–25
    # -----------------------------------------

    assert len(first.pages) == 25

    for index, page in enumerate(
        first.pages,
        start=1,
    ):

        text = page.extract_text()

        assert (
            f"ORIGINAL_PAGE_{index}"
            in text
        )

    # -----------------------------------------
    # Chunk 2 = original pages 26–42
    # -----------------------------------------

    assert len(second.pages) == 17

    for index, page in enumerate(
        second.pages,
        start=26,
    ):

        text = page.extract_text()

        assert (
            f"ORIGINAL_PAGE_{index}"
            in text
        )