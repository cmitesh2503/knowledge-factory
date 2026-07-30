# Infrastructure Architecture

**Project:** Knowledge Factory  
**Document Version:** 1.0  
**Status:** Active  
**Type:** Infrastructure Architecture

---

# Purpose

This document defines the infrastructure architecture of the Knowledge Factory platform.

It describes the cloud resources, Terraform modules, deployment order, environment strategy, and operational architecture required to deploy the platform on Google Cloud Platform (GCP).

This document focuses on infrastructure only. Document processing, canonical schema, and storage design are documented separately.

---

# Infrastructure Principles

The infrastructure is designed with the following principles:

- Infrastructure as Code (Terraform)
- Modular Terraform design
- Environment isolation
- Least-privilege security
- Immutable infrastructure
- Provider-independent application architecture
- Repeatable deployments
- Production-ready design

---

# Target Cloud Platform

Google Cloud Platform (GCP)

Primary services:

- Cloud Storage
- Firestore
- Document AI
- Cloud Run
- Workflows
- IAM
- Service Accounts
- Secret Manager (future)
- Cloud Logging
- Cloud Monitoring

---

# High-Level Infrastructure

```text
                     Google Cloud Platform
                               │
                               │
        ┌──────────────────────┴──────────────────────┐
        │                                             │
        ▼                                             ▼
 Cloud Storage                               Firestore
(Raw / Processed / Archive)              Metadata Storage
        │                                             │
        └──────────────────────┬──────────────────────┘
                               │
                               ▼
                        Document AI
                               │
                               ▼
                        Cloud Run Service
                               │
                               ▼
                           Workflows
                               │
                               ▼
                     Downstream Applications
```

---

# Infrastructure Components

## Cloud Storage

Responsibilities:

- Raw document storage
- Canonical JSON storage
- Archive storage

---

## Firestore

Responsibilities:

- Metadata
- Processing status
- Document references
- Audit information

---

## Document AI

Responsibilities:

- Document parsing
- OCR
- Layout extraction
- Structured extraction

---

## Cloud Run

Responsibilities:

- Document processing services
- Provider adapters
- Canonical transformation
- Validation
- Publishing

---

## Workflows

Responsibilities:

- Orchestrate document processing
- Retry failed operations
- Coordinate processing stages
- Monitor execution

---

## IAM

Responsibilities:

- Identity management
- Access control
- Least privilege
- Service authentication

---

## Service Accounts

Responsibilities:

- Terraform deployment
- Cloud Run execution
- Workflow execution
- Document AI access
- Firestore access
- Cloud Storage access

---

# Terraform Structure

```text
terraform/

├── environments/
│   ├── dev/
│   ├── test/
│   └── prod/
│
└── modules/
    ├── storage/
    ├── storage_iam/
    ├── firestore/
    ├── document_ai/
    ├── cloudrun/
    ├── workflows/
    ├── project_iam/
    └── service_accounts/
```

---

# Environment Strategy

Each environment maintains its own configuration while sharing reusable modules.

Supported environments:

- Development
- Test
- Production

Reusable infrastructure remains inside the `modules` directory.

---

# Deployment Order

Infrastructure should be deployed in the following order:

1. Project Configuration
2. IAM
3. Service Accounts
4. Cloud Storage
5. Firestore
6. Document AI
7. Cloud Run
8. Workflows

Each stage depends only on previously deployed resources.

---

# Module Responsibilities

| Module | Responsibility |
|---------|----------------|
| project_iam | Project-level IAM configuration |
| service_accounts | Service account creation |
| storage | Cloud Storage buckets |
| storage_iam | Storage permissions |
| firestore | Firestore database |
| document_ai | Document AI resources |
| cloudrun | Cloud Run services |
| workflows | Workflow orchestration |

---

# Security Principles

- Least privilege IAM
- Dedicated service accounts
- Private infrastructure
- Encrypted storage
- Encrypted communication
- No embedded secrets
- Infrastructure managed through Terraform only

---

# Monitoring

Infrastructure should integrate with:

- Cloud Logging
- Cloud Monitoring
- Cloud Audit Logs

Future enhancements may include:

- Error reporting
- Performance dashboards
- Cost monitoring
- Alerting

---

# Current Implementation Status

| Component | Status |
|-----------|--------|
| Terraform Foundation | Complete |
| IAM | Complete |
| Service Accounts | Complete |
| Cloud Storage | Complete |
| Firestore | Complete |
| Document AI | Complete |
| Cloud Run | In Progress |
| Workflows | Planned |
| Monitoring | Planned |

---

# Current Implementation Blocker

The current implementation is paused during the Cloud Run deployment phase.

Future implementation should continue from:

1. Complete Cloud Run deployment.
2. Validate Cloud Run infrastructure.
3. Deploy Workflows.
4. Implement document processing services.
5. Perform end-to-end integration testing.

---

# Future Infrastructure

Planned enhancements include:

- Secret Manager integration
- CI/CD pipeline
- Artifact Registry
- VPC networking
- Load balancing
- Custom domains
- Monitoring dashboards
- Disaster recovery

---

# Related Documents

| Document | Purpose |
|----------|---------|
| ARCHITECTURE.md | High-level architecture |
| PIPELINE.md | Processing pipeline |
| Canonical Schema.md | Canonical document model |
| Storage Strategy.md | Cloud Storage architecture |
| Firestore Metadata.md | Firestore metadata architecture |
| IMPLEMENTATION_ROADMAP.md | Implementation progress and next steps |