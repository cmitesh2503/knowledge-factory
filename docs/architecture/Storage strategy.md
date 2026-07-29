# ADR-003: Storage Strategy

**Status:** Accepted

**Date:** 2026-07-29

**Decision Makers:** Knowledge Factory Architecture Team

---

# Context

Knowledge Factory processes educational documents through multiple independent pipelines.

Each pipeline produces artifacts that are consumed by subsequent pipelines and consumer applications.

The platform requires a storage strategy that:

- Separates large artifacts from searchable metadata.
- Supports immutable processing outputs.
- Scales with growing document volumes.
- Enables independent pipeline execution.
- Maintains technology independence.

---

# Decision

Knowledge Factory SHALL separate storage into two categories:

1. **Artifact Storage**
2. **Metadata Storage**

Artifacts are stored in Cloud Storage.

Metadata is stored in Firestore.

This separation ensures that large documents remain in object storage while Firestore acts as a lightweight catalog for discovery, tracking, and pipeline coordination.

---

# Storage Architecture

```
                   Knowledge Factory

                  +-------------------+
                  |     Firestore     |
                  | Metadata Catalog  |
                  +-------------------+
                           ▲
                           │
                           │ References
                           │
+------------------------------------------------------+
|                  Cloud Storage                        |
|------------------------------------------------------|
| Raw Bucket        | Original uploaded PDFs           |
| Processed Bucket  | Canonical JSON and future assets |
+------------------------------------------------------+
```

---

# Artifact Storage

Artifact storage contains immutable files produced during processing.

Examples include:

- Original PDF
- Canonical JSON
- Lesson JSON (future)
- Chunk JSON (future)
- Embedding files (future)
- Published knowledge packages (future)

Artifacts are never stored inside Firestore.

---

# Metadata Storage

Firestore stores metadata required to:

- Discover processed documents.
- Track processing status.
- Locate artifacts.
- Support pipeline orchestration.
- Enable monitoring and auditing.

Metadata documents reference artifact locations but never duplicate artifact content.

---

# Storage Responsibilities

## Cloud Storage

Responsible for:

- Large files
- Immutable artifacts
- Versioned outputs
- Long-term retention

Cloud Storage is the system of record for all generated artifacts.

---

## Firestore

Responsible for:

- Document catalog
- Processing status
- Pipeline state
- Artifact references
- Operational metadata

Firestore is the system of record for metadata only.

---

# Rationale

Separating artifacts from metadata provides:

- Better scalability
- Lower database costs
- Faster metadata queries
- Simpler pipeline coordination
- Independent artifact lifecycle management
- Reduced duplication

---

# Alternatives Considered

## Option A – Store Everything in Firestore

```
Firestore

├── Metadata
├── Canonical JSON
├── Lessons
└── Chunks
```

### Advantages

- Single storage system.

### Disadvantages

- Poor scalability.
- Firestore document size limitations.
- Expensive for large documents.
- Inefficient for large JSON artifacts.

**Decision:** Rejected.

---

## Option B – Store Everything in Cloud Storage

```
Cloud Storage

├── PDF
├── Metadata
├── Canonical
└── Lessons
```

### Advantages

- Simple storage model.

### Disadvantages

- Difficult metadata querying.
- No efficient document tracking.
- Poor operational visibility.

**Decision:** Rejected.

---

## Option C – Hybrid Storage (Selected)

```
Cloud Storage
    │
    ├── Artifacts
    │
    ▼
Firestore
    │
    └── Metadata
```

### Advantages

- Scalable architecture.
- Clear separation of concerns.
- Efficient metadata queries.
- Optimized storage costs.
- Independent pipeline execution.

**Decision:** Accepted.

---

# Consequences

## Positive

- Large artifacts remain outside the database.
- Firestore remains lightweight and responsive.
- Pipelines exchange artifacts through object storage.
- Storage scales independently of metadata.

## Negative

- Applications must resolve artifact references from Firestore.
- Artifact lifecycle and metadata lifecycle must remain synchronized.

---

# Design Rules

1. Cloud Storage stores all processing artifacts.
2. Firestore stores metadata only.
3. Firestore never stores document content.
4. Artifacts are immutable after publication.
5. Every artifact must have corresponding metadata.
6. Metadata must reference artifacts using storage URIs.

---

# Related Documents

- ARCHITECTURE.md
- PIPELINE.md
- ADR-001: Canonical Schema as the Primary Data Contract
- ADR-002: Event-Driven Document Ingestion Pipeline
- ADR-004: Firestore Metadata Catalog
One improvement I'd make

Instead of saying:

Cloud Storage stores artifacts

I'd be even more explicit and define artifact classes, so future developers know exactly what belongs there.

Artifact Class	Examples
Source	PDF
Canonical	canonical.json
Learning	lesson.json, exercise.json
AI	chunks.json, embeddings
Published	Knowledge packages for consumer applications

This gives the storage strategy room to grow without changing the underlying architecture. It's the kind of detail that makes an ADR useful years later, not just during the initial implementation.