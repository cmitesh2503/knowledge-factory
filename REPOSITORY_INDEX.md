# Repository Index

**Project:** Knowledge Factory  
**Document Version:** 1.0  
**Status:** Active  
**Type:** Repository Navigation Guide

---

# Purpose

This document is the authoritative index of the Knowledge Factory repository.

It provides a structured overview of the repository layout, explains the responsibility of each directory, and serves as the primary navigation guide for contributors.

This document reflects the **current repository implementation** and must be updated whenever the repository structure changes.

---

# Repository Structure

```text
knowledge-factory/
│
├── README.md
├── ARCHITECTURE.md
├── REPOSITORY_INDEX.md
│
├── docs/
│   ├── architecture/
│   ├── adr/
│   ├── audit/
│   ├── diagrams/
│   └── implementation/
│
├── infrastructure/
│   ├── scripts/
│   └── terraform/
│
└── .gitignore
```

---

# Root Files

| File | Purpose |
|------|---------|
| README.md | Repository entry point and getting started guide |
| ARCHITECTURE.md | High-level system architecture |
| REPOSITORY_INDEX.md | Repository navigation guide |
| .gitignore | Git ignore rules |

---

# Directory Overview

## docs/

Contains all project documentation.

```text
docs/
├── architecture/
├── adr/
├── audit/
├── diagrams/
└── implementation/
```

---

### architecture/

Contains all technical architecture documentation.

Contents include:

- Overall architecture
- Processing pipeline
- Canonical schema
- Storage design
- Firestore metadata
- Infrastructure architecture

---

### adr/

Architecture Decision Records (ADRs).

Each ADR documents a significant architectural decision together with its rationale and consequences.

---

### audit/

Repository audit documentation.

These documents record repository reviews, cleanup activities, findings, and implementation decisions.

Audit documentation may be archived after repository stabilization.

---

### diagrams/

Architecture diagrams and supporting visuals.

Examples:

- Mermaid diagrams
- PlantUML diagrams
- Images
- Architecture illustrations

---

### implementation/

Implementation planning documents.

Contains:

- Implementation roadmap
- Deployment progress
- Current development status
- Future implementation phases

---

# infrastructure/

Infrastructure as Code (IaC) for Knowledge Factory.

```text
infrastructure/
├── scripts/
└── terraform/
```

---

## scripts/

Utility scripts supporting infrastructure deployment and maintenance.

---

## terraform/

Terraform configuration for provisioning Google Cloud resources.

Current infrastructure includes:

- Google Cloud Storage
- IAM
- Service Accounts
- Firestore
- Document AI
- Cloud Run
- Workflows

---

# Documentation Reading Order

For new contributors, the recommended reading order is:

1. README.md
2. ARCHITECTURE.md
3. REPOSITORY_INDEX.md
4. docs/architecture/README.md
5. docs/architecture/ARCHITECTURE.md
6. docs/architecture/PIPELINE.md
7. docs/architecture/Canonical Schema.md
8. docs/architecture/Storage Strategy.md
9. docs/architecture/Firestore Metadata.md
10. docs/architecture/Infrastructure.md
11. docs/implementation/IMPLEMENTATION_ROADMAP.md

---

# Repository Conventions

## Documentation

- Documentation reflects the current implementation.
- Architecture describes the approved system design.
- Significant design decisions are recorded as ADRs.

---

## Infrastructure

- Infrastructure is managed using Terraform.
- Infrastructure changes must be version controlled.
- Environment-specific configuration remains isolated from reusable modules.

---

## Repository Organization

- Root contains only repository-level documents.
- Technical documentation belongs under `docs/`.
- Infrastructure belongs under `infrastructure/`.
- Generated artifacts should not be committed unless explicitly required.

---

# Repository Maintenance

Update this document whenever:

- A directory is added, renamed, or removed.
- A major document is introduced.
- Infrastructure layout changes.
- Repository organization changes.

---

# Related Documents

| Document | Purpose |
|----------|---------|
| README.md | Repository overview |
| ARCHITECTURE.md | High-level architecture |
| docs/architecture/README.md | Architecture documentation index |
| docs/implementation/IMPLEMENTATION_ROADMAP.md | Implementation progress |

---

# Ownership

The Repository Index is the primary navigation document for the Knowledge Factory repository and should remain synchronized with the repository structure throughout the lifecycle of the project.