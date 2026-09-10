"""
Visual candidate selection for Knowledge Factory.

Step 5 of the visual figure extraction pipeline.

This module takes the output of visual region detection/context building and
semantic analysis, then decides how a candidate should be handled.

The selector is intentionally provider-independent and does not:
- render images
- perform OCR
- call Document AI
- infer detailed geometry
- create canonical Figure objects
- perform RAG or embedding work

It only makes a conservative promotion decision based on evidence already
available from previous pipeline stages.

Decision states:

    promote
        Strong enough evidence exists to promote the candidate toward a
        canonical Figure.

    retain
        The candidate may be meaningful, but the available evidence is not
        strong enough for automatic promotion.

    defer
        The candidate is likely structural/decorative or has insufficient
        semantic evidence. It remains available as pipeline metadata but
        should not currently become a Figure.

The selector deliberately favors false negatives over false positives.
Promoting a bad figure into the canonical knowledge model is more damaging
than retaining an uncertain candidate for later processing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable


VALID_DECISIONS = frozenset({"promote", "retain", "defer"})


@dataclass(slots=True)
class VisualCandidateSelection:
    """
    Selection decision for one visual candidate.

    Attributes:
        candidate_id: Stable visual candidate identifier.
        decision: One of promote, retain, or defer.
        score: Deterministic selection score between 0.0 and 1.0.
        reasons: Human-readable reasons supporting the decision.
        evidence: Structured evidence used by the selector.
        metadata: Additional provider-independent metadata.
    """

    candidate_id: str
    decision: str
    score: float
    reasons: list[str] = field(default_factory=list)
    evidence: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.candidate_id:
            raise ValueError("candidate_id is required")

        if self.decision not in VALID_DECISIONS:
            raise ValueError(
                f"Invalid decision: {self.decision!r}. "
                f"Expected one of {sorted(VALID_DECISIONS)}."
            )

        if not 0.0 <= self.score <= 1.0:
            raise ValueError("score must be between 0.0 and 1.0")

    @property
    def is_promoted(self) -> bool:
        """Return True when the candidate is selected for promotion."""
        return self.decision == "promote"

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return {
            "candidate_id": self.candidate_id,
            "decision": self.decision,
            "score": self.score,
            "reasons": list(self.reasons),
            "evidence": dict(self.evidence),
            "metadata": dict(self.metadata),
        }


class VisualCandidateSelector:
    """
    Select visual candidates conservatively.

    The selector consumes the context and semantic-analysis objects produced
    by previous pipeline stages. It accepts dataclass-like objects as well as
    dictionaries to keep the boundary flexible.

    The selector does not mutate its inputs.
    """

    MIN_PROMOTE_CONFIDENCE = 0.70
    STRONG_PROMOTE_CONFIDENCE = 0.85

    def select(
        self,
        context: Any,
        semantic_result: Any,
    ) -> VisualCandidateSelection:
        """
        Select one visual candidate.

        Args:
            context: VisualCandidateContext-like object.
            semantic_result: SemanticAnalysisResult-like object.

        Returns:
            VisualCandidateSelection.
        """
        candidate_id = self._get(
            semantic_result,
            "candidate_id",
            default=None,
        ) or self._get(
            context,
            "id",
            default=None,
        )

        if not candidate_id:
            raise ValueError(
                "candidate_id could not be determined from context "
                "or semantic result"
            )

        confidence = self._normalise_confidence(
            self._get(semantic_result, "confidence", default=None)
        )

        figure_type = self._normalise_string(
            self._get(semantic_result, "figure_type", default=None)
        )

        labels = self._as_list(
            self._get(semantic_result, "labels", default=[])
        )

        concepts = self._as_list(
            self._get(
                semantic_result,
                "related_concepts",
                default=self._get(
                    semantic_result,
                    "concepts",
                    default=[],
                ),
            )
        )

        educational = self._get(
            semantic_result,
            "is_educationally_relevant",
            default=None,
        )

        region_role = self._normalise_string(
            self._get(context, "region_role", default=None)
        )

        repeated = bool(
            self._get(
                context,
                "repeated",
                default=self._get(
                    context,
                    "metadata.repeated",
                    default=False,
                ),
            )
        )

        caption = self._normalise_string(
            self._get(context, "caption", default=None)
        )

        nearby_text = self._as_list(
            self._get(context, "nearby_text", default=[])
        )

        preceding_text = self._as_list(
            self._get(context, "preceding_text", default=[])
        )

        following_text = self._as_list(
            self._get(context, "following_text", default=[])
        )

        strong_figure_context = self._has_strong_figure_context(
            context=context,
            semantic_result=semantic_result,
            nearby_text=nearby_text,
            preceding_text=preceding_text,
            following_text=following_text,
            caption=caption,
        )

        localized = region_role == "localized_visual_candidate"

        reasons: list[str] = []
        score = 0.0

        # ------------------------------------------------------------------
        # Strong semantic figure type
        # ------------------------------------------------------------------

        if figure_type:
            score += 0.35
            reasons.append(f"semantic figure type detected: {figure_type}")

        # ------------------------------------------------------------------
        # Confidence
        # ------------------------------------------------------------------

        if confidence >= self.STRONG_PROMOTE_CONFIDENCE:
            score += 0.30
            reasons.append(
                f"high semantic confidence: {confidence:.2f}"
            )
        elif confidence >= self.MIN_PROMOTE_CONFIDENCE:
            score += 0.20
            reasons.append(
                f"acceptable semantic confidence: {confidence:.2f}"
            )
        elif confidence > 0.0:
            score += 0.05
            reasons.append(
                f"weak semantic confidence: {confidence:.2f}"
            )

        # ------------------------------------------------------------------
        # Explicit figure context
        # ------------------------------------------------------------------

        if strong_figure_context:
            score += 0.20
            reasons.append("strong textual figure context detected")

        # ------------------------------------------------------------------
        # Caption
        # ------------------------------------------------------------------

        if caption:
            score += 0.15
            reasons.append("figure caption detected")

        # ------------------------------------------------------------------
        # Labels
        # ------------------------------------------------------------------

        if labels:
            score += 0.10
            reasons.append(
                f"explicit labels detected: {', '.join(labels)}"
            )

        # ------------------------------------------------------------------
        # Educational relevance
        # ------------------------------------------------------------------

        if educational is True:
            score += 0.10
            reasons.append("candidate marked educationally relevant")
        elif educational is False:
            score -= 0.25
            reasons.append("candidate marked non-educational")

        # ------------------------------------------------------------------
        # Concept evidence
        #
        # Concepts alone are deliberately weak evidence. Step 4 already
        # learned that generic concepts such as "function" and "graph" can
        # occur around structural page content.
        # ------------------------------------------------------------------

        meaningful_concepts = [
            concept
            for concept in concepts
            if self._is_meaningful_concept(concept)
        ]

        if meaningful_concepts:
            score += min(0.10, 0.03 * len(meaningful_concepts))
            reasons.append(
                "meaningful mathematical concepts detected"
            )

        # ------------------------------------------------------------------
        # Localized candidate bonus
        # ------------------------------------------------------------------

        if localized:
            score += 0.15
            reasons.append("candidate is a localized visual region")

        # ------------------------------------------------------------------
        # Repeated structural region penalty
        #
        # Large repeated page structures are not automatically figures.
        # Strong semantics can still make them worth retaining, but the
        # selector should be conservative about promotion.
        # ------------------------------------------------------------------

        if repeated or region_role == "repeated_structural_region":
            score -= 0.25
            reasons.append(
                "candidate is a repeated structural region"
            )

        score = self._clamp(score)

        # ------------------------------------------------------------------
        # Final decision
        # ------------------------------------------------------------------

        decision = self._decide(
            score=score,
            figure_type=figure_type,
            confidence=confidence,
            educational=educational,
            localized=localized,
            repeated=repeated
            or region_role == "repeated_structural_region",
            strong_figure_context=strong_figure_context,
            labels=labels,
            meaningful_concepts=meaningful_concepts,
        )

        evidence = {
            "figure_type": figure_type,
            "confidence": confidence,
            "labels": list(labels),
            "related_concepts": list(concepts),
            "meaningful_concepts": meaningful_concepts,
            "educationally_relevant": educational,
            "region_role": region_role,
            "repeated": repeated,
            "localized": localized,
            "caption_present": bool(caption),
            "strong_figure_context": strong_figure_context,
        }

        metadata = {
            "selector_version": "1.1",
            "selection_policy": "conservative",
            "score_semantics": (
                "evidence_strength_after_penalties; "
                "decision_is_policy_based"
            ),
        }

        return VisualCandidateSelection(
            candidate_id=candidate_id,
            decision=decision,
            score=score,
            reasons=reasons,
            evidence=evidence,
            metadata=metadata,
        )

    def select_many(
        self,
        candidates: Iterable[tuple[Any, Any]],
    ) -> list[VisualCandidateSelection]:
        """
        Select multiple candidates.

        Args:
            candidates: Iterable of
                (VisualCandidateContext, SemanticAnalysisResult) pairs.

        Returns:
            Selection results in input order.
        """
        return [
            self.select(context, semantic_result)
            for context, semantic_result in candidates
        ]

    def _decide(
        self,
        *,
        score: float,
        figure_type: str | None,
        confidence: float,
        educational: bool | None,
        localized: bool,
        repeated: bool,
        strong_figure_context: bool,
        labels: list[str],
        meaningful_concepts: list[str],
    ) -> str:
        """
        Convert evidence into a conservative decision.

        Promotion requires more than a numerical score. This prevents a
        candidate from being promoted simply because it accumulated several
        weak signals.
        """

        # Explicit negative evidence always prevents promotion.
        if educational is False:
            return "defer"

        # A localized candidate with a meaningful semantic type and adequate
        # confidence is the strongest automatic promotion path.
        if (
            localized
            and figure_type
            and confidence >= self.MIN_PROMOTE_CONFIDENCE
        ):
            return "promote"

        # A clearly identified figure with strong textual evidence can also
        # be promoted even if the region is not localized.
        if (
            figure_type
            and confidence >= self.STRONG_PROMOTE_CONFIDENCE
            and (strong_figure_context or labels)
            and not repeated
        ):
            return "promote"

        # A very strong semantic result can be promoted when accompanied by
        # explicit figure context, even without labels.
        if (
            figure_type
            and confidence >= 0.90
            and strong_figure_context
            and not repeated
        ):
            return "promote"

        # Repeated structural regions are deliberately not automatically
        # promoted. Strong evidence makes them retain-worthy.
        if repeated:
            if (
                figure_type
                or strong_figure_context
                or labels
                or meaningful_concepts
            ):
                return "retain"
            return "defer"

        # Non-repeated candidates without enough evidence remain available
        # for later processing rather than being discarded.
        if score >= 0.55:
            return "retain"

        return "defer"

    @staticmethod
    def _get(
        value: Any,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Read a field from either an object or a dictionary.

        Supports dotted dictionary/object paths such as
        ``metadata.repeated``.
        """
        current = value

        for part in key.split("."):
            if current is None:
                return default

            if isinstance(current, dict):
                if part not in current:
                    return default
                current = current[part]
            else:
                if not hasattr(current, part):
                    return default
                current = getattr(current, part)

        return current

    @staticmethod
    def _normalise_string(value: Any) -> str | None:
        if value is None:
            return None

        value = str(value).strip()

        return value or None

    @staticmethod
    def _normalise_confidence(value: Any) -> float:
        if value is None:
            return 0.0

        try:
            confidence = float(value)
        except (TypeError, ValueError):
            return 0.0

        return max(0.0, min(1.0, confidence))

    @staticmethod
    def _as_list(value: Any) -> list[str]:
        if value is None:
            return []

        if isinstance(value, str):
            value = [value]

        if not isinstance(value, (list, tuple, set)):
            return []

        result: list[str] = []

        for item in value:
            if item is None:
                continue

            text = str(item).strip()

            if text:
                result.append(text)

        return result

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, round(value, 4)))

    @staticmethod
    def _is_meaningful_concept(concept: str) -> bool:
        """
        Filter concepts that are too generic to be strong visual evidence.
        """
        normalized = concept.strip().lower()

        generic = {
            "function",
            "graph",
            "mathematics",
            "mathematical",
        }

        return normalized not in generic

    @staticmethod
    def _has_strong_figure_context(
        *,
        context: Any,
        semantic_result: Any,
        nearby_text: list[str],
        preceding_text: list[str],
        following_text: list[str],
        caption: str | None,
    ) -> bool:
        """
        Determine whether the existing textual evidence explicitly refers
        to a visual/figure.

        This intentionally uses only evidence already supplied by Step 3/4.
        """

        evidence = VisualCandidateSelector._get(
            semantic_result,
            "evidence",
            default={},
        )

        if isinstance(evidence, dict):
            explicit = evidence.get("strong_figure_context")

            if explicit is True:
                return True

        all_text: list[str] = []

        if caption:
            all_text.append(caption)

        all_text.extend(nearby_text)
        all_text.extend(preceding_text)
        all_text.extend(following_text)

        strong_terms = (
            "figure",
            "fig.",
            "diagram",
            "illustration",
            "shown below",
            "shown above",
            "as shown",
            "shown in",
            "graph of the function",
        )

        text = " ".join(all_text).lower()

        return any(term in text for term in strong_terms)