from __future__ import annotations

from dataclasses import dataclass, field

from services.extractors.visual_candidate_selector import (
    VisualCandidateSelection,
    VisualCandidateSelector,
)


@dataclass
class FakeContext:
    id: str = "visual-region-1-1"
    region_role: str = "localized_visual_candidate"
    repeated: bool = False
    caption: str | None = None
    nearby_text: list[str] = field(default_factory=list)
    preceding_text: list[str] = field(default_factory=list)
    following_text: list[str] = field(default_factory=list)


@dataclass
class FakeSemanticResult:
    candidate_id: str = "visual-region-1-1"
    figure_type: str | None = None
    labels: list[str] = field(default_factory=list)
    related_concepts: list[str] = field(default_factory=list)
    is_educationally_relevant: bool | None = None
    confidence: float | None = None
    evidence: dict = field(default_factory=dict)


def _context(**kwargs) -> FakeContext:
    return FakeContext(**kwargs)


def _semantic(**kwargs) -> FakeSemanticResult:
    return FakeSemanticResult(**kwargs)


def test_localized_typed_candidate_is_promoted():
    context = _context()

    semantic = _semantic(
        figure_type="triangle",
        confidence=0.90,
        labels=["A", "B", "C"],
        related_concepts=["triangle", "angle"],
        is_educationally_relevant=True,
    )

    result = VisualCandidateSelector().select(context, semantic)

    assert result.decision == "promote"
    assert result.is_promoted is True
    assert result.candidate_id == "visual-region-1-1"
    assert result.score > 0.70


def test_repeated_structural_candidate_is_not_automatically_promoted():
    context = _context(
        region_role="repeated_structural_region",
        repeated=True,
    )

    semantic = _semantic(
        figure_type="function_graph",
        confidence=0.90,
        labels=["x", "y"],
        related_concepts=["function", "graph"],
        is_educationally_relevant=True,
    )

    result = VisualCandidateSelector().select(context, semantic)

    assert result.decision == "retain"
    assert result.is_promoted is False


def test_repeated_structural_weak_candidate_is_deferred():
    context = _context(
        region_role="repeated_structural_region",
        repeated=True,
    )

    semantic = _semantic(
        confidence=0.10,
        related_concepts=["function", "graph"],
        is_educationally_relevant=None,
    )

    result = VisualCandidateSelector().select(context, semantic)

    assert result.decision == "defer"


def test_generic_concepts_alone_do_not_promote_candidate():
    context = _context()

    semantic = _semantic(
        confidence=0.25,
        related_concepts=["function", "graph"],
        is_educationally_relevant=None,
    )

    result = VisualCandidateSelector().select(context, semantic)

    assert result.decision == "defer"


def test_non_educational_candidate_is_deferred():
    context = _context()

    semantic = _semantic(
        figure_type="rectangle",
        confidence=0.95,
        related_concepts=["rectangle"],
        is_educationally_relevant=False,
    )

    result = VisualCandidateSelector().select(context, semantic)

    assert result.decision == "defer"


def test_caption_strengthens_candidate():
    context = _context(
        caption="Figure 2.1: Right triangle",
    )

    semantic = _semantic(
        figure_type="triangle",
        confidence=0.75,
        related_concepts=["triangle", "angle"],
        is_educationally_relevant=True,
    )

    result = VisualCandidateSelector().select(context, semantic)

    assert result.decision in {"promote", "retain"}
    assert "figure caption detected" in result.reasons


def test_strong_figure_context_is_preserved():
    context = _context(
        nearby_text=[
            "As shown in Figure 2.1, the triangle has a right angle."
        ],
    )

    semantic = _semantic(
        figure_type="triangle",
        confidence=0.90,
        related_concepts=["triangle", "angle"],
        is_educationally_relevant=True,
    )

    result = VisualCandidateSelector().select(context, semantic)

    assert result.decision == "promote"
    assert result.evidence["strong_figure_context"] is True


def test_labels_strengthen_semantic_candidate():
    context = _context()

    semantic = _semantic(
        figure_type="triangle",
        confidence=0.80,
        labels=["A", "B", "C"],
        related_concepts=["triangle"],
        is_educationally_relevant=True,
    )

    result = VisualCandidateSelector().select(context, semantic)

    assert "explicit labels detected: A, B, C" in result.reasons


def test_candidate_selection_is_serializable():
    context = _context()

    semantic = _semantic(
        figure_type="circle",
        confidence=0.90,
        labels=["O"],
        related_concepts=["circle"],
        is_educationally_relevant=True,
    )

    result = VisualCandidateSelector().select(context, semantic)

    data = result.to_dict()

    assert data["candidate_id"] == "visual-region-1-1"
    assert data["decision"] in {"promote", "retain", "defer"}
    assert 0.0 <= data["score"] <= 1.0
    assert isinstance(data["reasons"], list)
    assert isinstance(data["evidence"], dict)


def test_select_many_preserves_order():
    selector = VisualCandidateSelector()

    context_1 = _context(id="visual-1")
    semantic_1 = _semantic(
        candidate_id="visual-1",
        figure_type="triangle",
        confidence=0.90,
        is_educationally_relevant=True,
    )

    context_2 = _context(id="visual-2")
    semantic_2 = _semantic(
        candidate_id="visual-2",
        confidence=0.10,
    )

    results = selector.select_many(
        [
            (context_1, semantic_1),
            (context_2, semantic_2),
        ]
    )

    assert [result.candidate_id for result in results] == [
        "visual-1",
        "visual-2",
    ]

    assert results[0].decision == "promote"
    assert results[1].decision == "defer"


def test_missing_candidate_id_raises_error():
    context = _context(id="")

    semantic = _semantic(candidate_id="")

    selector = VisualCandidateSelector()

    try:
        selector.select(context, semantic)
    except ValueError as exc:
        assert "candidate_id" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_invalid_selection_decision_is_rejected():
    try:
        VisualCandidateSelection(
            candidate_id="visual-1",
            decision="invalid",
            score=0.5,
        )
    except ValueError as exc:
        assert "Invalid decision" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_invalid_score_is_rejected():
    try:
        VisualCandidateSelection(
            candidate_id="visual-1",
            decision="retain",
            score=1.5,
        )
    except ValueError as exc:
        assert "score" in str(exc)
    else:
        raise AssertionError("Expected ValueError")