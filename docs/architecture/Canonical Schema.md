# ADR-001: Canonical Schema as the Primary Data Contract

**Status:** Accepted

**Date:** 2026-07-29

**Decision Makers:** Knowledge Factory Architecture Team

---

# Context

Knowledge Factory ingests educational PDF documents using an OCR/document understanding engine.

Different OCR providers produce different output formats, for example:

- Google Document AI
- Azure Document Intelligence
- AWS Textract
- LlamaParse
- Marker
- Unstructured

Persisting vendor-specific output would tightly couple the platform to a single technology and require downstream pipelines to understand multiple document formats.

Knowledge Factory requires a stable, technology-independent contract for all downstream processing.

---

# Decision

Knowledge Factory SHALL persist only the **Knowledge Factory Canonical Schema**.

Vendor-specific document formats are considered transient processing artifacts.

The ingestion pipeline transforms vendor output into the canonical schema before any data is persisted.

The canonical schema is the first persisted structured artifact produced by the platform.

---

# Rationale

This decision provides:

- Technology independence
- Stable data contracts
- Simplified downstream pipelines
- Easier migration between OCR providers
- Consistent processing regardless of document source

Only the ingestion adapter is responsible for understanding vendor-specific formats.

---

# Alternatives Considered

## Option A — Persist Vendor Output

```
PDF
    ↓
Document AI
    ↓
Persist Document AI JSON
    ↓
Canonical Transformation
```

### Advantages

- Easier debugging
- Original OCR output preserved

### Disadvantages

- Tight coupling to vendor schema
- Downstream systems become vendor-aware
- More complex processing pipelines
- Harder migration to another OCR provider

**Decision:** Rejected.

---

## Option B — Persist Canonical Schema (Selected)

```
PDF
    ↓
Document AI
    ↓
Canonical Transformation
    ↓
Persist Canonical JSON
```

### Advantages

- Technology independent
- Stable contract
- Cleaner architecture
- Easier maintenance
- Future-proof

**Decision:** Accepted.

---

# Consequences

## Positive

- Downstream pipelines consume a single schema.
- OCR providers can be replaced with minimal impact.
- Consumer applications remain independent of OCR technology.
- Canonical JSON becomes the official platform artifact.

## Negative

- Vendor-specific OCR output is not available after processing.
- Debugging relies on logs and processing metadata rather than persisted raw OCR output.

---

# Design Rules

1. Canonical JSON is the first persisted structured artifact.
2. Vendor-specific formats must not be exposed outside the ingestion worker.
3. All downstream pipelines consume only the canonical schema.
4. Consumer applications must never depend on vendor-specific document formats.

---

# Impact

This decision affects:

- Ingestion Pipeline
- Storage Strategy
- Firestore Catalog
- Lesson Builder
- Chunk Builder
- Embedding Pipeline
- Publishing Pipeline
- All consumer applications

---

# Related Documents

- ARCHITECTURE.md
- PIPELINE.md
- ADR-002: Ingestion Pipeline
- ADR-003: Storage Strategy