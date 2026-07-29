# Knowledge Factory Architecture

**Version:** 1.0.0  
**Status:** Draft  
**Last Updated:** 2026-07-29

---

# 1. Purpose

Knowledge Factory is a cloud-native, event-driven data engineering platform that transforms educational documents into a technology-independent canonical knowledge model.

It serves as the central knowledge ingestion platform for MathVerse and other future AI learning products.

Knowledge Factory is responsible for acquiring, processing, normalizing, and publishing educational content while remaining independent of any specific OCR, AI, cloud provider, or consumer application.

---

# 2. Vision

Build a reusable, scalable, and technology-independent knowledge processing platform capable of converting any educational document into structured knowledge assets.

Knowledge Factory is not an application.

It is a data engineering platform.

---

# 3. Design Principles

## Documentation First

Architecture is documented before implementation.

---

## Event-Driven

Every processing stage is triggered by an event.

No manual execution.

---

## Technology Independent

Vendor-specific formats are never exposed outside the ingestion pipeline.

The canonical schema is the only persistent data contract.

---

## Modular Pipelines

Each pipeline performs one responsibility.

Pipelines communicate through storage artifacts and metadata.

---

## Cloud Native

Infrastructure is fully managed using Terraform.

Services remain stateless.

---

## Infrastructure as Code

Every cloud resource is provisioned using Terraform.

No manual configuration in production.

---

# 4. High-Level Architecture

```text
                     Upload PDF
                          │
                          ▼
              Raw Storage Bucket
                          │
                 Object Finalized
                          │
                          ▼
                     Eventarc
                          │
                          ▼
                Cloud Run Worker
                          │
                 Call Document AI
                          │
                          ▼
          Canonical Schema Transformation
                 │                    │
                 ▼                    ▼
      Processed Storage Bucket   Firestore Metadata
```

---

# 5. Core Components

## Cloud Storage

### Raw Bucket

Stores original uploaded PDFs.

Example

```
raw/
    cbse/
        grade10/
            mathematics/
                matrices.pdf
```

---

### Processed Bucket

Stores Knowledge Factory artifacts.

Example

```
processed/
    canonical/
        cbse/
            grade10/
                mathematics/
                    matrices.json
```

---

## Eventarc

Listens for object creation events in the Raw bucket.

Triggers the Cloud Run Worker.

Contains no business logic.

---

## Cloud Run Worker

Responsible for executing the ingestion pipeline.

Responsibilities

- Receive storage event
- Read uploaded PDF
- Call Document AI
- Transform output into the Knowledge Factory Canonical Schema
- Store canonical JSON
- Write Firestore metadata
- Return success

The worker is stateless.

---

## Document AI

Provides OCR and document structure extraction.

Its output is used only during processing.

Vendor-specific output is never persisted.

---

## Firestore

Acts as the metadata catalog.

Stores

- Document ID
- Processing Status
- Canonical URI
- Source PDF URI
- Pipeline Version
- Created Timestamp
- Updated Timestamp

Firestore never stores document content.

---

# 6. Canonical Data Model

Knowledge Factory persists only its own canonical schema.

This schema represents the official contract between Knowledge Factory and downstream systems.

Vendor-specific formats are transient and discarded after transformation.

---

# 7. Processing Pipeline

```
PDF

↓

Raw Bucket

↓

Eventarc

↓

Cloud Run Worker

↓

Document AI

↓

Canonical Transformation

↓

Processed Bucket

↓

Firestore Metadata
```

The pipeline is fully automated.

No manual intervention is required.

---

# 8. Storage Strategy

Cloud Storage

Stores immutable processing artifacts.

Examples

- PDF
- Canonical JSON
- Future lesson JSON
- Future chunk JSON

Firestore

Stores searchable metadata.

---

# 9. Future Pipelines

Future processing stages may include

- Lesson Builder
- Exercise Extraction
- Chunk Builder
- Embedding Pipeline
- Vector Index Builder
- AI Enrichment
- Publishing Pipeline

These pipelines consume canonical artifacts.

They never consume vendor-specific formats.

---

# 10. Repository Structure

```
knowledge-factory/

├── docs/
├── terraform/
├── worker/
├── pipelines/
├── shared/
└── schemas/
```

---

# 11. Design Rules

### Rule 1

Canonical schema is the first persisted structured artifact.

---

### Rule 2

Vendor-specific formats must never leave the ingestion worker.

---

### Rule 3

All downstream pipelines consume canonical artifacts.

---

### Rule 4

Cloud Storage stores artifacts.

Firestore stores metadata.

---

### Rule 5

Infrastructure is managed exclusively through Terraform.

---

### Rule 6

Every architectural change requires:

- Architecture update
- ADR update
- Implementation

Documentation precedes code.

---

# 12. Version History

| Version | Date | Description |
|----------|------------|---------------------------|
| 1.0.0 | 2026-07-29 | Initial architecture definition |

# 13. Non-Goals

Knowledge Factory does not:

- Serve end-user APIs
- Implement business workflows
- Persist vendor-specific document formats
- Contain application-specific logic
- Perform AI tutoring
- Manage user sessions
- Render educational content

These responsibilities belong to consumer applications such as MathVerse.