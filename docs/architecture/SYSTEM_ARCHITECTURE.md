# Knowledge Factory System Architecture

**Project:** Knowledge Factory  
**Version:** 2.0.0  
**Status:** Active  
**Type:** Detailed Technical Architecture

---

# Purpose

This document describes the detailed technical architecture of the Knowledge Factory platform.

Knowledge Factory is a cloud-native, event-driven document processing platform that transforms unstructured educational content into a technology-independent canonical knowledge model.

This document focuses on the overall system architecture and component interactions.

Detailed information is documented separately:

- Processing Pipeline → `PIPELINE.md`
- Canonical Schema → `Canonical Schema.md`
- Storage Design → `Storage Strategy.md`
- Firestore Metadata → `Firestore Metadata.md`
- Infrastructure → `Infrastructure.md`

---

# Vision

Knowledge Factory provides a reusable document processing platform capable of converting educational content into structured knowledge that can be consumed by multiple downstream applications.

The platform is independent of:

- OCR providers
- AI providers
- Cloud vendors
- Consumer applications

---

# Architectural Goals

- Technology-independent processing
- Canonical-first architecture
- Event-driven processing
- Infrastructure as Code
- Modular components
- Stateless services
- Provider abstraction
- Extensible processing pipeline

---

# Design Principles

## Documentation First

Architecture is approved before implementation.

---

## Event-Driven Processing

Processing begins automatically when new documents arrive.

Manual execution is avoided wherever possible.

---

## Canonical First

The canonical document model is the first persistent structured artifact produced by the platform.

All downstream systems consume canonical data.

---

## Technology Independence

Provider-specific implementations remain isolated inside the processing layer.

The canonical model never depends on Google Document AI or any other provider.

---

## Modular Components

Every component has a single responsibility.

Components communicate through well-defined interfaces.

---

## Stateless Processing

Processing services do not maintain session state.

State is stored only in platform-managed storage services.

---

## Infrastructure as Code

All infrastructure is provisioned using Terraform.

No production resources are created manually.

---

# High-Level Architecture

```text
                 Source Documents
                        │
                        ▼
                 Cloud Storage (Raw)
                        │
                        ▼
                    Eventarc
                        │
                        ▼
                 Cloud Run Worker
                        │
                        ▼
               Document Processing
                        │
                        ▼
               Provider Adapter Layer
                        │
                        ▼
              Canonical Transformation
                 │                 │
                 ▼                 ▼
      Cloud Storage         Firestore Metadata
    (Canonical JSON)       (Document Metadata)
                 │
                 ▼
       Downstream Applications
```

---

# Core Components

## Cloud Storage

Stores:

- Source documents
- Canonical JSON
- Archived artifacts

Cloud Storage is the primary artifact repository.

---

## Eventarc

Monitors storage events and initiates document processing.

Responsibilities:

- Event routing
- Event delivery
- Trigger management

Contains no business logic.

---

## Cloud Run Worker

Executes the processing pipeline.

Responsibilities:

- Receive events
- Download source document
- Invoke document processing provider
- Execute canonical transformation
- Publish canonical artifacts
- Update metadata

The worker remains stateless.

---

## Document Processing Provider

Responsible for extracting structured information from uploaded documents.

Current provider:

- Google Document AI

Future providers may include:

- Azure Document Intelligence
- OCR engines
- Other AI extraction services

---

## Provider Adapter

Converts provider-specific output into the Knowledge Factory canonical model.

This layer isolates provider-specific implementations from the remainder of the platform.

---

## Firestore

Stores platform metadata.

Examples include:

- Processing status
- Document metadata
- Artifact locations
- Audit information

Canonical document content is not stored in Firestore.

---

# Component Interaction

```text
Document Upload

↓

Storage Event

↓

Eventarc

↓

Cloud Run Worker

↓

Document Provider

↓

Provider Adapter

↓

Canonical JSON

↓

Validation

↓

Publication

↓

Metadata Update
```

Detailed processing flow is documented in `PIPELINE.md`.

---

# Future Pipelines

The architecture supports additional processing pipelines without modifying the ingestion architecture.

Examples include:

- Lesson Builder
- Question Extraction
- Chunk Builder
- Embedding Generation
- Vector Index Builder
- AI Enrichment
- Publishing Pipeline

Each pipeline consumes canonical artifacts rather than provider-specific outputs.

---

# Architectural Decisions

The platform follows these architectural decisions:

- Canonical schema is the primary data contract.
- Vendor-specific outputs are transient.
- Original source documents remain immutable.
- Cloud Storage stores processing artifacts.
- Firestore stores metadata only.
- Infrastructure is managed exclusively through Terraform.
- Components remain loosely coupled.
- Downstream systems consume canonical artifacts only.

---

# Non-Goals

Knowledge Factory does not provide:

- End-user APIs
- AI tutoring
- Prompt engineering
- User management
- Session management
- Business-specific workflows
- Application UI

These responsibilities belong to consumer applications such as MathVerse.

---

# Related Documents

| Document | Purpose |
|----------|---------|
| Root `ARCHITECTURE.md` | High-level architecture |
| `PIPELINE.md` | Processing pipeline |
| `Canonical Schema.md` | Canonical data model |
| `Storage Strategy.md` | Cloud Storage architecture |
| `Firestore Metadata.md` | Metadata architecture |
| `Infrastructure.md` | Infrastructure and deployment |

---

# Version History

| Version | Date | Description |
|----------|------------|--------------------------------------|
| 2.0.0 | 2026-07-30 | Refactored architecture with separated design documents |
| 1.0.0 | 2026-07-29 | Initial architecture definition |