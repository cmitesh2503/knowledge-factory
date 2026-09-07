from pdf_text_extractor import (
    PDFTextExtractor,
)


def _create_two_page_pdf(
    file_path,
) -> None:
    """
    Create a minimal two-page PDF fixture.
    """

    pdf_content = (
        b"%PDF-1.4\n"
        b"1 0 obj\n"
        b"<< /Type /Catalog /Pages 2 0 R >>\n"
        b"endobj\n"
        b"2 0 obj\n"
        b"<< /Type /Pages /Kids [3 0 R 4 0 R] /Count 2 >>\n"
        b"endobj\n"
        b"3 0 obj\n"
        b"<< /Type /Page /Parent 2 0 R "
        b"/MediaBox [0 0 612 792] >>\n"
        b"endobj\n"
        b"4 0 obj\n"
        b"<< /Type /Page /Parent 2 0 R "
        b"/MediaBox [0 0 612 792] >>\n"
        b"endobj\n"
        b"xref\n"
        b"0 5\n"
        b"0000000000 65535 f \n"
        b"0000000009 00000 n \n"
        b"0000000058 00000 n \n"
        b"0000000121 00000 n \n"
        b"0000000208 00000 n \n"
        b"trailer\n"
        b"<< /Size 5 /Root 1 0 R >>\n"
        b"startxref\n"
        b"295\n"
        b"%%EOF\n"
    )

    file_path.write_bytes(
        pdf_content
    )


def test_page_count_returns_pdf_page_count(
    tmp_path,
):
    pdf_file = (
        tmp_path / "two_page.pdf"
    )

    _create_two_page_pdf(
        pdf_file
    )

    extractor = PDFTextExtractor()

    page_count = extractor.page_count(
        pdf_file
    )

    assert page_count == 2