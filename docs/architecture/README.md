# Architecture Documentation

**Project:** Knowledge Factory  
**Document Version:** 1.0  
**Status:** Active  
**Type:** Architecture Documentation Index

---

# Purpose

This directory contains the detailed architecture documentation for the Knowledge Factory platform.

While the root `ARCHITECTURE.md` provides a high-level overview of the system, the documents in this directory describe individual architectural domains in greater detail.

---

# Documentation Structure

| Document | Purpose |
|----------|---------|
| ARCHITECTURE.md | Detailed system architecture and component interactions |
| PIPELINE.md | End-to-end document processing pipeline |
| Canonical Schema.md | Technology-independent canonical document model |
| Storage Strategy.md | Cloud Storage architecture and object lifecycle |
| Firestore Metadata.md | Firestore collections, metadata model, and indexing strategy |
| Infrastructure.md | Infrastructure architecture, Terraform modules, deployment order, and GCP resources |

---

# Recommended Reading Order

New contributors should review the architecture documents in the following order:

1. `README.md` *(Repository Overview)*
2. `ARCHITECTURE.md` *(Root)*
3. `REPOSITORY_INDEX.md`
4. `docs/architecture/README.md`
5. `docs/architecture/ARCHITECTURE.md`
6. `docs/architecture/PIPELINE.md`
7. `docs/architecture/Canonical Schema.md`
8. `docs/architecture/Storage Strategy.md`
9. `docs/architecture/Firestore Metadata.md`
10. `docs/architecture/Infrastructure.md`

---

# Architecture Principles

The architecture documentation follows these principles:

- Technology-independent design
- Canonical-first processing
- Modular components
- Infrastructure as Code
- Separation of concerns
- Clear ownership of responsibilities
- Extensible architecture for future providers

---

# Document Responsibilities

## ARCHITECTURE.md

Describes the detailed system architecture, major components, processing flow, and interactions between components.

---

## PIPELINE.md

Documents the complete document processing pipeline from ingestion through publishing.

Defines:

- Pipeline stages
- Inputs and outputs
- Processing responsibilities
- Error handling
- Retry flow

---

## Canonical Schema.md

Defines the canonical document representation used throughout the platform.

Includes:

- Document schema
- Metadata
- Sections
- Elements
- Validation rules
- Versioning

---

## Storage Strategy.md

Documents the storage architecture.

Includes:

- Cloud Storage buckets
- Folder hierarchy
- Object naming conventions
- Lifecycle policies
- Archival strategy

---

## Firestore Metadata.md

Defines the Firestore data model.

Includes:

- Collections
- Documents
- Metadata schema
- Relationships
- Indexing strategy

---

## Infrastructure.md

Documents the deployment architecture.

Includes:

- Google Cloud services
- Terraform modules
- Module dependencies
- Deployment sequence
- Environment structure
- Current implementation status

---

# Related Documents

| Document | Purpose |
|----------|---------|
| README.md | Repository overview |
| ARCHITECTURE.md | High-level architecture |
| REPOSITORY_INDEX.md | Repository navigation |
| docs/implementation/IMPLEMENTATION_ROADMAP.md | Implementation progress |

---

# Maintenance

Update this index whenever:

- A new architecture document is added.
- An architecture document is renamed or removed.
- Responsibilities change between documents.
- The overall architecture evolves.

The goal is to keep every architecture topic documented in exactly one place, avoiding duplication and maintaining a clear separation of responsibilities.