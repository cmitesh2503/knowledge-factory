import json
from collections import Counter

from services.extractors.visual_region_detector import VisualRegionDetector
from services.extractors.visual_candidate_context import (
    VisualCandidateContextBuilder,
)
from services.extractors.visual_semantic_analyzer import (
    RuleBasedVisualSemanticAnalyzer,
)
from services.extractors.visual_candidate_selector import (
    VisualCandidateSelector,
)


PDF = "tests/data/trigonometry.pdf"


def load_canonical_document():
    """
    Load the canonical document used by the existing local pipeline.

    Update this path if your canonical JSON is stored elsewhere.
    """
    candidates = [
        r"C:\Users\mites\AppData\Local\Temp\trigonometry-canonical.json",
        "tests/data/trigonometry-canonical.json",
        "trigonometry-canonical.json",
    ]

    for path in candidates:
        try:
            with open(path, "r", encoding="utf-8") as handle:
                return json.load(handle)
        except FileNotFoundError:
            continue

    raise FileNotFoundError(
        "Could not find the canonical JSON. "
        "Provide the path to the canonical document."
    )


print("=" * 80)
print("PHASE B - VISUAL PIPELINE VALIDATION")
print("=" * 80)


# ---------------------------------------------------------------------------
# Step 1 - Visual region detection
# ---------------------------------------------------------------------------

print("\n[1] Detecting visual regions...")

regions = VisualRegionDetector().detect(PDF)

print(f"Total regions: {len(regions)}")

for region in regions:
    print(
        f"  {region.id}: "
        f"page={region.page_number}, "
        f"bbox={region.bbox}, "
        f"types={region.source_types}, "
        f"role={region.metadata.get('region_role')}, "
        f"repeated={region.metadata.get('repeated')}"
    )


# ---------------------------------------------------------------------------
# Step 2 - Load canonical document
# ---------------------------------------------------------------------------

print("\n[2] Loading canonical document...")

canonical_document = load_canonical_document()

print(
    f"Canonical pages: "
    f"{len(canonical_document.get('pages', []))}"
)


# ---------------------------------------------------------------------------
# Step 3 - Build contextual candidates
# ---------------------------------------------------------------------------

print("\n[3] Building contextual candidates...")

contexts = VisualCandidateContextBuilder().build(
    regions,
    canonical_document,
)

print(f"Contexts: {len(contexts)}")


# ---------------------------------------------------------------------------
# Step 4 - Semantic analysis
# ---------------------------------------------------------------------------

print("\n[4] Semantic analysis...")

analyzer = RuleBasedVisualSemanticAnalyzer()

candidates = analyzer.analyze_many(contexts)

print(f"Candidates: {len(candidates)}")


# ---------------------------------------------------------------------------
# Step 5 - Candidate selection
# ---------------------------------------------------------------------------

print("\n[5] Selecting visual candidates...")

selector = VisualCandidateSelector()

selections = selector.select_many(
    zip(contexts, candidates)
)

print(f"Selections: {len(selections)}")


# ---------------------------------------------------------------------------
# Semantic results
# ---------------------------------------------------------------------------

print("\n" + "=" * 80)
print("SEMANTIC RESULTS")
print("=" * 80)

for candidate in candidates:
    print(f"\n{candidate.id}")
    print(f"  page:          {candidate.page}")
    print(f"  type:          {candidate.figure_type}")
    print(f"  labels:        {candidate.labels}")
    print(f"  concepts:      {candidate.related_concepts}")
    print(
        f"  educational:   "
        f"{candidate.is_educationally_relevant}"
    )
    print(f"  confidence:    {candidate.confidence}")
    print(f"  caption:       {candidate.caption}")
    print(f"  description:   {candidate.description}")

    context_metadata = candidate.metadata.get(
        "context",
        {},
    )

    print(
        f"  region role:   "
        f"{context_metadata.get('region_role')}"
    )

    print(
        f"  repeated:      "
        f"{context_metadata.get('repeated')}"
    )


# ---------------------------------------------------------------------------
# Selection results
# ---------------------------------------------------------------------------

print("\n" + "=" * 80)
print("SELECTION RESULTS")
print("=" * 80)

for selection in selections:
    print()
    print(selection.candidate_id)
    print(f"  decision: {selection.decision}")
    print(f"  score:    {selection.score:.2f}")
    print(f"  reasons:  {selection.reasons}")


# ---------------------------------------------------------------------------
# Selection summary
# ---------------------------------------------------------------------------

print("\n" + "=" * 80)
print("SELECTION SUMMARY")
print("=" * 80)

decision_counts = Counter(
    selection.decision
    for selection in selections
)

promoted = decision_counts.get("promote", 0)
retained = decision_counts.get("retain", 0)
deferred = decision_counts.get("defer", 0)

print(f"Promoted: {promoted}")
print(f"Retained: {retained}")
print(f"Deferred: {deferred}")
print(f"Total selections: {len(selections)}")


# ---------------------------------------------------------------------------
# Overall visual pipeline summary
# ---------------------------------------------------------------------------

print("\n" + "=" * 80)
print("PIPELINE SUMMARY")
print("=" * 80)

typed = [
    candidate
    for candidate in candidates
    if candidate.figure_type is not None
]

with_labels = [
    candidate
    for candidate in candidates
    if candidate.labels
]

with_concepts = [
    candidate
    for candidate in candidates
    if candidate.related_concepts
]

educational = [
    candidate
    for candidate in candidates
    if candidate.is_educationally_relevant is True
]

localized = [
    candidate
    for candidate in candidates
    if candidate.metadata.get("context", {}).get(
        "region_role"
    ) == "localized_visual_candidate"
]

repeated = [
    candidate
    for candidate in candidates
    if candidate.metadata.get("context", {}).get(
        "repeated"
    ) is True
]

print(f"Total regions:             {len(regions)}")
print(f"Total contexts:            {len(contexts)}")
print(f"Total candidates:          {len(candidates)}")
print(f"Typed candidates:          {len(typed)}")
print(f"Candidates with labels:    {len(with_labels)}")
print(f"Candidates with concepts:  {len(with_concepts)}")
print(f"Educationally relevant:    {len(educational)}")
print(f"Localized candidates:      {len(localized)}")
print(f"Repeated candidates:       {len(repeated)}")

print("\nValidation complete.")
