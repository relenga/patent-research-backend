# Corpus Enforcement Specification

**Status**: APPROVED - Corpus Business Rules and Technical Implementation (Dec 30, 2025)  
**Authority**: Technical implementation of CorpusModel.md business rules for P3.5 Corpus Classification and Storage  
**Business Rules Authority**: [CorpusModel.md](../../CorpusModel.md) - AUTHORITATIVE corpus definitions and access matrix
**Agent Rules**: [AgentResponsibilities.md](../../AgentResponsibilities.md) - Agent-specific corpus access permissions
**Database Schema**: [DatabaseSchemaSpec.md](./DatabaseSchemaSpec.md) - Database implementation of corpus isolation

## Authority Relationship

**CorpusModel.md defines WHAT** (business rules, access matrix, corpus purposes)
**This specification defines HOW** (technical enforcement, violation detection, audit events)
**AgentResponsibilities.md defines WHO** (which agents can access which corpora)

## Purpose

Defines how corpus boundaries are enforced across storage, retrieval, indexing, and agent input construction to prevent cross-contamination between Open Patent, Adversarial, Product, and Guidance corpora.

## Required Content (Minimum Specification)

## Business Rules Implementation

### Corpus Access Matrix Enforcement

Per [CorpusModel.md](../../CorpusModel.md) authoritative access matrix:

**FORBIDDEN Operations** (Must be blocked):
- [x] Adversarial corpus → Claim drafting attempts
- [x] Product corpus → Claim drafting attempts  
- [x] Guidance corpus → Claim drafting attempts
- [x] Any corpus → Unauthorized agent access per AgentResponsibilities.md

**AUTHORIZED Operations** (Must be permitted):
- [x] Open Patent corpus → All operations (claim drafting, risk analysis, evidence mapping)
- [x] Adversarial corpus → Risk analysis and vulnerability identification only
- [x] Product corpus → Evidence mapping and read-on verification only
- [x] Guidance corpus → Style and structure guidance only

### Storage-Level Enforcement

#### Database Constraints
- [ ] Foreign key constraints preventing invalid corpus assignments
- [ ] Check constraints validating corpus-document relationships
- [ ] Trigger-based validation for corpus membership changes
- [ ] Immutable audit trail for corpus violations

#### File System Isolation
- [ ] Directory structure enforcing corpus separation
- [ ] File naming conventions with corpus prefixes
- [ ] Storage-level access controls per corpus
- [ ] Backup and restore corpus integrity validation

### Retrieval/Indexing Enforcement

#### Query-Level Filtering
- [ ] Mandatory corpus filters on all document queries
- [ ] Index partitioning by corpus for performance
- [ ] Search result isolation per corpus boundary
- [ ] Vector embedding space separation per corpus

#### RAG Infrastructure Boundaries
- [ ] Corpus-specific embedding models and indexes
- [ ] Retrieval pipeline corpus validation
- [ ] Cross-corpus contamination detection
- [ ] Embedding space isolation verification

### Agent Input Construction

#### Prompt Assembly Controls
- [ ] Agent-to-corpus permission matrix enforcement
- [ ] Input validation preventing unauthorized corpus access
- [ ] Context window corpus boundary validation
- [ ] Multi-document input corpus consistency checks

#### Runtime Boundary Validation
- [ ] Agent execution corpus scope verification
- [ ] Input sanitization and corpus tagging
- [ ] Output validation for corpus compliance
- [ ] Real-time boundary violation detection

### Violation Handling & Audit Events

#### Violation Detection
- [ ] Automated corpus boundary violation detection
- [ ] Cross-corpus reference attempt logging
- [ ] Agent boundary exceeding detection
- [ ] Invalid corpus assignment detection

#### Response Procedures
- [ ] Immediate execution halt on violations
- [ ] Violation escalation procedures
- [ ] Recovery and remediation protocols
- [ ] Human notification and review triggers

#### Audit Event Types
- [ ] `CORPUS_VIOLATION_ATTEMPTED`: Boundary breach attempts
- [ ] `CORPUS_ACCESS_GRANTED`: Successful corpus access
- [ ] `CORPUS_MEMBERSHIP_CHANGED`: Document corpus reassignments
- [ ] `AGENT_BOUNDARY_EXCEEDED`: Agent unauthorized access attempts

## Design Decisions Required

1. **Enforcement Level**: Database constraints vs application-level validation
2. **Performance vs Security**: Query filtering overhead vs isolation guarantees
3. **Violation Severity**: Warning vs immediate termination
4. **Recovery Strategy**: Automatic vs manual remediation procedures

## Implementation Guidance

### Database Integration
- SQLAlchemy relationship definitions with corpus filtering
- Alembic migrations for constraint enforcement
- Query interceptors for mandatory corpus filtering
- Performance monitoring for corpus-filtered queries

### Application Integration
- FastAPI middleware for corpus boundary validation
- Pydantic schema validation with corpus constraints
- Agent framework integration for runtime checks
- Logging integration for violation audit trails

## Acceptance Criteria

- [ ] Storage-level corpus isolation verified
- [ ] Retrieval operations corpus-aware
- [ ] Agent input construction corpus-validated
- [ ] Violation detection comprehensive
- [ ] Audit trails complete for all violations
- [ ] Performance impact documented and acceptable
- [ ] Human reviewer approval obtained

---

**Status**: SPECIFICATION COMPLETE - Ready for P3.5 Implementation
**Approved**: Corpus Business Rules Enforcement (Dec 30, 2025)
**Compliance**: Implements CorpusModel.md access matrix and AgentResponsibilities.md permissions