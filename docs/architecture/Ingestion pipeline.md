# ADR-002: Event-Driven Document Ingestion Pipeline

**Status:** Accepted

**Date:** 2026-07-29

**Decision Makers:** Knowledge Factory Architecture Team

---

# Context

Knowledge Factory requires a fully automated mechanism to ingest educational documents and transform them into the platform's canonical knowledge model.

The ingestion process must:

- Execute without manual intervention.
- Scale automatically with document uploads.
- Support stateless processing.
- Be independent of downstream consumer applications.
- Produce consistent, repeatable outputs.

---

# Decision

Knowledge Factory SHALL implement an event-driven ingestion pipeline.

The ingestion pipeline begins when a PDF is uploaded to the Raw Storage Bucket.

A storage event automatically triggers the ingestion worker, which processes the document and produces the platform's canonical artifact.

The pipeline completes by:

1. Persisting the canonical JSON to the Processed Storage Bucket.
2. Recording document metadata in Firestore.

No manual execution or scheduled jobs are required.

---

# Pipeline Flow

```
PDF Upload
     │
     ▼
Raw Storage Bucket
     │
Object Finalized Event
     │
     ▼
Event Router
     │
     ▼
Ingestion Worker
     │
     ▼
Document Processing Engine
     │
     ▼
Canonical Schema Transformation
     │
     ├────────► Processed Storage Bucket
     │
     └────────► Firestore Metadata Catalog
```

---

# Processing Responsibilities

The ingestion worker is responsible for:

- Receiving storage events.
- Reading uploaded PDF documents.
- Extracting document structure using the configured processing engine.
- Transforming extracted content into the Knowledge Factory Canonical Schema.
- Persisting canonical artifacts.
- Updating processing metadata.
- Reporting processing status.

---

# Rationale

This architecture provides:

- Fully automated document processing.
- Horizontal scalability.
- Stateless execution.
- Loose coupling between services.
- Technology independence.
- Clear separation between ingestion and downstream pipelines.

---

# Alternatives Considered

## Option A – Manual Processing

```
Upload PDF

↓

Manual Execution

↓

Processing
```

### Advantages

- Simple implementation.

### Disadvantages

- Not scalable.
- Operational overhead.
- Human intervention required.

**Decision:** Rejected.

---

## Option B – Scheduled Batch Processing

```
Upload PDF

↓

Scheduled Job

↓

Process Queue
```

### Advantages

- Easier batch processing.

### Disadvantages

- Increased latency.
- Delayed availability.
- Additional scheduling complexity.

**Decision:** Rejected.

---

## Option C – Event-Driven Processing (Selected)

```
Upload PDF

↓

Storage Event

↓

Ingestion Worker

↓

Canonical Artifact
```

### Advantages

- Near real-time processing.
- Automatic scaling.
- Stateless execution.
- Cloud-native architecture.
- Simplified operations.

**Decision:** Accepted.

---

# Consequences

## Positive

- Documents are processed automatically.
- No operational scheduling is required.
- Processing scales with document volume.
- Every uploaded document follows the same workflow.
- Downstream systems receive consistent canonical artifacts.

## Negative

- Event delivery and processing failures must be monitored.
- Processing must be idempotent to safely handle retries.

---

# Design Rules

1. Every document upload generates an ingestion event.
2. The ingestion pipeline must be fully automated.
3. Each document is processed independently.
4. Processing must be idempotent.
5. The ingestion pipeline produces only canonical artifacts.
6. Downstream pipelines must consume canonical artifacts only.

---

# Related Documents

- ARCHITECTURE.md
- PIPELINE.md
- ADR-001: Canonical Schema as the Primary Data Contract
- ADR-003: Storage Strategy
- ADR-004: Firestore Metadata Catalog