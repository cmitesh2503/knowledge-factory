# Knowledge Factory Processing Pipelines

**Version:** 1.0.0  
**Status:** Draft  
**Last Updated:** 2026-07-29

---

# 1. Purpose

This document defines the end-to-end processing pipelines of the Knowledge Factory platform.

A pipeline is an autonomous, event-driven workflow responsible for transforming one artifact into another.

Each pipeline:

- Has a single responsibility
- Is independently deployable
- Produces well-defined outputs
- Uses the canonical schema as the contract between pipelines

---

# 2. Pipeline Architecture

```
                    Upload PDF
                         │
                         ▼
                 Raw Storage Bucket
                         │
                  Object Finalized
                         │
                         ▼
                 Pipeline 1
              Document Ingestion
                         │
                         ▼
                 Canonical JSON
                         │
                         ▼
               Processed Bucket
                         │
                         ▼
                 Firestore Catalog
                         │
      ┌──────────────────┼──────────────────┐
      ▼                  ▼                  ▼
 Pipeline 2         Pipeline 3         Pipeline 4
 Lesson Builder     Chunk Builder      Publishing
```

---

# 3. Pipeline Design Principles

- Event-driven
- Stateless execution
- Single responsibility
- Technology independent
- Immutable outputs
- Idempotent processing
- Canonical schema between pipelines

---

# 4. Pipeline 1 – Document Ingestion

## Purpose

Transform an uploaded PDF into the Knowledge Factory Canonical Schema.

---

## Trigger

Cloud Storage Object Finalized Event

---

## Input

```
PDF
```

---

## Processing Steps

```
Receive Storage Event

↓

Download PDF

↓

Document AI OCR

↓

Canonical Transformation

↓

Generate Canonical JSON

↓

Upload Canonical JSON

↓

Write Firestore Metadata
```

---

## Output

### Processed Bucket

```
processed/
    canonical/
        cbse/
            grade10/
                mathematics/
                    matrices.json
```

### Firestore

Metadata record

---

## Status

✅ Active (Version 1)

---

# 5. Pipeline 2 – Lesson Builder

## Purpose

Generate lesson-oriented learning content from canonical documents.

---

## Trigger

Canonical JSON Created

---

## Input

```
Canonical JSON
```

---

## Output

```
lesson.json
```

---

## Status

Planned

---

# 6. Pipeline 3 – Chunk Builder

## Purpose

Split canonical content into semantic chunks for AI retrieval.

---

## Trigger

Canonical JSON Created

---

## Input

```
Canonical JSON
```

---

## Output

```
chunks.json
```

---

## Status

Planned

---

# 7. Pipeline 4 – Embedding Builder

## Purpose

Generate vector embeddings from semantic chunks.

---

## Trigger

Chunk JSON Created

---

## Input

```
chunks.json
```

---

## Output

```
Vector Index
```

---

## Status

Planned

---

# 8. Pipeline 5 – Publishing

## Purpose

Publish validated knowledge assets for consumer applications.

---

## Trigger

Pipeline Approval

---

## Input

- Canonical JSON
- Lesson JSON
- Chunk JSON

---

## Output

Published Knowledge Package

---

## Status

Planned

---

# 9. Canonical Data Flow

```
PDF

↓

Document AI

↓

Canonical JSON

↓

Lesson JSON

↓

Chunk JSON

↓

Embeddings

↓

Published Knowledge
```

The canonical schema is the contract between every pipeline.

---

# 10. Pipeline Ownership

| Pipeline | Responsibility |
|----------|----------------|
| Pipeline 1 | Document ingestion |
| Pipeline 2 | Lesson generation |
| Pipeline 3 | Chunk generation |
| Pipeline 4 | Embedding generation |
| Pipeline 5 | Knowledge publishing |

---

# 11. Error Handling

Each pipeline must:

- Log processing status
- Retry transient failures
- Record failure metadata
- Never overwrite successful artifacts
- Support idempotent reprocessing

---

# 12. Versioning

Pipeline outputs must include:

- Pipeline Version
- Processing Timestamp
- Source Document ID
- Canonical Schema Version

---

# 13. Pipeline Roadmap

| Pipeline | Status |
|----------|--------|
| Document Ingestion | ✅ Active |
| Lesson Builder | Planned |
| Chunk Builder | Planned |
| Embedding Builder | Planned |
| Publishing Pipeline | Planned |

---

# 14. Processing Lifecycle

```
Upload PDF
      │
      ▼
Pipeline 1
(Document Ingestion)
      │
      ▼
Canonical JSON
      │
      ├────────► Firestore Metadata
      │
      ▼
Pipeline 2
(Lesson Builder)
      │
      ▼
Pipeline 3
(Chunk Builder)
      │
      ▼
Pipeline 4
(Embedding Builder)
      │
      ▼
Pipeline 5
(Publishing)
      │
      ▼
Knowledge Ready for Consumers
```

---

# Version History

| Version | Date | Description |
|----------|------------|----------------------------|
| 1.0.0 | 2026-07-29 | Initial processing pipeline definition |