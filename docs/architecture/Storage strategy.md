# Storage Strategy

**Project:** Knowledge Factory  
**Document Version:** 1.0  
**Status:** Active  
**Type:** Storage Architecture

---

# Purpose

This document defines the storage architecture for the Knowledge Factory platform.

It describes how documents move through the storage lifecycle, how storage resources are organized, and the storage standards used throughout the platform.

This document focuses on Cloud Storage only. Firestore is documented separately in **Firestore Metadata.md**.

---

# Objectives

The storage architecture is designed to:

- Store documents securely
- Separate processing stages
- Support versioning
- Enable recovery and auditing
- Minimize storage costs
- Support lifecycle management
- Remain independent of processing providers

---

# Storage Architecture

```text
                    Source Documents
                           │
                           ▼
                 Raw Storage Bucket
                           │
                           ▼
                 Document Processing
                           │
                           ▼
             Canonical JSON Generation
                           │
                           ▼
             Processed Storage Bucket
                           │
                           ▼
               Downstream Consumers
                           │
                           ▼
                 Archive Storage Bucket
```

---

# Storage Principles

- Store each artifact only once.
- Never overwrite original documents.
- Canonical JSON is the primary processed artifact.
- Separate raw, processed, and archived data.
- Infrastructure provisions storage; applications consume it.
- Storage must remain independent of processing providers.

---

# Storage Buckets

## Raw Bucket

### Purpose

Stores original uploaded documents before processing.

### Contents

- PDF files
- Images
- Other supported document formats

Example:

```text
raw/
    mathematics.pdf
    chapter1.pdf
```

---

## Processed Bucket

### Purpose

Stores processed canonical artifacts.

### Contents

- Canonical JSON
- Processing output
- Validation reports (future)

Example

```text
processed/
    mathematics.json
    chemistry.json
```

---

## Archive Bucket

### Purpose

Stores long-term archived artifacts.

### Contents

- Historical canonical documents
- Previous versions
- Archived processing outputs

---

# Folder Structure

Recommended structure:

```text
raw/
    incoming/

processed/
    canonical/

archive/
    historical/
```

The structure should remain simple and provider independent.

---

# Naming Convention

Object names should:

- Be lowercase
- Use hyphens
- Avoid spaces
- Avoid provider-specific names
- Be deterministic where possible

Example

```text
cbse-class10-maths.pdf

cbse-class10-maths.json
```

---

# Storage Classes

Recommended Google Cloud Storage classes:

| Bucket | Storage Class |
|---------|---------------|
| Raw | Standard |
| Processed | Standard |
| Archive | Coldline |

Storage class selection may change based on usage patterns.

---

# Versioning

Bucket versioning is recommended for:

- Processed artifacts
- Canonical JSON
- Archived documents

Original documents should never be modified after upload.

---

# Lifecycle Policies

Recommended lifecycle strategy:

Raw Bucket

- Retain until processing completes.
- Delete after successful publication if business requirements permit.

Processed Bucket

- Retain active canonical artifacts.

Archive Bucket

- Long-term retention.
- Lower-cost storage class.
- Restore only when required.

---

# Security

Storage should follow least-privilege principles.

Recommendations:

- Private buckets
- IAM-based access
- Encryption at rest
- Encryption in transit
- Uniform bucket-level access
- No public access

---

# Backup Strategy

Recommendations:

- Enable bucket versioning.
- Replicate critical artifacts if required.
- Protect canonical documents.
- Archive previous versions before deletion.

---

# Current Storage Layout

Current infrastructure provisions storage for:

- Raw documents
- Processed canonical documents
- Archived artifacts

Additional storage locations may be introduced as the platform evolves.

---

# Future Enhancements

Potential future improvements include:

- Multi-region storage
- Automatic archival
- Object lifecycle optimization
- Event-driven processing
- Metadata-based partitioning
- Object integrity verification

---

# Related Documents

| Document | Purpose |
|----------|---------|
| ARCHITECTURE.md | High-level architecture |
| PIPELINE.md | Processing pipeline |
| Canonical Schema.md | Canonical document model |
| Firestore Metadata.md | Firestore metadata design |
| Infrastructure.md | Infrastructure and Terraform |