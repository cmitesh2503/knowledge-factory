# STORAGE_MODEL.md

# Knowledge Factory Storage Model

**Version:** 2.0  
**Status:** Draft  
**Owner:** Aastha Global IT Solutions

---

# 1. Purpose

This document defines how Knowledge Factory stores educational knowledge.

The storage model separates:

- Educational Knowledge
- Processing Metadata
- Provider Metadata
- Vector Data
- Binary Assets

Each category has different storage requirements and lifecycle policies.

---

# 2. Storage Principles

The storage model follows these principles.

## Separation of Concerns

Educational knowledge and operational metadata are stored independently.

## Provider Independence

Storage design must not expose provider-specific information.

## Immutable Knowledge

Knowledge Packages are immutable once published.

New versions create new packages.

## Traceability

Every stored artifact must preserve provenance.

## Scalability

Storage must support:

- Millions of documents
- Multiple curricula
- Multiple languages
- Multiple versions

---

# 3. Storage Architecture

```
Knowledge Factory

        │

        ▼

Knowledge Package

        │

 ┌──────┼─────────┬───────────┬────────────┐

 ▼      ▼         ▼           ▼

Canonical Firestore Storage   Vector DB   Assets

Document      Metadata        Embeddings  Images

Knowledge

Graph

```

---

# 4. Storage Layers

Knowledge Factory stores information in five logical layers.

---

## Layer 1

Canonical Document

Purpose

Store the provider-independent document representation.

Examples

- Pages
- Blocks
- Reading Order
- Provenance

Characteristics

- Immutable
- Versioned
- Internal artifact

---

## Layer 2

Knowledge Package

Purpose

Store educational knowledge.

Contains

- Curriculum
- Chapters
- Concepts
- Formulae
- Theorems
- Examples
- Exercises
- Figures
- Relationships

Characteristics

- Canonical
- Versioned
- Public to consumers

---

## Layer 3

Processing Metadata

Purpose

Track processing lifecycle.

Examples

- Status
- Processing duration
- Processing version
- Pipeline version
- Retry information

Characteristics

Operational data only.

---

## Layer 4

Provider Metadata

Purpose

Store provider-specific information.

Examples

- OCR provider
- AI provider
- Confidence scores
- Bounding polygons
- Provider identifiers

Characteristics

Never exposed outside Knowledge Factory.

---

## Layer 5

Embeddings

Purpose

Store vector representations.

Generated From

Semantic Chunks

Characteristics

Versioned

Regenerable

Independent of document storage

---

# 5. Storage Categories

Knowledge Factory separates storage into logical categories.

## Canonical Storage

Stores

Canonical Documents

Knowledge Packages

---

## Metadata Storage

Stores

Processing Metadata

Provider Metadata

---

## Vector Storage

Stores

Embeddings

Semantic Chunks

---

## Asset Storage

Stores

Images

Figures

Diagrams

Original Documents

---

# 6. Artifact Lifecycle

Every document follows this lifecycle.

```
Raw Document

↓

Canonical Document

↓

Knowledge Package

↓

Semantic Chunks

↓

Embeddings

↓

Published Package
```

Older versions remain available for traceability.

---

# 7. Versioning

Every stored artifact has its own version.

Examples

- Schema Version
- Package Version
- Pipeline Version
- Embedding Version

Updating embeddings must never require regenerating the Canonical Document.

---

# 8. Storage Independence

This document intentionally avoids binding the architecture to any storage technology.

Implementations may use:

- Firestore
- Cloud Storage
- Vector Databases
- Relational Databases
- Object Storage

without changing the logical storage model.

---

# 9. Data Ownership

Knowledge Factory owns all stored educational knowledge.

Consumer applications never modify stored knowledge directly.

Consumers may cache retrieved knowledge but must not overwrite canonical artifacts.

---

# 10. Data Retention

Knowledge Factory retains:

- Raw source documents
- Canonical Documents
- Knowledge Packages
- Processing Metadata
- Provider Metadata
- Embeddings

Retention policies are implementation-specific.

---

# 11. Security

Storage must support:

- Version integrity
- Auditability
- Access control
- Encryption
- Backup
- Disaster recovery

Implementation details are outside the scope of this document.

---

# 12. Future Extensions

The storage model supports future capabilities.

Examples

- Incremental document updates
- Multi-region replication
- Curriculum version history
- Knowledge snapshots
- Publisher editions
- Multi-language knowledge packages

without redesigning storage.

---

# 13. Related Documents

- VISION.md
- SYSTEM_ARCHITECTURE.md
- KNOWLEDGE_CONTRACT.md
- PIPELINE.md
- DATA_MODEL.md
- CANONICAL_SCHEMA.md