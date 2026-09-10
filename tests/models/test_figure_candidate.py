from services.models.figure_candidate import FigureCandidate


def test_figure_candidate_preserves_visual_candidate_contract():

    candidate = FigureCandidate(
        id="figure-001",
        page=3,
        source_block_id="block-000123",
        caption="Triangle ABC",
        description="A triangle with labelled vertices.",
        figure_type="triangle",
        labels=["A", "B", "C"],
        geometry={
            "elements": [
                {
                    "type": "triangle",
                    "vertices": ["A", "B", "C"],
                },
            ],
        },
        rendering={
            "renderer": "mathverse",
        },
        educational={
            "purpose": "explain_triangle",
        },
        interaction={
            "modifiable": True,
            "can_highlight": True,
        },
        related_concepts=[
            "triangle",
            "geometry",
        ],
        is_educationally_relevant=True,
        confidence=0.91,
        provenance={
            "source": "visual_extraction",
            "page": 3,
        },
        metadata={
            "test": True,
        },
    )

    assert candidate.id == "figure-001"
    assert candidate.page == 3
    assert candidate.source_block_id == "block-000123"
    assert candidate.caption == "Triangle ABC"
    assert candidate.description == (
        "A triangle with labelled vertices."
    )
    assert candidate.figure_type == "triangle"

    assert candidate.labels == ["A", "B", "C"]

    assert candidate.geometry["elements"][0]["type"] == (
        "triangle"
    )

    assert candidate.rendering["renderer"] == "mathverse"
    assert candidate.educational["purpose"] == (
        "explain_triangle"
    )

    assert candidate.interaction["modifiable"] is True
    assert candidate.interaction["can_highlight"] is True

    assert candidate.related_concepts == [
        "triangle",
        "geometry",
    ]

    assert candidate.is_educationally_relevant is True
    assert candidate.confidence == 0.91

    assert candidate.provenance["source"] == (
        "visual_extraction"
    )
    assert candidate.metadata["test"] is True


def test_figure_candidate_uses_safe_defaults():

    candidate = FigureCandidate(id="figure-002")

    assert candidate.page is None
    assert candidate.source_block_id is None
    assert candidate.caption is None
    assert candidate.description is None
    assert candidate.figure_type is None

    assert candidate.labels == []
    assert candidate.geometry == {}
    assert candidate.rendering == {}
    assert candidate.educational == {}
    assert candidate.interaction == {}
    assert candidate.related_concepts == []

    assert candidate.is_educationally_relevant is None
    assert candidate.confidence is None
    assert candidate.provenance == {}
    assert candidate.metadata == {}