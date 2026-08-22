from pathlib import Path

from pypdf import PdfReader, PdfWriter

from functions.pdf_ingestion.ingestion_coordinator import (
    IngestionCoordinator,
)


def create_pdf(
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


def test_small_pdf_is_returned_unchanged(
    tmp_path,
):

    source = tmp_path / "small.pdf"

    create_pdf(
        source,
        20,
    )

    coordinator = IngestionCoordinator(
        max_pages=25,
    )

    files = coordinator.prepare(
        source,
    )

    assert files == [source]

    assert len(files) == 1

    assert (
        len(PdfReader(str(files[0])).pages)
        == 20
    )


def test_exactly_25_pages_is_returned_unchanged(
    tmp_path,
):

    source = tmp_path / "exact.pdf"

    create_pdf(
        source,
        25,
    )

    coordinator = IngestionCoordinator(
        max_pages=25,
    )

    files = coordinator.prepare(
        source,
    )

    assert files == [source]

    assert len(files) == 1

    assert (
        len(PdfReader(str(files[0])).pages)
        == 25
    )


def test_large_pdf_is_split(
    tmp_path,
):

    source = tmp_path / "Matrices.pdf"

    output_dir = (
        tmp_path / "chunks"
    )

    create_pdf(
        source,
        42,
    )

    coordinator = IngestionCoordinator(
        max_pages=25,
    )

    files = coordinator.prepare(
        source,
        output_dir=output_dir,
    )

    assert len(files) == 2

    assert (
        len(PdfReader(str(files[0])).pages)
        == 25
    )

    assert (
        len(PdfReader(str(files[1])).pages)
        == 17
    )


def test_75_page_pdf_creates_three_chunks(
    tmp_path,
):

    source = tmp_path / "large.pdf"

    output_dir = (
        tmp_path / "chunks"
    )

    create_pdf(
        source,
        75,
    )

    coordinator = IngestionCoordinator(
        max_pages=25,
    )

    files = coordinator.prepare(
        source,
        output_dir=output_dir,
    )

    assert len(files) == 3

    page_counts = [
        len(PdfReader(str(file)).pages)
        for file in files
    ]

    assert page_counts == [
        25,
        25,
        25,
    ]