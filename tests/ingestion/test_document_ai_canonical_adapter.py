import json

from functions.pdf_ingestion.document_ai_canonical_adapter import (
    DocumentAICanonicalAdapter,
)


def test_adapter_converts_merged_document_ai_blocks(
    tmp_path,
):

    source = {
        "source": {
            "type": "gcp_document_ai_chunk_merge",
            "chunk_count": 2,
            "original_page_count": 42,
        },
        "document": {
            "document_layout": {
                "blocks": [
                    {
                        "block_id": "1",
                        "text_block": {
                            "text": "Chapter 3",
                            "type_": "paragraph",
                        },
                        "page_span": {
                            "page_start": 1,
                            "page_end": 1,
                        },
                    },
                    {
                        "block_id": "2",
                        "text_block": {
                            "text": "Matrices",
                            "type_": "paragraph",
                        },
                        "page_span": {
                            "page_start": 26,
                            "page_end": 27,
                        },
                    },
                ]
            }
        },
    }

    input_file = (
        tmp_path
        / "merged.json"
    )

    input_file.write_text(
        json.dumps(source),
        encoding="utf-8",
    )

    adapter = (
        DocumentAICanonicalAdapter()
    )

    document = adapter.load(
        input_file
    )

    blocks = adapter.extract_blocks(
        document
    )

    assert len(blocks) == 2

    assert blocks[0]["type"] == "paragraph"
    assert blocks[0]["text"] == "Chapter 3"
    assert blocks[0]["page"] == 1
    assert blocks[0]["metadata"] == {}

    assert blocks[1]["page"] == 26

    assert blocks[1]["metadata"] == {
        "page_span": {
            "start": 26,
            "end": 27,
        }
    }

    assert (
        adapter.page_count(document)
        == 42
    )