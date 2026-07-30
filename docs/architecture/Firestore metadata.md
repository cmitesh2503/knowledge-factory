# Firestore Metadata Architecture

**Project:** Knowledge Factory  
**Document Version:** 1.0  
**Status:** Active  
**Type:** Metadata Storage Architecture

---

# Purpose

This document defines how metadata is stored in Google Firestore within the Knowledge Factory platform.

Firestore stores metadata required for document discovery, processing status, auditing, and downstream integrations.

The canonical document itself remains stored in Cloud Storage. Firestore stores metadata and references to those artifacts.

---

# Design Principles

- Firestore stores metadata only.
- Canonical JSON remains the source of truth.
- Documents are immutable after successful publication.
- Collections should be optimized for lookup rather than document storage.
- Metadata should remain independent of document processing providers.

---

# Firestore Responsibilities

Firestore is responsible for:

- Document discovery
- Processing status
- Processing history
- Document metadata
- Storage references
- Audit information

Firestore is **not** responsible for:

- Storing source documents
- Storing canonical JSON
- Storing extracted images
- Storing large binary content

---

# High-Level Architecture

```text
                 Source Document
                        │
                        ▼
               Document Processing
                        │
                        ▼
               Canonical JSON Created
                        │
          ┌─────────────┴─────────────┐
          ▼                           ▼
Cloud Storage                  Firestore Metadata
(Canonical JSON)              (Metadata + References)
```

---

# Collection Structure

Recommended Firestore collections:

```text
knowledge-factory/

├── documents/
├── processing_jobs/
├── processing_history/
└── system_metadata/
```

---

# documents Collection

Stores one document per processed source document.

Example fields:

```text
Document ID
Document Name
Document Type
Language
Page Count
Schema Version
Processing Status
Created Timestamp
Updated Timestamp
Canonical JSON Location
Source Document Location
```

---

# processing_jobs Collection

Tracks active and completed processing jobs.

Example fields:

```text
Job ID
Document ID
Provider
Processing Start Time
Processing End Time
Status
Duration
Error Message
Retry Count
```

---

# processing_history Collection

Stores historical processing events.

Example fields:

```text
History ID
Document ID
Event Type
Timestamp
Status
Description
```

---

# system_metadata Collection

Stores platform configuration metadata.

Examples:

- Current schema version
- Supported providers
- Platform version
- Processing configuration

---

# Metadata Relationships

```text
Document
    │
    ├── Processing Job
    │
    ├── Processing History
    │
    └── Canonical JSON (Cloud Storage)
```

---

# Processing Status

Recommended document states:

```text
UPLOADED

PROCESSING

NORMALIZED

VALIDATED

PUBLISHED

FAILED

ARCHIVED
```

---

# Metadata Lifecycle

```text
Upload

↓

Create Metadata

↓

Processing

↓

Update Status

↓

Publish Canonical JSON

↓

Store Reference

↓

Archive
```

---

# Indexing Strategy

Indexes should support:

- Document lookup
- Processing status
- Processing date
- Source document
- Provider
- Processing failures

Avoid unnecessary composite indexes.

---

# Security

Recommendations:

- IAM-based access
- Least privilege
- No public access
- Encryption at rest
- Audit logging enabled

---

# Data Retention

Recommended strategy:

| Collection | Retention |
|------------|-----------|
| documents | Permanent |
| processing_jobs | Configurable |
| processing_history | Long-term |
| system_metadata | Permanent |

---

# Current Implementation

The current implementation stores:

- Document metadata
- Processing metadata
- References to canonical JSON stored in Cloud Storage

The canonical document remains outside Firestore.

---

# Future Enhancements

Potential future additions include:

- Document tags
- Search metadata
- Processing metrics
- AI enrichment metadata
- Version history
- Quality scores
- User annotations

---

# Related Documents

| Document | Purpose |
|----------|---------|
| ARCHITECTURE.md | High-level architecture |
| PIPELINE.md | Processing pipeline |
| Canonical Schema.md | Canonical document model |
| Storage Strategy.md | Cloud Storage architecture |
| Infrastructure.md | Terraform and deployment architecture |