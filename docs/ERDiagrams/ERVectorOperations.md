# ER Diagram - Vector & Cache Operations

## Purpose

Vector cleanup and data restoration infrastructure. Audits vector database cleanup operations and maintains restoration caches for recovering cleaned data when needed, supporting large-scale patent document vector operations.

## Vector & Cache Operations Domain

```mermaid
%%{init: {"securityLevel": "loose"}}%%
erDiagram
    %% Referenced table (from Document Management domain)
    DOCUMENTS_ref {
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
    
    %% Vector & Cache Operations Tables
    VECTOR_CLEANUP_AUDIT {
        uuid cleanup_audit_id PK
        uuid document_uuid FK
        varchar cleanup_strategy
        integer vectors_deleted
        jsonb sections_affected
        integer cleanup_time
        varchar cleanup_reason
        boolean restoration_ok
        jsonb audit_trail
        timestamp created_timestamp
        timestamp updated_timestamp
        uuid created_by FK
        uuid updated_by FK
    }
    
    VECTOR_RESTORATION_CACHE {
        uuid restoration_cache_id PK
        uuid document_uuid FK
        jsonb cached_vectors
        jsonb cached_sections
        timestamp cache_timestamp
        timestamp expiry_timestamp
        integer restoration_cnt
        timestamp created_timestamp
        timestamp updated_timestamp
        uuid created_by FK
        uuid updated_by FK
    }
    
    %% Domain Relationships
    DOCUMENTS_ref ||--o{ VECTOR_CLEANUP_AUDIT : audited_by
    DOCUMENTS_ref ||--o{ VECTOR_RESTORATION_CACHE : cached_by
```

## Referenced Tables Legend
- **DOCUMENTS_ref** → **DOCUMENTS** (Document Management domain) - Source documents for vector operations

## Cross-Domain Relationships

**To System Foundation domain:**
- `VECTOR_CLEANUP_AUDIT.created_by` → `USERS.user_id`
- `VECTOR_CLEANUP_AUDIT.updated_by` → `USERS.user_id`
- `VECTOR_RESTORATION_CACHE.created_by` → `USERS.user_id`
- `VECTOR_RESTORATION_CACHE.updated_by` → `USERS.user_id`

**To Document Management domain:**
- `VECTOR_CLEANUP_AUDIT.document_uuid` → `DOCUMENTS.document_uuid`
- `VECTOR_RESTORATION_CACHE.document_uuid` → `DOCUMENTS.document_uuid`

## Domain Tables (2 + 1 referenced)

1. **`VECTOR_CLEANUP_AUDIT`** - Vector lifecycle management and cleanup tracking
2. **`VECTOR_RESTORATION_CACHE`** - Cached vector data for restoration operations
3. **`DOCUMENTS`** (referenced) - Document entities from Document Management domain

## Key Features

- **Cleanup Auditing**: Complete tracking of vector deletion operations
- **Restoration Cache**: Performance optimization for vector recovery
- **Strategy Tracking**: Different cleanup approaches with success metrics
- **Time Management**: Cache expiry and restoration count tracking

## Operations Workflow

1. Documents undergo vector cleanup with strategy-based deletion
2. Cleanup operations are fully audited with affected sections tracked
3. Vector data is cached for potential restoration needs
4. Cache expiry ensures optimal storage utilization

---

**Last Updated**: January 7, 2026  
**Domain Tables**: 2 operations tables + 1 referenced  
**Status**: Vector lifecycle optimization

---
**VISUAL AUTHORITY** | **Implementation**: [database.py](../src/app/models/database.py) | **Requirements**: [DatabaseSchemaSpec.md](../design/DatabaseSchemaSpec.md)