# Repository Index

**Repository:** knowledge-factory

**Version:** 1.0

**Status:** Under Audit

**Last Updated:** YYYY-MM-DD

---

# Purpose

The Repository Index is the master navigation document for the Knowledge Factory repository.

It provides a complete overview of the repository structure, explains the responsibility of every major directory, and identifies where each part of the platform is implemented.

This document reflects the **actual implementation** of the repository. It is not an architecture proposal or future design document.

---

# Repository Overview

Knowledge Factory is a cloud-native document processing platform that transforms unstructured documents into a technology-independent canonical knowledge representation.

The repository contains:

- Documentation
- Infrastructure
- Processing services
- Workflow orchestration
- Sample data
- Automated tests

---

# Top Level Repository Structure

| Path | Description | Status |
|------|-------------|--------|
| docs/ | Project documentation, architecture, ADRs and diagrams | Pending Audit |
| docker/ | Docker build resources | Pending Audit |
| infrastructure/ | Infrastructure as Code, Terraform modules and deployment scripts | Pending Audit |
| samples/ | Sample input and output documents | Pending Audit |
| services/ | Processing services implementing Knowledge Factory pipeline stages | Pending Audit |
| tests/ | Unit and integration tests | Pending Audit |
| workflows/ | Workflow definitions and orchestration | Pending Audit |
| README.md | Repository overview | Pending Audit |
| ARCHITECTURE.md | System architecture | Pending Audit |

---

# Documentation

```
docs/
├── adr/
├── architecture/
└── diagrams/
```

### Purpose

Contains all project documentation including:

- Architecture
- ADRs
- Design documents
- Diagrams

---

# Infrastructure

```
infrastructure/
├── scripts/
└── terraform/
```

Terraform contains:

```
terraform/
├── environments/
│   ├── dev/
│   ├── test/
│   └── prod/
└── modules/
    ├── cloudrun/
    ├── document_ai/
    ├── firestore/
    ├── project_iam/
    ├── service_accounts/
    ├── storage/
    ├── storage_iam/
    └── workflows/
```

### Responsibility

Infrastructure provisioning for:

- Google Cloud
- Storage
- Firestore
- Document AI
- IAM
- Cloud Run
- Workflows

---

# Services

```
services/
├── adapter/
├── normalizer/
├── outline/
├── publisher/
└── shared/
```

### Responsibility

Implements the document processing pipeline.

Current service responsibilities:

| Service | Responsibility |
|----------|----------------|
| adapter | Converts external provider output into internal processing format |
| normalizer | Produces canonical document representation |
| outline | Generates document outline and structure |
| publisher | Publishes processed documents |
| shared | Common utilities and shared components |

---

# Workflows

```
workflows/
```

### Responsibility

Workflow definitions and orchestration logic for the Knowledge Factory processing pipeline.

---

# Samples

```
samples/
```

### Responsibility

Reference documents used for development, testing and validation.

---

# Tests

```
tests/
```

### Responsibility

Repository test suite including unit, integration and validation tests.

---

# Repository Audit Order

The repository will be audited in the following order:

1. Repository Foundation
2. Documentation
3. Infrastructure
4. Services
5. Workflows
6. Samples
7. Tests
8. Final Review

---

# Repository Standards

The repository follows the following principles:

- Documentation reflects implementation.
- Architecture documents approved design.
- Every change is traceable.
- Infrastructure is managed as code.
- Processing stages remain modular.
- Canonical data model remains technology independent.

---

# Related Documents

- README.md
- ARCHITECTURE.md
- docs/architecture/
- docs/audit/AUDIT_PROCESS.md
- docs/audit/AUDIT_FINDINGS.md
- docs/audit/AUDIT_DECISIONS.md
- docs/audit/AUDIT_STATUS.md

---

# Maintenance

This document must be updated whenever:

- A top-level directory is added, removed or renamed.
- A major processing service is introduced.
- Infrastructure layout changes.
- Documentation structure changes.
- Repository organization changes.

This document is the authoritative navigation reference for the Knowledge Factory repository.