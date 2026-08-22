import json

from functions.pdf_ingestion.document_ai_merger import (
    DocumentAIChunkMerger,
)


def create_chunk(
    path,
    first_page,
    last_page,
):
    """
    Create a fake Document AI artifact where
    every page has one layout block.
    """

    blocks = []

    for page in range(
        first_page,
        last_page + 1,
    ):

        blocks.append(
            {
                "block_id": str(page),
                "text_block": {
                    "text": (
                        f"Test content page {page}"
                    ),
                    "type_": "paragraph",
                },
                "page_span": {
                    "page_start": page,
                    "page_end": page,
                },
            }
        )

    data = {
        "document": {
            "document_layout": {
                "blocks": blocks,
            }
        }
    }

    path.write_text(
        json.dumps(data),
        encoding="utf-8",
    )


def test_merges_two_chunks_and_rebases_pages(
    tmp_path,
):

    chunk_1 = (
        tmp_path
        / "Matrices_chunk_001.json"
    )

    chunk_2 = (
        tmp_path
        / "Matrices_chunk_002.json"
    )

    create_chunk(
        chunk_1,
        first_page=1,
        last_page=25,
    )

    create_chunk(
        chunk_2,
        first_page=1,
        last_page=17,
    )

    output = (
        tmp_path
        / "merged.json"
    )

    merger = DocumentAIChunkMerger()

    result = merger.merge(
        [
            chunk_1,
            chunk_2,
        ],
        output,
    )

    assert result.exists()

    merged = json.loads(
        result.read_text(
            encoding="utf-8"
        )
    )

    assert (
        merged["source"]
        ["chunk_count"]
        == 2
    )

    assert (
        merged["source"]
        ["original_page_count"]
        == 42
    )

    blocks = (
        merged
        ["document"]
        ["document_layout"]
        ["blocks"]
    )

    assert len(blocks) == 42

    # Chunk 1 remains pages 1-25.
    assert (
        blocks[0]
        ["page_span"]
        ["page_start"]
        == 1
    )

    assert (
        blocks[24]
        ["page_span"]
        ["page_start"]
        == 25
    )

    # Chunk 2 originally had local pages 1-17.
    # After merging, those become original pages 26-42.

    assert (
        blocks[25]
        ["page_span"]
        ["page_start"]
        == 26
    )

    assert (
        blocks[26]
        ["page_span"]
        ["page_start"]
        == 27
    )

    assert (
        blocks[41]
        ["page_span"]
        ["page_start"]
        == 42
    )
        


def test_missing_chunk_fails(tmp_path):

    merger = DocumentAIChunkMerger()

    output = (
        tmp_path
        / "merged.json"
    )

    missing = (
        tmp_path
        / "missing.json"
    )

    try:

        merger.merge(
            [missing],
            output,
        )

        assert False

    except FileNotFoundError:
        pass