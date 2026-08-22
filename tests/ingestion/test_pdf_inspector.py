from pypdf import PdfWriter

from functions.pdf_ingestion.pdf_inspector import (
    inspect_pdf,
)


def create_pdf(path, page_count):
    writer = PdfWriter()

    for _ in range(page_count):
        writer.add_blank_page(
            width=612,
            height=792,
        )

    with path.open("wb") as file:
        writer.write(file)


def test_pdf_under_limit_does_not_require_split(
    tmp_path,
):

    pdf = tmp_path / "small.pdf"

    create_pdf(pdf, 20)

    result = inspect_pdf(pdf)

    assert result.page_count == 20
    assert result.max_pages == 25
    assert result.requires_split is False


def test_pdf_exactly_at_limit_does_not_require_split(
    tmp_path,
):

    pdf = tmp_path / "exact.pdf"

    create_pdf(pdf, 25)

    result = inspect_pdf(pdf)

    assert result.page_count == 25
    assert result.max_pages == 25
    assert result.requires_split is False


def test_pdf_over_limit_requires_split(
    tmp_path,
):

    pdf = tmp_path / "large.pdf"

    create_pdf(pdf, 42)

    result = inspect_pdf(pdf)

    assert result.page_count == 42
    assert result.max_pages == 25
    assert result.requires_split is True