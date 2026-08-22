from pathlib import Path
from unittest.mock import Mock

from pypdf import PdfReader, PdfWriter

from functions.pdf_ingestion.chunk_processor import (
    DocumentAIChunkProcessor,
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


def test_processes_single_pdf_chunk(
    tmp_path,
):

    pdf = tmp_path / "chunk_001.pdf"

    create_pdf(
        pdf,
        20,
    )

    document_ai = Mock()

    document_ai.process_file.return_value = (
        "DOCUMENT_AI_RESULT"
    )

    processor = DocumentAIChunkProcessor(
        document_ai=document_ai,
        max_pages=25,
    )

    results = processor.process(
        [pdf]
    )

    assert len(results) == 1

    result = results[0]

    assert result.chunk_index == 1

    assert result.start_page == 1

    assert result.end_page == 20

    assert (
        result.document_ai_result
        == "DOCUMENT_AI_RESULT"
    )

    document_ai.process_file.assert_called_once_with(
        pdf
    )


def test_processes_multiple_chunks_in_order(
    tmp_path,
):

    chunk_1 = (
        tmp_path / "Matrices_chunk_001.pdf"
    )

    chunk_2 = (
        tmp_path / "Matrices_chunk_002.pdf"
    )

    create_pdf(
        chunk_1,
        25,
    )

    create_pdf(
        chunk_2,
        17,
    )

    document_ai = Mock()

    document_ai.process_file.side_effect = [
        "RESULT_1",
        "RESULT_2",
    ]

    processor = DocumentAIChunkProcessor(
        document_ai=document_ai,
        max_pages=25,
    )

    results = processor.process(
        [
            chunk_1,
            chunk_2,
        ]
    )

    assert len(results) == 2

    # -----------------------------------------
    # Chunk 1
    # -----------------------------------------

    assert results[0].chunk_index == 1

    assert results[0].start_page == 1

    assert results[0].end_page == 25

    assert (
        results[0].document_ai_result
        == "RESULT_1"
    )

    # -----------------------------------------
    # Chunk 2
    # -----------------------------------------

    assert results[1].chunk_index == 2

    assert results[1].start_page == 26

    assert results[1].end_page == 42

    assert (
        results[1].document_ai_result
        == "RESULT_2"
    )

    assert (
        document_ai.process_file.call_count
        == 2
    )


def test_75_pages_are_mapped_correctly(
    tmp_path,
):

    chunks = []

    for index in range(1, 4):

        chunk = (
            tmp_path
            / f"large_chunk_{index:03d}.pdf"
        )

        create_pdf(
            chunk,
            25,
        )

        chunks.append(chunk)

    document_ai = Mock()

    document_ai.process_file.side_effect = [
        "RESULT_1",
        "RESULT_2",
        "RESULT_3",
    ]

    processor = DocumentAIChunkProcessor(
        document_ai=document_ai,
        max_pages=25,
    )

    results = processor.process(
        chunks
    )

    assert [
        (
            result.start_page,
            result.end_page,
        )
        for result in results
    ] == [
        (1, 25),
        (26, 50),
        (51, 75),
    ]