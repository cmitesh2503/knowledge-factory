from pathlib import Path

from pypdf import PdfReader, PdfWriter


MAX_PAGES_PER_CHUNK = 25


def split_pdf(
    input_pdf: str | Path,
    output_dir: str | Path,
    max_pages: int = MAX_PAGES_PER_CHUNK,
) -> list[Path]:
    """
    Split a PDF into chunks containing at most max_pages pages.

    If the PDF already contains <= max_pages pages,
    no split is required and the original PDF is returned.

    Returns:
        List of generated PDF paths.
    """

    input_path = Path(input_pdf)
    output_path = Path(output_dir)

    if not input_path.exists():
        raise FileNotFoundError(
            f"PDF not found: {input_path}"
        )

    if max_pages <= 0:
        raise ValueError(
            "max_pages must be greater than zero."
        )

    output_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    reader = PdfReader(str(input_path))

    total_pages = len(reader.pages)

    if total_pages == 0:
        raise ValueError(
            f"PDF contains no pages: {input_path}"
        )

    # No split required
    if total_pages <= max_pages:
        return [input_path]

    chunks: list[Path] = []

    for start in range(0, total_pages, max_pages):

        end = min(
            start + max_pages,
            total_pages,
        )

        writer = PdfWriter()

        for page_number in range(start, end):
            writer.add_page(
                reader.pages[page_number]
            )

        chunk_number = (
            start // max_pages
        ) + 1

        chunk_path = (
            output_path
            / f"{input_path.stem}_chunk_{chunk_number:03d}.pdf"
        )

        with chunk_path.open("wb") as output_file:
            writer.write(output_file)

        chunks.append(chunk_path)

    return chunks