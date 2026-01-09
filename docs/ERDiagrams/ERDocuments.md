# ER Diagram - Document Management & Storage

## Purpose

Document ingestion pipeline with corpus-based access control. Tracks documents from upload through processing states, maintains immutable version history, extracts artifacts (text, images, diagrams), and enforces strict corpus isolation for patent intelligence workflows.

## Document Management & Storage Domain

```mermaid
%%{init: {"securityLevel": "loose"}}%%
erDiagram
    %% Core Document Management
    CORPORA {
        uuid corpus_id PK
        varchar name
        text description
        varchar corpus_type
        varchar isolation_level
        timestamp created_timestamp
        timestamp updated_timestamp
        uuid created_by FK
        uuid updated_by FK
    }
    
    DOCUMENTS {
        uuid document_uuid PK
        uuid corpus_id FK
        varchar title
        varchar source
        varchar document_type
        varchar current_state
        varchar document_hash
        jsonb document_structure
        jsonb bibliographic_data
        varchar deletion_strategy
        varchar vector_cleanup_status
        timestamp ingestion_timestamp
        integer error_count
        varchar uploaded_by
        jsonb upload_source_info
        timestamp created_timestamp
        timestamp updated_timestamp
        uuid created_by FK
        uuid updated_by FK
    }
    
    DOCUMENT_VERSIONS {
        uuid version_id PK
        uuid document_uuid FK
        integer version_number
        text content
        jsonb metadata
        varchar version_reason
        boolean marked_deleted
        timestamp deleted_timestamp
        varchar deletion_reason
        varchar deleted_by
        timestamp created_timestamp
        timestamp updated_timestamp
        uuid created_by FK
        uuid updated_by FK
    }
    
    CORPUS_MEMBERSHIPS {
        uuid membership_id PK
        uuid corpus_id FK
        uuid document_uuid FK
        timestamp assigned_at
        varchar assigned_by
        varchar membership_reason
        timestamp created_timestamp
        timestamp updated_timestamp
        uuid created_by FK
        uuid updated_by FK
    }
    
    ARTIFACTS {
        uuid artifact_id PK
        uuid document_uuid FK
        varchar artifact_type
        varchar name
        text content
        bytea binary_data
        jsonb metadata
        boolean marked_deleted
        timestamp deleted_timestamp
        varchar deletion_reason
        varchar deleted_by
        timestamp created_timestamp
        timestamp updated_timestamp
        uuid created_by FK
        uuid updated_by FK
    }
    
    IMAGES {
        uuid image_id PK
        uuid document_uuid FK
        varchar image_path
        varchar original_filename
        integer file_size_bytes
        varchar image_format
        varchar dimensions
        varchar perceptual_hash
        timestamp extracted_at
        varchar processing_state
        jsonb vision_analysis_result
        jsonb document_context
        text multimodal_description
        decimal generation_confidence
        decimal context_correlation_score
        jsonb sources_used
        jsonb ref_numerals_correlated
        varchar figure_type
        varchar technical_complexity
        varchar llm_model_used
        integer ocr_attempts
        integer vision_attempts
        boolean human_validated
        jsonb metadata
    }
    
    %% Domain Relationships
    CORPORA ||--o{ DOCUMENTS : contains
    CORPORA ||--o{ CORPUS_MEMBERSHIPS : has
    DOCUMENTS ||--o{ DOCUMENT_VERSIONS : versioned_as
    DOCUMENTS ||--o{ CORPUS_MEMBERSHIPS : member_of
    DOCUMENTS ||--o{ ARTIFACTS : contains
    DOCUMENTS ||--o{ IMAGES : contains
```

## Cross-Domain Relationships

All tables in this domain have audit field foreign keys to the System Foundation domain:
- `*.created_by` → `USERS.user_id` (System Foundation domain)
- `*.updated_by` → `USERS.user_id` (System Foundation domain)

## Domain Tables (6 total)

1. **`CORPORA`** - Corpus definitions and isolation policies
2. **`DOCUMENTS`** - Primary document entities with enhanced metadata
3. **`DOCUMENT_VERSIONS`** - Immutable version history with soft delete
4. **`CORPUS_MEMBERSHIPS`** - Document-to-corpus assignment tracking
5. **`ARTIFACTS`** - Document-derived content (text, images, diagrams)
6. **`IMAGES`** - Enhanced image metadata with multimodal analysis

## Key Features

- **Corpus Isolation**: Document-to-corpus assignment via memberships table
- **Version Control**: Immutable version history with soft delete capabilities
- **Content Management**: Structured storage for documents, artifacts, and images
- **Metadata Rich**: JSONB fields for flexible document structure and context

---

**Last Updated**: January 7, 2026  
**Domain Tables**: 6 tables  
**Status**: Core document management foundation

---
**VISUAL AUTHORITY** | **Implementation**: [database.py](../src/app/models/database.py) | **Requirements**: [DatabaseSchemaSpec.md](../design/DatabaseSchemaSpec.md), [CorpusRequirements.md](../proposals/CorpusDesign/CorpusRequirements.md)