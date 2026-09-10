from services.extractors.visual_candidate_context import (
    VisualCandidateContext,
)
from services.extractors.visual_semantic_analyzer import (
    RuleBasedVisualSemanticAnalyzer,
)


def _context(
    *,
    caption=None,
    nearby_text=None,
    preceding_text=None,
    following_text=None,
    repeated=False,
    role="localized_visual_candidate",
):
    return VisualCandidateContext(
        id="visual-region-1",
        page_number=12,
        bbox=(100.0, 200.0, 300.0, 400.0),
        region_role=role,
        repeated=repeated,
        source_types=["drawing"],
        nearby_text=nearby_text or [],
        preceding_text=preceding_text,
        following_text=following_text,
        caption=caption,
        source_block_ids=["block-1"],
        evidence={},
        provenance={
            "source": "pdf",
            "page": 12,
        },
        metadata={},
    )


def test_detects_explicit_triangle():
    context = _context(
        nearby_text=[
            "Consider triangle ABC."
        ]
    )

    result = RuleBasedVisualSemanticAnalyzer().analyze(context)

    assert result.figure_type == "triangle"


def test_detects_concepts():
    context = _context(
        nearby_text=[
            "Consider triangle ABC and the angle at A."
        ]
    )

    result = RuleBasedVisualSemanticAnalyzer().analyze(context)

    assert "triangle" in result.related_concepts
    assert "angle" in result.related_concepts


def test_detects_explicit_labels():
    context = _context(
        nearby_text=[
            "Consider triangle ABC."
        ]
    )

    result = RuleBasedVisualSemanticAnalyzer().analyze(context)

    assert "B" in result.labels
    assert "C" in result.labels


def test_caption_can_supply_semantic_evidence():
    context = _context(
        caption="Figure 2.1: Triangle ABC"
    )

    result = RuleBasedVisualSemanticAnalyzer().analyze(context)

    assert result.figure_type == "triangle"
    assert result.caption == "Figure 2.1: Triangle ABC"


def test_no_textual_evidence_does_not_invent_type():
    context = _context()

    result = RuleBasedVisualSemanticAnalyzer().analyze(context)

    assert result.figure_type is None
    assert result.geometry == {}
    assert result.confidence is None


def test_localized_mathematical_candidate_is_educationally_relevant():
    context = _context(
        nearby_text=[
            "The triangle has an angle of 30 degrees."
        ]
    )

    result = RuleBasedVisualSemanticAnalyzer().analyze(context)

    assert result.is_educationally_relevant is True


def test_repeated_region_is_not_automatically_marked_relevant():
    context = _context(
        repeated=True,
        role="repeated_structural_region",
    )

    result = RuleBasedVisualSemanticAnalyzer().analyze(context)

    assert result.is_educationally_relevant is None


def test_repeated_region_with_mathematical_context_can_be_relevant():
    context = _context(
        repeated=True,
        role="repeated_structural_region",
        nearby_text=[
            "The following triangle illustrates the angle theorem."
        ],
    )

    result = RuleBasedVisualSemanticAnalyzer().analyze(context)

    assert result.figure_type == "triangle"
    assert result.is_educationally_relevant is True


def test_geometry_contains_only_semantic_type_hint():
    context = _context(
        nearby_text=[
            "Triangle ABC"
        ]
    )

    result = RuleBasedVisualSemanticAnalyzer().analyze(context)

    assert result.geometry["type"] == "triangle"
    assert result.geometry["elements"] == []
    assert result.geometry["source"] == "textual_semantic_hint"


def test_interaction_capabilities_are_preserved():
    context = _context(
        nearby_text=[
            "Triangle ABC"
        ]
    )

    result = RuleBasedVisualSemanticAnalyzer().analyze(context)

    assert result.interaction["modifiable"] is True
    assert result.interaction["can_highlight"] is True
    assert result.interaction["can_animate"] is True


def test_provenance_is_preserved():
    context = _context(
        nearby_text=[
            "Triangle ABC"
        ]
    )

    result = RuleBasedVisualSemanticAnalyzer().analyze(context)

    assert result.provenance["source"] == "pdf"
    assert result.provenance["page"] == 12
    assert (
        result.provenance["semantic_analysis"]
        == "rule_based_text_evidence"
    )


def test_analyze_many_preserves_order():
    analyzer = RuleBasedVisualSemanticAnalyzer()

    contexts = [
        _context(
            nearby_text=["Triangle ABC"]
        ),
        VisualCandidateContext(
            id="visual-region-2",
            page_number=13,
            bbox=(10.0, 20.0, 30.0, 40.0),
            source_types=["drawing"],
            nearby_text=["Circle O"],
            source_block_ids=["block-2"],
        ),
    ]

    results = analyzer.analyze_many(contexts)

    assert len(results) == 2
    assert results[0].id == "visual-region-1"
    assert results[0].figure_type == "triangle"
    assert results[1].id == "visual-region-2"
    assert results[1].figure_type == "circle"
    
def test_does_not_detect_arc_from_substring():
    context = _context(
        nearby_text=[
            "In particular, consider the function."
        ]
    )

    result = RuleBasedVisualSemanticAnalyzer().analyze(context)

    assert result.figure_type is None
    
def test_generic_function_does_not_become_function_graph():
    context = _context(
        nearby_text=[
            "The function is defined for all real numbers."
        ]
    )

    result = RuleBasedVisualSemanticAnalyzer().analyze(context)

    assert result.figure_type is None
    assert result.is_educationally_relevant is None
    
def test_ordinary_uppercase_letter_is_not_visual_label():
    context = _context(
        nearby_text=[
            "Let R be a real number."
        ]
    )

    result = RuleBasedVisualSemanticAnalyzer().analyze(context)

    assert result.labels == []