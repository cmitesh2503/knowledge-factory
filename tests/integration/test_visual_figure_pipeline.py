from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from services.extractors.visual_candidate_selector import (
    VisualCandidateSelection,
)
from services.integration.knowledge_package_builder import (
    KnowledgePackageBuilder,
)
from services.integration.visual_figure_pipeline import (
    VisualFigurePipeline,
    append_promoted_visual_figures_to_canonical_document,
)
from services.models.figure import Figure
from services.models.figure_candidate import FigureCandidate


@dataclass
class FakeContext:
    id: str
    page_number: int = 1
    bbox: tuple[float, float, float, float] = (
        10.0,
        20.0,
        110.0,
        160.0,
    )
    region_role: str = "localized_visual_candidate"
    repeated: bool = False
    source_types: list[str] = field(
        default_factory=lambda: ["drawing"]
    )
    nearby_text: list[str] = field(
        default_factory=lambda: [
            "As shown in the diagram, triangle ABC is right angled."
        ]
    )
    caption: str | None = "Figure 1: Triangle ABC"
    source_block_ids: list[str] = field(
        default_factory=lambda: ["text-1"]
    )
    evidence: dict[str, Any] = field(
        default_factory=lambda: {
            "has_caption": True,
            "is_localized": True,
        }
    )
    provenance: dict[str, Any] = field(
        default_factory=lambda: {
            "source": "pdf",
            "page": 1,
            "visual_region_id": "visual-1",
        }
    )
    metadata: dict[str, Any] = field(
        default_factory=lambda: {
            "region_role": "localized_visual_candidate",
            "repeated": False,
        }
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "page_number": self.page_number,
            "bbox": list(self.bbox),
            "region_role": self.region_role,
            "repeated": self.repeated,
            "source_types": list(self.source_types),
            "nearby_text": list(self.nearby_text),
            "caption": self.caption,
            "source_block_ids": list(self.source_block_ids),
            "evidence": dict(self.evidence),
            "provenance": dict(self.provenance),
            "metadata": dict(self.metadata),
        }


class FakeVisualExtractor:
    def __init__(self, page_count: int = 1) -> None:
        self.pages = [
            SimpleNamespace(page_number=page_number)
            for page_number in range(1, page_count + 1)
        ]

    def extract(self, pdf_path):
        return self.pages


class FakeRegionDetector:
    def __init__(self, contexts: list[FakeContext]) -> None:
        self.contexts = contexts

    def detect(self, pdf_path):
        return [
            SimpleNamespace(
                id=context.id,
                page_number=context.page_number,
                bbox=context.bbox,
            )
            for context in self.contexts
        ]


class FakeContextBuilder:
    def __init__(self, contexts: list[FakeContext]) -> None:
        self.contexts = contexts

    def build(self, regions, canonical_document):
        return self.contexts


class FakeSemanticAnalyzer:
    def __init__(
        self,
        candidates: list[FigureCandidate],
    ) -> None:
        self.candidates = {
            candidate.id: candidate
            for candidate in candidates
        }

    def analyze(
        self,
        context,
        visual_input=None,
    ):
        return self.candidates[context.id]


class FakeSelector:
    def __init__(
        self,
        decisions: dict[str, str],
    ) -> None:
        self.decisions = decisions

    def select_many(self, candidates):
        selections: list[VisualCandidateSelection] = []

        for _context, candidate in candidates:
            decision = self.decisions[candidate.id]
            score = 0.9 if decision == "promote" else 0.4

            selections.append(
                VisualCandidateSelection(
                    candidate_id=candidate.id,
                    decision=decision,
                    score=score,
                    reasons=[
                        f"test decision: {decision}"
                    ],
                    evidence={
                        "figure_type": candidate.figure_type,
                    },
                    metadata={
                        "selector_version": "test",
                    },
                )
            )

        return selections


def _canonical_document() -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "document": {
            "document_id": "doc-visual-test",
        },
        "pages": [
            {
                "page_number": 1,
                "blocks": [
                    {
                        "id": "text-1",
                        "type": "paragraph",
                        "text": "A paragraph near the visual region.",
                        "page": 1,
                        "metadata": {},
                    }
                ],
            }
        ],
    }


def _candidate(
    *,
    candidate_id: str = "visual-1",
    page: Any = 1,
    source_block_id: str | None = "text-1",
) -> FigureCandidate:
    provenance = {
        "source": "pdf",
        "page": page,
        "visual_region_id": candidate_id,
        "provider": "visual_test_provider",
    }

    if source_block_id is not None:
        provenance["source_block_id"] = source_block_id

    return FigureCandidate(
        id=candidate_id,
        page=page if isinstance(page, int) else None,
        source_block_id=source_block_id,
        caption="Figure 1: Triangle ABC",
        description="Visual candidate identified as a triangle.",
        figure_type="triangle",
        labels=["A", "B", "C"],
        geometry={
            "type": "triangle",
            "elements": [],
            "source": "textual_semantic_hint",
        },
        rendering={
            "renderer": "mathverse_native",
        },
        educational={
            "importance": "potentially_relevant",
        },
        interaction={
            "modifiable": True,
            "can_highlight": True,
        },
        related_concepts=[
            "triangle",
            "angle",
        ],
        is_educationally_relevant=True,
        confidence=0.9,
        provenance=provenance,
        metadata={
            "semantic_analysis": {
                "method": "test",
            }
        },
    )


def _figure(
    *,
    figure_id: str = "visual-1",
    page: Any = 1,
    source_block_id: str | None = "text-1",
) -> Figure:
    candidate = _candidate(
        candidate_id=figure_id,
        page=page,
        source_block_id=source_block_id,
    )

    provenance = dict(candidate.provenance)

    metadata = dict(candidate.metadata)
    metadata["visual_context"] = {
        "id": figure_id,
        "page_number": page,
        "bbox": [
            10.0,
            20.0,
            110.0,
            160.0,
        ],
        "metadata": {
            "repeated": False,
        },
    }
    metadata["selector"] = VisualCandidateSelection(
        candidate_id=figure_id,
        decision="promote",
        score=0.9,
    ).to_dict()

    return Figure(
        id=candidate.id,
        caption=candidate.caption,
        description=candidate.description,
        figure_type=candidate.figure_type,
        related_concepts=list(candidate.related_concepts),
        labels=list(candidate.labels),
        geometry=dict(candidate.geometry),
        rendering=dict(candidate.rendering),
        educational=dict(candidate.educational),
        interaction=dict(candidate.interaction),
        provenance=provenance,
        confidence=candidate.confidence,
        is_educationally_relevant=(
            candidate.is_educationally_relevant
        ),
        metadata=metadata,
    )


def _run_pipeline(
    *,
    canonical_document: dict[str, Any],
    contexts: list[FakeContext],
    candidates: list[FigureCandidate],
    decisions: dict[str, str],
):
    pipeline = VisualFigurePipeline(
        visual_extractor=FakeVisualExtractor(),
        region_detector=FakeRegionDetector(contexts),
        context_builder=FakeContextBuilder(contexts),
        semantic_analyzer=FakeSemanticAnalyzer(candidates),
        selector=FakeSelector(decisions),
    )

    return pipeline.run(
        pdf_path="test.pdf",
        canonical_document=canonical_document,
    )


def test_promoted_candidate_becomes_canonical_figure_block():
    canonical = _canonical_document()
    context = FakeContext(id="visual-1")
    candidate = _candidate(candidate_id="visual-1")

    result = _run_pipeline(
        canonical_document=canonical,
        contexts=[context],
        candidates=[candidate],
        decisions={
            "visual-1": "promote",
        },
    )

    assert result.promoted_count == 1
    assert result.append_result.added_count == 1

    block = canonical["pages"][0]["blocks"][-1]

    assert block["id"] == "text-1-figure-visual-1"
    assert block["type"] == "figure"
    assert block["page"] == 1
    assert block["metadata"]["source"] == "visual_figure_pipeline"
    assert block["geometry"]["bbox"] == [
        10.0,
        20.0,
        110.0,
        160.0,
    ]

    figure = block["figure"]

    assert figure["id"] == "visual-1"
    assert figure["caption"] == "Figure 1: Triangle ABC"
    assert figure["description"] == (
        "Visual candidate identified as a triangle."
    )
    assert figure["figure_type"] == "triangle"
    assert figure["labels"] == ["A", "B", "C"]
    assert figure["geometry"]["type"] == "triangle"
    assert figure["rendering"]["renderer"] == "mathverse_native"
    assert figure["educational"]["importance"] == (
        "potentially_relevant"
    )
    assert figure["interaction"]["modifiable"] is True
    assert figure["provenance"]["source"] == "pdf"
    assert figure["provenance"]["source_block_id"] == "text-1"
    assert figure["provenance"]["page"] == 1
    assert figure["provenance"]["provider"] == (
        "visual_test_provider"
    )
    assert figure["confidence"] == 0.9
    assert figure["is_educationally_relevant"] is True
    assert figure["metadata"]["selector"]["decision"] == "promote"
    assert figure["metadata"]["visual_context"]["id"] == "visual-1"


def test_ingestion_main_serializes_after_visual_enrichment():
    source = Path(
        "functions/pdf_ingestion/main.py"
    ).read_text(encoding="utf-8")

    build_index = source.index(
        "STEP 10: BUILD CANONICAL DOCUMENT"
    )
    visual_index = source.index(
        "visual_figure_pipeline.run(",
        build_index,
    )
    dump_index = source.index(
        "json.dump(",
        visual_index,
    )
    upload_index = source.index(
        "storage_service.upload_blob(",
        dump_index,
    )
    package_index = source.index(
        "knowledge_package_builder.build(",
        upload_index,
    )

    assert (
        build_index
        < visual_index
        < dump_index
        < upload_index
        < package_index
    )


def test_retained_candidate_is_not_promoted_to_canonical_figure():
    canonical = _canonical_document()
    context = FakeContext(id="visual-retain")
    candidate = _candidate(candidate_id="visual-retain")

    result = _run_pipeline(
        canonical_document=canonical,
        contexts=[context],
        candidates=[candidate],
        decisions={
            "visual-retain": "retain",
        },
    )

    assert result.retained_count == 1
    assert result.append_result.added_count == 0
    assert len(canonical["pages"][0]["blocks"]) == 1


def test_deferred_candidate_is_not_promoted_to_canonical_figure():
    canonical = _canonical_document()
    context = FakeContext(id="visual-defer")
    candidate = _candidate(candidate_id="visual-defer")

    result = _run_pipeline(
        canonical_document=canonical,
        contexts=[context],
        candidates=[candidate],
        decisions={
            "visual-defer": "defer",
        },
    )

    assert result.deferred_count == 1
    assert result.append_result.added_count == 0
    assert len(canonical["pages"][0]["blocks"]) == 1


def test_zero_promoted_candidates_succeeds_with_empty_figures():
    canonical = _canonical_document()

    result = _run_pipeline(
        canonical_document=canonical,
        contexts=[],
        candidates=[],
        decisions={},
    )

    package = KnowledgePackageBuilder().build(
        canonical
    )

    assert result.promoted_count == 0
    assert result.append_result.added_count == 0
    assert package.figures == []


def test_invalid_page_provenance_is_skipped_cleanly():
    canonical = _canonical_document()

    result = append_promoted_visual_figures_to_canonical_document(
        canonical_document=canonical,
        figures=[
            _figure(figure_id="invalid-none", page=None),
            _figure(figure_id="invalid-empty", page=""),
            _figure(figure_id="invalid-text", page="abc"),
            _figure(figure_id="invalid-object", page=object()),
        ],
    )

    assert result.added_count == 0
    assert result.invalid_provenance_skipped == 4
    assert len(canonical["pages"][0]["blocks"]) == 1


def test_numeric_string_and_integer_page_numbers_are_supported():
    canonical = {
        "schema_version": "1.0",
        "document": {
            "document_id": "doc-page-types",
        },
        "pages": [
            {
                "page_number": "1",
                "blocks": [],
            },
            {
                "page_number": 2,
                "blocks": [],
            },
        ],
    }

    result = append_promoted_visual_figures_to_canonical_document(
        canonical_document=canonical,
        figures=[
            _figure(
                figure_id="visual-string-page",
                page="1",
                source_block_id=None,
            ),
            _figure(
                figure_id="visual-int-page",
                page=2,
                source_block_id=None,
            ),
        ],
    )

    assert result.added_count == 2
    assert canonical["pages"][0]["blocks"][0]["id"] == (
        "figure-visual-string-page"
    )
    assert canonical["pages"][1]["blocks"][0]["id"] == (
        "figure-visual-int-page"
    )


def test_unique_block_ids_are_deterministic_and_collision_safe():
    canonical = {
        "schema_version": "1.0",
        "document": {
            "document_id": "doc-unique-blocks",
        },
        "pages": [
            {
                "page_number": 1,
                "blocks": [
                    {
                        "id": "source-block",
                        "type": "paragraph",
                        "text": "Text source.",
                    },
                    {
                        "id": "source-block-figure-visual-conflict",
                        "type": "paragraph",
                        "text": "Existing conflicting ID.",
                    },
                ],
            }
        ],
    }

    result = append_promoted_visual_figures_to_canonical_document(
        canonical_document=canonical,
        figures=[
            _figure(
                figure_id="visual-one",
                source_block_id="source-block",
            ),
            _figure(
                figure_id="visual-two",
                source_block_id="source-block",
            ),
            _figure(
                figure_id="visual-missing-source",
                source_block_id=None,
            ),
            _figure(
                figure_id="visual-conflict",
                source_block_id="source-block",
            ),
        ],
    )

    block_ids = [
        block["id"]
        for block in canonical["pages"][0]["blocks"]
    ]

    assert result.added_count == 4
    assert result.block_id_conflicts_resolved == 1
    assert len(block_ids) == len(set(block_ids))
    assert "source-block-figure-visual-one" in block_ids
    assert "source-block-figure-visual-two" in block_ids
    assert "figure-visual-missing-source" in block_ids
    assert "source-block-figure-visual-conflict-2" in block_ids


def test_running_enrichment_twice_does_not_duplicate_blocks():
    canonical = _canonical_document()
    figure = _figure()

    first = append_promoted_visual_figures_to_canonical_document(
        canonical_document=canonical,
        figures=[
            figure,
        ],
    )

    second = append_promoted_visual_figures_to_canonical_document(
        canonical_document=canonical,
        figures=[
            figure,
        ],
    )

    assert first.added_count == 1
    assert second.added_count == 0
    assert second.duplicate_figures_skipped == 1
    assert len(canonical["pages"][0]["blocks"]) == 2


def test_original_text_blocks_are_preserved_unchanged():
    canonical = _canonical_document()
    original_blocks = deepcopy(
        canonical["pages"][0]["blocks"]
    )

    append_promoted_visual_figures_to_canonical_document(
        canonical_document=canonical,
        figures=[
            _figure(),
        ],
    )

    assert canonical["pages"][0]["blocks"][
        : len(original_blocks)
    ] == original_blocks


def test_existing_figure_representation_is_not_duplicated():
    canonical = _canonical_document()
    canonical["pages"][0]["blocks"].append(
        {
            "id": "existing-visual-figure",
            "type": "figure",
            "text": "Existing visual figure.",
            "figure": {
                "id": "visual-1",
                "provenance": {
                    "page": 1,
                    "visual_region_id": "visual-1",
                },
            },
            "metadata": {
                "source": "visual_figure_pipeline",
            },
        }
    )

    result = append_promoted_visual_figures_to_canonical_document(
        canonical_document=canonical,
        figures=[
            _figure(),
        ],
    )

    figure_blocks = [
        block
        for block in canonical["pages"][0]["blocks"]
        if block["type"] == "figure"
    ]

    assert result.added_count == 0
    assert result.duplicate_figures_skipped == 1
    assert len(figure_blocks) == 1


def test_promoted_canonical_figure_reaches_knowledge_package():
    canonical = _canonical_document()

    append_promoted_visual_figures_to_canonical_document(
        canonical_document=canonical,
        figures=[
            _figure(),
        ],
    )

    serialized_canonical = json.loads(
        json.dumps(canonical)
    )

    figure_blocks = [
        block
        for block in serialized_canonical["pages"][0]["blocks"]
        if block["type"] == "figure"
    ]

    assert len(figure_blocks) == 1
    assert figure_blocks[0]["figure"]["id"] == "visual-1"

    package = KnowledgePackageBuilder().build(
        serialized_canonical
    )

    assert len(package.figures) == 1

    figure = package.figures[0]

    assert figure.id == "visual-1"
    assert figure.figure_type == "triangle"
    assert figure.labels == ["A", "B", "C"]
    assert figure.geometry["type"] == "triangle"
    assert figure.interaction["modifiable"] is True
    assert figure.provenance["source_block_id"] == "text-1"
    assert figure.provenance["page"] == 1
