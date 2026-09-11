"""
Production integration for the visual figure extraction pipeline.

This module composes the existing visual pipeline components and enriches a
canonical document with only promoted visual figure candidates. It does not
perform provider-specific document extraction, embedding, search, or rendering.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
import logging
from pathlib import Path
from typing import Any

from services.extractors.visual_candidate_context import (
    VisualCandidateContextBuilder,
)
from services.extractors.visual_candidate_selector import (
    VisualCandidateSelection,
    VisualCandidateSelector,
)
from services.extractors.visual_figure_extractor import (
    VisualFigureExtractor,
)
from services.extractors.visual_region_detector import (
    VisualRegionDetector,
)
from services.extractors.visual_semantic_analyzer import (
    RuleBasedVisualSemanticAnalyzer,
)
from services.models.figure import Figure
from services.models.figure_candidate import FigureCandidate


@dataclass(slots=True)
class CanonicalFigureAppendResult:
    """Counts produced while appending visual figures to canonical pages."""

    added_count: int = 0
    invalid_provenance_skipped: int = 0
    duplicate_figures_skipped: int = 0
    block_id_conflicts_resolved: int = 0
    malformed_canonical_pages_skipped: int = 0

    def to_metadata(self) -> dict[str, int]:
        return {
            "canonical_blocks_added": self.added_count,
            "invalid_provenance_skipped": (
                self.invalid_provenance_skipped
            ),
            "duplicate_figures_skipped": (
                self.duplicate_figures_skipped
            ),
            "block_id_conflicts_resolved": (
                self.block_id_conflicts_resolved
            ),
            "malformed_canonical_pages_skipped": (
                self.malformed_canonical_pages_skipped
            ),
        }


@dataclass(slots=True)
class VisualFigurePipelineResult:
    """Structured result from one visual figure pipeline run."""

    visual_page_count: int
    regions: list[Any] = field(default_factory=list)
    contexts: list[Any] = field(default_factory=list)
    candidates: list[FigureCandidate] = field(default_factory=list)
    selections: list[VisualCandidateSelection] = field(
        default_factory=list
    )
    promoted_figures: list[Figure] = field(default_factory=list)
    append_result: CanonicalFigureAppendResult = field(
        default_factory=CanonicalFigureAppendResult
    )

    @property
    def promoted_count(self) -> int:
        return self._decision_count("promote")

    @property
    def retained_count(self) -> int:
        return self._decision_count("retain")

    @property
    def deferred_count(self) -> int:
        return self._decision_count("defer")

    def to_metadata(self) -> dict[str, Any]:
        metadata: dict[str, Any] = {
            "visual_pages": self.visual_page_count,
            "visual_regions_detected": len(self.regions),
            "visual_contexts_created": len(self.contexts),
            "visual_candidates_created": len(self.candidates),
            "visual_candidates_promoted": self.promoted_count,
            "visual_candidates_retained": self.retained_count,
            "visual_candidates_deferred": self.deferred_count,
        }

        metadata.update(
            self.append_result.to_metadata()
        )

        return metadata

    def _decision_count(self, decision: str) -> int:
        return sum(
            1
            for selection in self.selections
            if selection.decision == decision
        )


class VisualFigurePipeline:
    """
    Orchestrate visual figure extraction and canonical enrichment.

    The component intentionally delegates rendering, region detection,
    context building, semantic analysis, and selection to the existing
    pipeline classes.
    """

    def __init__(
        self,
        *,
        visual_extractor: Any | None = None,
        region_detector: Any | None = None,
        context_builder: Any | None = None,
        semantic_analyzer: Any | None = None,
        selector: Any | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.visual_extractor = (
            visual_extractor or VisualFigureExtractor()
        )
        self.region_detector = (
            region_detector or VisualRegionDetector()
        )
        self.context_builder = (
            context_builder or VisualCandidateContextBuilder()
        )
        self.semantic_analyzer = (
            semantic_analyzer or RuleBasedVisualSemanticAnalyzer()
        )
        self.selector = selector or VisualCandidateSelector()
        self.logger = logger or logging.getLogger(
            "knowledge_factory"
        )

    def run(
        self,
        *,
        pdf_path: str | Path,
        canonical_document: dict[str, Any],
    ) -> VisualFigurePipelineResult:
        """
        Run the visual figure pipeline and enrich the canonical document.

        Only selector decisions of ``promote`` become canonical figure
        blocks. ``retain`` and ``defer`` candidates remain represented in
        the returned pipeline metadata but are not appended to the canonical
        document.
        """

        path = Path(pdf_path)

        visual_pages = self.visual_extractor.extract(path)
        visual_pages_by_number = {
            page.page_number: page
            for page in visual_pages
        }

        regions = self.region_detector.detect(path)

        contexts = self.context_builder.build(
            regions,
            canonical_document,
        )

        candidates = [
            self.semantic_analyzer.analyze(
                context,
                visual_pages_by_number.get(
                    getattr(
                        context,
                        "page_number",
                        None,
                    )
                ),
            )
            for context in contexts
        ]

        selections = self.selector.select_many(
            zip(contexts, candidates)
        )

        promoted_figures = self._build_promoted_figures(
            candidates=candidates,
            selections=selections,
            contexts=contexts,
        )

        append_result = (
            append_promoted_visual_figures_to_canonical_document(
                canonical_document=canonical_document,
                figures=promoted_figures,
                logger=self.logger,
            )
        )

        result = VisualFigurePipelineResult(
            visual_page_count=len(visual_pages),
            regions=list(regions),
            contexts=list(contexts),
            candidates=list(candidates),
            selections=list(selections),
            promoted_figures=promoted_figures,
            append_result=append_result,
        )

        self.logger.info(
            "Visual figure pipeline completed. "
            "Pages=%d Regions=%d Contexts=%d Candidates=%d "
            "Promoted=%d Retained=%d Deferred=%d "
            "CanonicalBlocksAdded=%d InvalidProvenanceSkipped=%d "
            "DuplicateFiguresSkipped=%d",
            result.visual_page_count,
            len(result.regions),
            len(result.contexts),
            len(result.candidates),
            result.promoted_count,
            result.retained_count,
            result.deferred_count,
            append_result.added_count,
            append_result.invalid_provenance_skipped,
            append_result.duplicate_figures_skipped,
        )

        return result

    def _build_promoted_figures(
        self,
        *,
        candidates: Sequence[FigureCandidate],
        selections: Sequence[VisualCandidateSelection],
        contexts: Sequence[Any],
    ) -> list[Figure]:
        selections_by_candidate_id = {
            selection.candidate_id: selection
            for selection in selections
        }

        contexts_by_id = {
            str(
                getattr(
                    context,
                    "id",
                    "",
                )
            ): context
            for context in contexts
        }

        figures: list[Figure] = []

        for candidate in candidates:
            selection = selections_by_candidate_id.get(
                candidate.id
            )

            if selection is None or not selection.is_promoted:
                continue

            figures.append(
                _figure_from_candidate(
                    candidate=candidate,
                    selection=selection,
                    context=contexts_by_id.get(
                        candidate.id
                    ),
                )
            )

        return figures


def append_promoted_visual_figures_to_canonical_document(
    *,
    canonical_document: dict[str, Any],
    figures: Iterable[Figure],
    logger: logging.Logger | None = None,
) -> CanonicalFigureAppendResult:
    """
    Append promoted visual figures to canonical page blocks in-place.

    Page numbers are read from figure provenance. Missing or malformed page
    provenance is skipped instead of failing ingestion.
    """

    active_logger = logger or logging.getLogger(
        "knowledge_factory"
    )

    result = CanonicalFigureAppendResult()

    pages_by_number: dict[int, dict[str, Any]] = {}

    pages = canonical_document.get(
        "pages",
        [],
    )

    if not isinstance(
        pages,
        Sequence,
    ):
        active_logger.warning(
            "Canonical document pages are malformed; "
            "visual figures cannot be appended."
        )
        return result

    for page in pages:
        if not isinstance(
            page,
            dict,
        ):
            result.malformed_canonical_pages_skipped += 1
            continue

        page_number = _coerce_page_number(
            page.get("page_number")
        )

        if page_number is None:
            result.malformed_canonical_pages_skipped += 1
            active_logger.warning(
                "Skipping canonical page with malformed page_number: %r",
                page.get("page_number"),
            )
            continue

        pages_by_number.setdefault(
            page_number,
            page,
        )

    existing_block_ids = _existing_block_ids(pages)
    existing_figure_keys = _existing_figure_keys(pages)

    for figure in figures:
        page_number = _coerce_page_number(
            figure.provenance.get("page")
            if figure.provenance
            else None
        )

        if page_number is None:
            result.invalid_provenance_skipped += 1
            active_logger.warning(
                "Skipping visual figure with invalid page provenance. "
                "FigureID=%s Page=%r",
                figure.id,
                (
                    figure.provenance.get("page")
                    if figure.provenance
                    else None
                ),
            )
            continue

        page = pages_by_number.get(page_number)

        if page is None:
            result.invalid_provenance_skipped += 1
            active_logger.warning(
                "Skipping visual figure for missing canonical page. "
                "FigureID=%s Page=%s",
                figure.id,
                page_number,
            )
            continue

        figure_keys = _figure_identity_keys(figure)

        if figure_keys & existing_figure_keys:
            result.duplicate_figures_skipped += 1
            active_logger.info(
                "Skipping duplicate visual figure. FigureID=%s",
                figure.id,
            )
            continue

        base_block_id = _canonical_figure_block_id(figure)
        block_id = _unique_block_id(
            base_block_id,
            existing_block_ids,
        )

        if block_id != base_block_id:
            result.block_id_conflicts_resolved += 1
            active_logger.info(
                "Resolved canonical visual figure block ID conflict. "
                "BaseID=%s NewID=%s",
                base_block_id,
                block_id,
            )

        blocks = page.setdefault(
            "blocks",
            [],
        )

        if not isinstance(
            blocks,
            list,
        ):
            result.malformed_canonical_pages_skipped += 1
            active_logger.warning(
                "Skipping visual figure because canonical page blocks "
                "are malformed. FigureID=%s Page=%s",
                figure.id,
                page_number,
            )
            continue

        block = _canonical_figure_block(
            block_id=block_id,
            page_number=page_number,
            figure=figure,
        )

        blocks.append(block)

        existing_block_ids.add(block_id)
        existing_figure_keys.update(figure_keys)
        result.added_count += 1

    return result


def _figure_from_candidate(
    *,
    candidate: FigureCandidate,
    selection: VisualCandidateSelection,
    context: Any | None,
) -> Figure:
    metadata = dict(
        candidate.metadata or {}
    )

    metadata["visual_candidate_id"] = candidate.id
    metadata["selector"] = selection.to_dict()

    if context is not None:
        metadata["visual_context"] = _context_to_dict(
            context
        )

    provenance = dict(
        candidate.provenance or {}
    )

    if candidate.source_block_id and not provenance.get(
        "source_block_id"
    ):
        provenance["source_block_id"] = candidate.source_block_id

    provenance.setdefault(
        "source",
        "visual_figure_pipeline",
    )

    provenance.setdefault(
        "visual_region_id",
        candidate.id,
    )

    return Figure(
        id=str(candidate.id),
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


def _canonical_figure_block(
    *,
    block_id: str,
    page_number: int,
    figure: Figure,
) -> dict[str, Any]:
    figure_data = figure.to_dict()
    figure_data["provenance"] = dict(
        figure_data.get("provenance") or {}
    )
    figure_data["provenance"]["page"] = page_number

    return {
        "id": block_id,
        "type": "figure",
        "text": figure.description or figure.caption or "",
        "page": page_number,
        "confidence": figure.confidence,
        "geometry": _visual_block_geometry(figure),
        "figure": figure_data,
        "metadata": {
            "source": "visual_figure_pipeline",
            "visual_candidate_id": figure.id,
            "selector_decision": "promote",
        },
    }


def _visual_block_geometry(
    figure: Figure,
) -> dict[str, Any]:
    context = figure.metadata.get(
        "visual_context",
        {},
    )

    if not isinstance(
        context,
        Mapping,
    ):
        return {}

    bbox = context.get("bbox")

    if not isinstance(
        bbox,
        Sequence,
    ) or isinstance(
        bbox,
        (str, bytes),
    ):
        return {}

    if len(bbox) != 4:
        return {}

    try:
        normalized_bbox = [
            float(value)
            for value in bbox
        ]
    except (TypeError, ValueError):
        return {}

    return {
        "bbox": normalized_bbox,
        "coordinate_system": "pdf_page",
        "source": "visual_region_detector",
    }


def _canonical_figure_block_id(
    figure: Figure,
) -> str:
    source_block_id = (
        figure.provenance.get("source_block_id")
        if figure.provenance
        else None
    )

    if source_block_id:
        return f"{source_block_id}-figure-{figure.id}"

    return f"figure-{figure.id}"


def _unique_block_id(
    base_block_id: str,
    existing_block_ids: set[str],
) -> str:
    if base_block_id not in existing_block_ids:
        return base_block_id

    suffix = 2

    while f"{base_block_id}-{suffix}" in existing_block_ids:
        suffix += 1

    return f"{base_block_id}-{suffix}"


def _existing_block_ids(
    pages: Sequence[Any],
) -> set[str]:
    block_ids: set[str] = set()

    for block in _iter_blocks(pages):
        block_id = block.get("id")

        if block_id:
            block_ids.add(
                str(block_id)
            )

    return block_ids


def _existing_figure_keys(
    pages: Sequence[Any],
) -> set[tuple[str, str]]:
    keys: set[tuple[str, str]] = set()

    for block in _iter_blocks(pages):
        if block.get("type") != "figure":
            continue

        keys.update(
            _block_figure_identity_keys(block)
        )

    return keys


def _iter_blocks(
    pages: Sequence[Any],
) -> Iterable[dict[str, Any]]:
    for page in pages:
        if not isinstance(
            page,
            Mapping,
        ):
            continue

        blocks = page.get(
            "blocks",
            [],
        )

        if not isinstance(
            blocks,
            Sequence,
        ):
            continue

        for block in blocks:
            if isinstance(
                block,
                dict,
            ):
                yield block


def _block_figure_identity_keys(
    block: Mapping[str, Any],
) -> set[tuple[str, str]]:
    figure_data = block.get("figure")

    if not isinstance(
        figure_data,
        Mapping,
    ):
        figure_data = {}

    metadata = block.get("metadata")

    if not isinstance(
        metadata,
        Mapping,
    ):
        metadata = {}

    provenance = figure_data.get("provenance")

    if not isinstance(
        provenance,
        Mapping,
    ):
        provenance = {}

    keys: set[tuple[str, str]] = set()

    figure_id = figure_data.get("id") or block.get("id")

    if figure_id:
        keys.add(
            (
                "figure_id",
                str(figure_id),
            )
        )

    visual_region_id = (
        provenance.get("visual_region_id")
        or metadata.get("visual_candidate_id")
    )

    figure_metadata = figure_data.get(
        "metadata",
        {},
    )

    if not isinstance(
        figure_metadata,
        Mapping,
    ):
        figure_metadata = {}

    visual_context = figure_metadata.get(
        "visual_context",
        {},
    )

    if isinstance(visual_context, Mapping):
        visual_region_id = (
            visual_region_id
            or visual_context.get("id")
        )

    if visual_region_id:
        keys.add(
            (
                "visual_region_id",
                str(visual_region_id),
            )
        )

    source_block_id = provenance.get(
        "source_block_id"
    )

    if source_block_id and visual_region_id:
        keys.add(
            (
                "source_block_visual_region",
                f"{source_block_id}:{visual_region_id}",
            )
        )

    if (
        block.get("type") == "figure"
        and source_block_id
        and block.get("id") == source_block_id
    ):
        keys.add(
            (
                "existing_source_figure_block",
                str(source_block_id),
            )
        )

    return keys


def _figure_identity_keys(
    figure: Figure,
) -> set[tuple[str, str]]:
    keys: set[tuple[str, str]] = {
        (
            "figure_id",
            figure.id,
        )
    }

    provenance = figure.provenance or {}

    visual_region_id = provenance.get(
        "visual_region_id"
    )

    metadata = figure.metadata or {}
    visual_context = metadata.get(
        "visual_context",
        {},
    )

    if isinstance(
        visual_context,
        Mapping,
    ):
        visual_region_id = (
            visual_region_id
            or visual_context.get("id")
        )

    if visual_region_id:
        keys.add(
            (
                "visual_region_id",
                str(visual_region_id),
            )
        )

    source_block_id = provenance.get(
        "source_block_id"
    )

    if source_block_id and visual_region_id:
        keys.add(
            (
                "source_block_visual_region",
                f"{source_block_id}:{visual_region_id}",
            )
        )

    return keys


def _context_to_dict(
    context: Any,
) -> dict[str, Any]:
    if hasattr(
        context,
        "to_dict",
    ):
        return dict(
            context.to_dict()
        )

    result: dict[str, Any] = {}

    for name in (
        "id",
        "page_number",
        "bbox",
        "region_role",
        "repeated",
        "source_types",
        "nearby_text",
        "caption",
        "source_block_ids",
        "evidence",
        "provenance",
        "metadata",
    ):
        if not hasattr(
            context,
            name,
        ):
            continue

        value = getattr(
            context,
            name,
        )

        if isinstance(
            value,
            tuple,
        ):
            value = list(value)

        result[name] = value

    return result


def _coerce_page_number(
    value: Any,
) -> int | None:
    if value is None or isinstance(
        value,
        bool,
    ):
        return None

    if isinstance(
        value,
        str,
    ):
        value = value.strip()

        if not value:
            return None

    try:
        page_number = int(value)
    except (TypeError, ValueError, OverflowError):
        return None

    if page_number < 1:
        return None

    return page_number
