# Database Schema Specification

**Status**: APPROVED - PostgreSQL Decision Confirmed (Dec 30, 2025)  
**Authority**: Implementation guidance for P3.1 Database Schema & Persistence Layer  
**State Machine Authority**: [PipelineStateMachine.md](../PipelineStateMachine.md) - AUTHORITATIVE state definitions for all pipeline state fields  
**Database Standards**: [Standards.md](../Standards.md) - MANDATORY persistence service usage, naming conventions, and session management  
**Cross-References**: [CorpusModel.md](../../CorpusModel.md), [ProvenanceAudit.md](../../ProvenanceAudit.md), [PipelineExecutionSpec.md](./PipelineExecutionSpec.md)

## Purpose

Defines complete relational database schema for patent intelligence system supporting document lifecycle, corpus isolation, agent execution, HITL workflows, and immutable audit trails.

## Required Content (Minimum Specification)

### Core Entities & Tables

#### Document Management
- **Document**: Primary document entity
  - [ ] Document metadata (id, title, source, ingestion_timestamp)
  - [ ] Document type classification (patent, prior_art, office_action, etc.)
  - [ ] Corpus assignment (single corpus per document)
  - [ ] Pipeline state tracking per [PipelineStateMachine.md](../PipelineStateMachine.md) AUTHORITATIVE definitions
  - [ ] Soft delete support (is_deleted, deleted_at, deletion_reason)

- **DocumentVersion**: Immutable document versions
  - [ ] Version tracking with parent relationships
  - [ ] Content snapshots for auditability
  - [ ] Transformation tracking
  - [ ] Archive version preservation with audit trails

- **Artifact**: Document-derived content
  - [ ] Text extractions, image references, diagram representations
  - [ ] Artifact type enumeration
  - [ ] Parent document relationships
  - [ ] Soft delete support (is_deleted, deleted_at, deletion_reason)
  - [ ] Pipeline state tracking per [PipelineStateMachine.md](../PipelineStateMachine.md)

- **DiagramCanonical**: Structured diagram representations
  - [ ] Canonical diagram format definition
  - [ ] Source artifact relationships
  - [ ] Versioning and approval workflows

#### Corpus & Access Control
- **Corpus**: Corpus definitions
  - [ ] Corpus types (Open Patent, Adversarial, Product, Guidance)
  - [ ] Access policies and boundaries
  - [ ] Isolation enforcement metadata

- **CorpusMembership**: Document-to-corpus assignments
  - [ ] Membership rules and timestamps
  - [ ] Violation audit trails
  - [ ] Membership validation logic

#### Agent & Task Management
- **AgentRun**: Agent execution tracking
  - [ ] Agent identity, parameters, corpus access
  - [ ] Input/output tracking with provenance
  - [ ] Success/failure status and retry logic

- **Task**: HITL task lifecycle
  - [ ] Task types, states, assignments
  - [ ] Evidence bundle references
  - [ ] Completion criteria and outcomes

#### Audit & Provenance
- **AuditEvent**: Immutable event log
  - [ ] Event types, timestamps, actor identity
  - [ ] Full context capture for legal compliance
  - [ ] Correlation with provenance records

- **Provenance/Lineage**: Data lineage tracking
  - [ ] Activity, entity, agent relationships
  - [ ] Transformation chains and dependencies
  - [ ] PROV-O compliance structures

### Actor Identity Model

**Requirements**: Simple identity with session-based reviewer selection (no authentication)

- [x] **Users Table Source**: Dropdown populated from existing users table for reviewer selection
- [x] **Session Persistence**: Selected reviewer persists across browser sessions
- [x] **Per-Entity Attribution**: All database operations use session-selected reviewer for audit fields  
- [x] **Actor Types**: Human reviewer (session-selected), system process, agent execution (distinct userids)
- [x] **Litigation-Grade Audit**: Complete reviewer attribution chain for legal defensibility
- [x] **Zero Authentication**: No login, passwords, roles, or authentication infrastructure
- [x] **Phase Compliance**: Maintains Phase 1 authentication removal constraints

### Schema Relationships

- [ ] Primary key definitions and constraints
- [ ] Foreign key relationships with cascade rules
- [ ] Junction tables for many-to-many relationships
- [ ] Unique constraints for business rules

### Indexing Strategy

- [ ] Performance-critical index definitions
- [ ] Corpus boundary enforcement indexes
- [ ] Audit trail query optimization
- [ ] Full-text search index requirements

### Data Constraints

#### **Standard Audit Fields (MANDATORY for All Tables)**
**Per [Standards.md](../Standards.md) naming conventions and audit requirements:**

- **`created_timestamp`**: TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
  - Datetime when record was created
  - Uses `_timestamp` suffix per Standards.md naming rules
  - UTC timezone with microsecond precision

- **`updated_timestamp`**: TIMESTAMP NULL
  - Datetime when record was last modified  
  - Updated automatically via database trigger
  - NULL for records that have never been modified

- **`created_by`**: VARCHAR(255) NOT NULL
  - User/system identifier who created the record
  - Values: user UUID, 'system_process', 'pipeline_automation', agent identifiers
  - Required for all record creation audit trails

- **`updated_by`**: VARCHAR(255) NULL
  - User/system identifier who last modified the record
  - Updated automatically with modification triggers
  - NULL for records that have never been modified

#### **Deletion Audit Fields (Where Soft Delete Required)**
**For tables supporting soft deletion (documents, artifacts, images, etc.):**

- **`marked_deleted`**: BOOLEAN DEFAULT FALSE
  - Soft delete flag for retention without physical removal
  - Enables recovery workflows and audit trail preservation

- **`deleted_timestamp`**: TIMESTAMP NULL
  - Datetime when record was marked for deletion
  - NULL for active records

- **`deleted_by`**: VARCHAR(255) NULL
  - User/system identifier who deleted the record
  - Required for deletion audit and accountability

- **`deletion_reason`**: VARCHAR(255) NULL
  - Categorized reason for deletion from predefined enum
  - Values: 'user_request', 'policy_violation', 'data_cleanup', etc.

#### **Document-Specific Upload Tracking**
**For document ingestion audit trails:**

- **`uploaded_by`**: ENUM('user', 'research_agent', 'system') NOT NULL
  - Source of document upload for processing accountability

- **`upload_source_info`**: JSONB NULL
  - Additional upload context and metadata
  - Structure varies by upload source type

#### **Processing-Specific Actor Identification**
**Standardized `created_by` values for automated processes:**
- `'ocr_pipeline_tesseract'`: Tesseract OCR processing
- `'vision_pipeline_pytorch'`: PyTorch vision analysis
- `'multimodal_llm_synthesis'`: LLM description generation
- `'vector_cleanup_system'`: Automated vector cleanup
- `'research_agent_[id]'`: Agent-initiated actions
- User UUID: Manual uploads and human actions

#### **Multimodal Processing Field Requirements**
**For enhanced image processing and vectorization support:**

**OCR Result Fields (image_ocr_results table):**
- **`language`**: VARCHAR(10) - OCR language configuration (e.g., 'eng', 'eng+fra')
- **`engine_version`**: VARCHAR(50) - Tesseract version for processing traceability  
- **`preprocessing_applied`**: JSONB - Array of preprocessing steps applied

**Multimodal Description Fields (images table):**
- **`context_correlation_score`**: FLOAT - Correlation between OCR and vision results (0.0-1.0)
- **`sources_used`**: JSONB - Array indicating processing sources ['ocr_tesseract', 'vision_pytorch', 'document_context']
- **`reference_numerals_correlated`**: JSONB - Array of patent figure reference numbers identified
- **`figure_type`**: VARCHAR(50) - Classification (system_architecture, flowchart, circuit_diagram, etc.)
- **`technical_complexity`**: VARCHAR(20) - Assessment level (low, medium, high)  
- **`llm_model_used`**: VARCHAR(100) - LLM model identifier for description generation

#### **Database Implementation Requirements**
- **Triggers**: Automatic `updated_timestamp` and `updated_by` updates
- **Constraints**: `created_timestamp` and `created_by` NOT NULL validation
- **Indexes**: Performance indexes on audit fields for compliance queries
- **Immutability**: Audit fields never modified after creation except via trigger

- [ ] Check constraints for business rules
- [ ] Corpus isolation enforcement constraints
- [ ] State transition validation constraints
- [ ] Immutability constraints for audit data

## Design Decisions (APPROVED)

1. **Database Technology**: **PostgreSQL** (single-node, local-first)
   - **Rationale**: Strong relational integrity for corpus isolation, provenance, and audit; supports advanced indexing (JSONB, vector extensions later); avoids SQLite concurrency limitations
   - **Constraints**: Single-node deployment, local development acceptable given hardware capacity

2. **Actor Identity Scope**: **Single reviewer model** (no authentication system)
   - **Rationale**: Single human reviewer for Phase 3; avoids reintroducing auth removed in Phase 1; reviewer identity tracked as simple actor metadata
   - **Constraints**: Reviewer selected from dropdown/fixed identifier; no login/passwords/roles; identity for audit/provenance only

3. **Provenance Granularity**: Event-level tracking with comprehensive audit trails
4. **Corpus Enforcement**: Database-level constraints with application validation

## Implementation Guidance

- Database migrations using Alembic (existing infrastructure)
- SQLAlchemy 2.0 model definitions (existing patterns)
- Connection pooling and session management patterns
- Database initialization and seeding procedures

## Acceptance Criteria

- [ ] All required entities defined with complete schemas
- [ ] Relationships clearly specified with constraints
- [ ] Corpus isolation enforceable at database level
- [ ] Audit trails complete and immutable
- [ ] Compatible with existing Phase 2 contracts
- [ ] Human reviewer approval obtained

---

**Status**: SPECIFICATION COMPLETE - Ready for P3.1 Implementation
**Approved**: PostgreSQL + Single Reviewer Model (Dec 30, 2025)