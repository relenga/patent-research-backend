# Database Schema Specification

**Status**: APPROVED - PostgreSQL Decision Confirmed (Dec 30, 2025)  
**Authority**: Implementation guidance for P3.1 Database Schema & Persistence Layer  
**Database Standards**: [Standards.md](../Standards.md) - MANDATORY persistence service usage, naming conventions, and session management  
**Cross-References**: [CorpusModel.md](../../CorpusModel.md), [ProvenanceAudit.md](../../ProvenanceAudit.md), [PipelineStateMachine.md](../../PipelineStateMachine.md)

## Purpose

Defines complete relational database schema for patent intelligence system supporting document lifecycle, corpus isolation, agent execution, HITL workflows, and immutable audit trails.

## Required Content (Minimum Specification)

### Core Entities & Tables

#### Document Management
- **Document**: Primary document entity
  - [ ] Document metadata (id, title, source, ingestion_timestamp)
  - [ ] Document type classification (patent, prior_art, office_action, etc.)
  - [ ] Corpus assignment (single corpus per document)
  - [ ] Current state tracking (PipelineStateMachine states)
  - [ ] Soft delete support (is_deleted, deleted_at, deletion_reason) - P3.2B.2

- **DocumentVersion**: Immutable document versions
  - [ ] Version tracking with parent relationships
  - [ ] Content snapshots for auditability
  - [ ] Transformation tracking
  - [ ] REPROCESSING version preservation (archived versions) - P3.2B.2

- **Artifact**: Document-derived content
  - [ ] Text extractions, image references, diagram representations
  - [ ] Artifact type enumeration
  - [ ] Parent document relationships
  - [ ] Soft delete support (is_deleted, deleted_at, deletion_reason) - P3.2B.2
  - [ ] Individual REPROCESSING state tracking - P3.2B.2

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

**Requirements**: Single reviewer model without authentication system

- [x] **Reviewer Entity**: Simple reviewer identifier (dropdown selection)
- [x] **Actor Types**: Human reviewer, system process, agent execution
- [x] **Session Tracking**: Basic context preservation for HITL task continuity
- [x] **Audit Identity**: Reviewer name stored for provenance and audit trails only
- [x] **No Authentication**: No login, passwords, roles, or user management
- [x] **Phase Compliance**: Maintains Phase 1 auth removal constraints

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