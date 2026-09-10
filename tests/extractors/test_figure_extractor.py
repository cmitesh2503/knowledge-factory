"""
Knowledge Factory

Figure Extractor Tests

Tests provider-independent figure extraction and the
information required for future MathVerse figure relevance
and linking.
"""

from services.extractors.figure_extractor import FigureExtractor


def test_extracts_captioned_educational_figure():
    canonical_document = {
        "pages": [
            {
                "page_number": 5,
                "blocks": [
                    {
                        "id": "figure-1",
                        "type": "figure",
                        "text": (
                            "A right triangle used to explain "
                            "trigonometric ratios."
                        ),
                        "figure": {
                            "caption": "Triangle ABC",
                            "figure_type": "geometry_diagram",
                            "labels": ["A", "B", "C"],
                            "related_concepts": [
                                "trigonometry",
                                "right_triangle",
                            ],
                            "is_educationally_relevant": True,
                            "confidence": 0.95,
                        },
                        "metadata": {
                            "provider": "document_ai",
                        },
                    }
                ],
            }
        ]
    }

    extractor = FigureExtractor()

    candidates = extractor.find_candidates(
        canonical_document
    )

    figures = extractor.build(
        extractor.validate_candidates(candidates)
    )

    assert len(figures) == 1

    figure = figures[0]

    assert figure.id == "figure-1"
    assert figure.caption == "Triangle ABC"
    assert figure.figure_type == "geometry_diagram"

    assert figure.related_concepts == [
        "trigonometry",
        "right_triangle",
    ]

    assert figure.is_educationally_relevant is True
    assert figure.confidence == 0.95


def test_uncaptioned_figure_is_retained():
    """
    A figure must not be discarded simply because the
    source document does not provide a caption.

    Many textbook diagrams contain only visual labels.
    """

    canonical_document = {
        "pages": [
            {
                "page_number": 8,
                "blocks": [
                    {
                        "id": "figure-2",
                        "type": "figure",
                        "text": None,
                        "figure": {
                            "figure_type": "geometry_diagram",
                            "labels": [
                                "A",
                                "B",
                                "C",
                                "90°",
                            ],
                            "related_concepts": [
                                "right_triangle",
                            ],
                            "is_educationally_relevant": True,
                        },
                    }
                ],
            }
        ]
    }

    extractor = FigureExtractor()

    candidates = extractor.find_candidates(
        canonical_document
    )

    valid = extractor.validate_candidates(
        candidates
    )

    figures = extractor.build(valid)

    assert len(figures) == 1

    figure = figures[0]

    assert figure.caption is None

    assert figure.labels == [
        "A",
        "B",
        "C",
        "90°",
    ]

    assert figure.related_concepts == [
        "right_triangle",
    ]


def test_figure_preserves_concept_linking_information():
    """
    The extractor does not decide concept relevance.

    However, it must preserve concept information already
    available in the canonical document so a later linking
    stage can use it.
    """

    canonical_document = {
        "pages": [
            {
                "page_number": 10,
                "blocks": [
                    {
                        "id": "figure-3",
                        "type": "figure",
                        "text": (
                            "Graph showing the sine function "
                            "between 0 and 2π."
                        ),
                        "figure": {
                            "figure_type": "function_graph",
                            "related_concepts": [
                                "trigonometry",
                                "sine_function",
                                "periodic_functions",
                            ],
                            "is_educationally_relevant": True,
                        },
                    }
                ],
            }
        ]
    }

    extractor = FigureExtractor()

    candidates = extractor.find_candidates(
        canonical_document
    )

    figures = extractor.build(
        extractor.validate_candidates(candidates)
    )

    assert len(figures) == 1

    figure = figures[0]

    assert "trigonometry" in (
        figure.related_concepts
    )

    assert "sine_function" in (
        figure.related_concepts
    )

    assert "periodic_functions" in (
        figure.related_concepts
    )


def test_figure_preserves_geometry_for_rendering():
    """
    Geometry must survive extraction so MathVerse can
    reconstruct a figure instead of displaying a PDF image.
    """

    canonical_document = {
        "pages": [
            {
                "page_number": 12,
                "blocks": [
                    {
                        "id": "figure-4",
                        "type": "figure",
                        "figure": {
                            "figure_type": "geometry_diagram",
                            "geometry": {
                                "elements": [
                                    {
                                        "id": "triangle-abc",
                                        "type": "triangle",
                                        "labels": [
                                            "A",
                                            "B",
                                            "C",
                                        ],
                                    }
                                ]
                            },
                            "interaction": {
                                "modifiable": True,
                                "can_add_elements": True,
                                "can_update_labels": True,
                            },
                            "is_educationally_relevant": True,
                        },
                    }
                ],
            }
        ]
    }

    extractor = FigureExtractor()

    figures = extractor.build(
        extractor.validate_candidates(
            extractor.find_candidates(
                canonical_document
            )
        )
    )

    assert len(figures) == 1

    figure = figures[0]

    assert figure.geometry == {
        "elements": [
            {
                "id": "triangle-abc",
                "type": "triangle",
                "labels": [
                    "A",
                    "B",
                    "C",
                ],
            }
        ]
    }

    assert figure.interaction[
        "modifiable"
    ] is True

    assert figure.interaction[
        "can_add_elements"
    ] is True

    assert figure.interaction[
        "can_update_labels"
    ] is True


def test_figure_can_support_tutor_modification():
    """
    A textbook figure can act as the starting point for
    a tutor explanation.

    The tutor may later add elements, labels, highlights,
    or animation.
    """

    canonical_document = {
        "pages": [
            {
                "page_number": 14,
                "blocks": [
                    {
                        "id": "figure-5",
                        "type": "figure",
                        "figure": {
                            "figure_type": (
                                "geometry_diagram"
                            ),
                            "interaction": {
                                "modifiable": True,
                                "can_add_elements": True,
                                "can_remove_elements": True,
                                "can_update_labels": True,
                                "can_animate": True,
                                "can_highlight": True,
                                "can_transform": True,
                            },
                            "is_educationally_relevant": True,
                        },
                    }
                ],
            }
        ]
    }

    extractor = FigureExtractor()

    figures = extractor.build(
        extractor.validate_candidates(
            extractor.find_candidates(
                canonical_document
            )
        )
    )

    figure = figures[0]

    assert figure.interaction[
        "modifiable"
    ] is True

    assert figure.interaction[
        "can_add_elements"
    ] is True

    assert figure.interaction[
        "can_remove_elements"
    ] is True

    assert figure.interaction[
        "can_update_labels"
    ] is True

    assert figure.interaction[
        "can_animate"
    ] is True

    assert figure.interaction[
        "can_highlight"
    ] is True

    assert figure.interaction[
        "can_transform"
    ] is True


def test_decorative_or_non_relevant_figure_is_preserved():
    """
    A figure may exist in the source document but not be
    useful for tutoring.

    It should remain traceable, while relevance information
    allows later MathVerse logic to avoid selecting it.
    """

    canonical_document = {
        "pages": [
            {
                "page_number": 16,
                "blocks": [
                    {
                        "id": "figure-6",
                        "type": "figure",
                        "text": (
                            "Decorative chapter illustration."
                        ),
                        "figure": {
                            "figure_type": "other",
                            "is_educationally_relevant": False,
                            "confidence": 0.70,
                        },
                    }
                ],
            }
        ]
    }

    extractor = FigureExtractor()

    candidates = extractor.find_candidates(
        canonical_document
    )

    figures = extractor.build(
        extractor.validate_candidates(
            candidates
        )
    )

    assert len(figures) == 1

    figure = figures[0]

    assert (
        figure.is_educationally_relevant
        is False
    )

    assert figure.id == "figure-6"

    assert figure.provenance["page"] == 16


def test_figure_preserves_source_block_and_page_linking():
    """
    A figure must remain traceable to its canonical source
    block and page.

    Future concept/exercise linking can use this location
    information to reason about nearby content.
    """

    canonical_document = {
        "pages": [
            {
                "page_number": 20,
                "blocks": [
                    {
                        "id": "figure-7",
                        "type": "figure",
                        "figure": {
                            "figure_type": (
                                "coordinate_plot"
                            ),
                            "is_educationally_relevant": True,
                        },
                    }
                ],
            }
        ]
    }

    extractor = FigureExtractor()

    candidates = extractor.find_candidates(
        canonical_document
    )

    assert len(candidates) == 1

    candidate = candidates[0]

    assert candidate.page == 20

    assert candidate.source_block_id == (
        "figure-7"
    )

    assert candidate.provenance["page"] == 20

    assert candidate.provenance[
        "source_block_id"
    ] == "figure-7"
