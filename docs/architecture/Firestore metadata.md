# ADR-004: Firestore Metadata Catalog

**Status:** Accepted

**Date:** 2026-07-29

**Decision Makers:** Knowledge Factory Architecture Team

---

# Context

Knowledge Factory processes documents through multiple independent pipelines.

The platform requires a centralized catalog to:

- Track document processing.
- Discover processed artifacts.
- Monitor pipeline execution.
- Enable downstream pipelines to locate artifacts.

The platform does **not** require Firestore to store document content.

---

# Decision

Firestore SHALL act as the **Metadata Catalog** for Knowledge Factory.

Firestore stores only metadata required to identify, locate, and monitor documents and their processing lifecycle.

All document artifacts remain in Cloud Storage.

Firestore is **not** an artifact repository.

---

# Responsibilities

Firestore is responsible for:

- Document registration
- Processing status
- Pipeline tracking
- Artifact references
- Version information
- Audit timestamps
- Processing errors (if any)

Firestore does not store:

- PDF files
- Canonical JSON
- Lesson JSON
- Chunk JSON
- Embeddings
- Any large document content

---

# Metadata Model

Each processed document is represented by a single metadata record.

```
Document
    │
    ├── Identity
    ├── Source
    ├── Processing
    ├── Artifacts
    ├── Version
    └── Audit
```

---

# Example Metadata

```json
{
  "documentId": "cbse-g10-matrices",
  "title": "Matrices",
  "board": "CBSE",
  "grade": "10",
  "subject": "Mathematics",

  "status": "COMPLETED",

  "source": {
    "pdfUri": "gs://knowledge-factory-raw/cbse/grade10/mathematics/matrices.pdf"
  },

  "artifacts": {
    "canonicalUri": "gs://knowledge-factory-processed/canonical/cbse/grade10/mathematics/matrices.json"
  },

  "pipeline": {
    "version": "1.0.0"
  },

  "audit": {
    "createdAt": "2026-07-29T10:30:00Z",
    "updatedAt": "2026-07-29T10:31:45Z"
  }
}
```

---

# Processing Lifecycle

```
Uploaded

↓

Processing

↓

Completed

↓

Published (Future)

↓

Archived (Future)
```

Each status transition updates the metadata record.

---

# Rationale

Using Firestore as a metadata catalog provides:

- Fast document lookup
- Pipeline visibility
- Operational monitoring
- Efficient querying
- Lightweight metadata storage
- Clear separation from artifact storage

---

# Alternatives Considered

## Option A – Store Everything in Firestore

### Advantages

- Single database

### Disadvantages

- Poor scalability
- Document size limits
- Expensive storage
- Mixing metadata with content

**Decision:** Rejected.

---

## Option B – No Metadata Catalog

```
Cloud Storage only
```

### Advantages

- Minimal infrastructure

### Disadvantages

- Difficult discovery
- No pipeline tracking
- No processing status
- No operational visibility

**Decision:** Rejected.

---

## Option C – Firestore as Metadata Catalog (Selected)

```
Cloud Storage
      │
      │ Artifacts
      ▼

Firestore
      │
Metadata Catalog
```

### Advantages

- Lightweight
- Scalable
- Queryable
- Supports future pipeline orchestration
- Clear separation of concerns

**Decision:** Accepted.

---

# Design Rules

1. One Firestore document represents one source document.
2. Firestore stores metadata only.
3. Artifact content is never duplicated in Firestore.
4. Every artifact must be referenced by URI.
5. Metadata reflects the latest processing state.
6. Metadata must remain synchronized with Cloud Storage artifacts.

---

# Related Documents

- ARCHITECTURE.md
- PIPELINE.md
- ADR-001: Canonical Schema as the Primary Data Contract
- ADR-002: Event-Driven Document Ingestion Pipeline
- ADR-003: Storage Strategy