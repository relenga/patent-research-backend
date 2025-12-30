# BuildPlan.md  
## Phase-Based Execution Plan

---

## Purpose

This document defines the **execution plan** for the project.  
It translates **PRD requirements** into **ordered, phase-scoped tasks**.

**EXECUTION AUTHORITY:** This BuildPlan is the sole authority for what tasks exist, their scope, and execution sequence. WBS.md provides implementation details only. Design documents provide context and constraints, not execution authority.

Key principles:
- PRD defines *what must be true*
- BuildPlan defines *how and in what order we execute*
- Task numbering is **phase-scoped** and **stable**
- No task may violate phase boundaries defined in AgentRules.md

**Design Evolution:** Design documents may evolve during planning alignment. Phase 3 execution does not begin until explicit human review and authorization.

---

## Task Numbering Convention

All execution tasks follow this format:

P<Phase>.<TaskNumber>


Examples:
- P1.1 = Phase 1, Task 1
- P2.3 = Phase 2, Task 3

Task numbers are **unique within a phase**, not global.

---

## Phase Overview

### Phase 0 — Bootstrap (COMPLETE)
Goal: Verify environment and toolchain

Status: ✅ Complete  
Tag: `phase-0-complete`

---

### Phase 1 — Prune (COMPLETE)
Goal: Remove unused features, disable external infrastructure, and establish governance

This phase focuses on **simplification and control**, not capability.

**Status:** ✅ Complete
**Tag:** `phase-1-prune-complete`

---

### Phase 2 — Harden (COMPLETE)
Goal: Introduce structure, contracts, and enforcement

**Status:** ✅ Complete
**Tag:** `phase-2-harden-complete`

---

### Phase 3 — Build (READY)
Goal: Implement document processing, agent execution, and HITL workflows

**Status:** 🔄 Ready to begin
**Prerequisites:** Phase 2 contracts operational, phase-2-harden-complete tag exists
**Foundation-First Rule:** Data persistence → Pipeline execution → Agent wiring → HITL interfaces

---

## Phase 3 Design Gate — CLOSED (Dec 30, 2025)

**GATE STATUS**: CLOSED - All technical specifications completed and approved

**Human Approval Date**: December 30, 2025
**Approved Decisions**: PostgreSQL, PyTorch+Transformers, FastAPI+HTMX UI, Single Reviewer Model, OCR+Human Diagram Processing

**Authority Model**: BuildPlan.md remains execution authority defining what tasks exist and their scope. Technical specifications provide implementation guidance for P3 tasks, with detailed "how" enabling the "what" defined here.

### Completed Specification Documents

All specifications are: **written, internally consistent, cross-referenced, and approved**

**Location**: `docs/design/phase-3-specs/`

1. **DatabaseSchemaSpec.md**: Complete schema design ✅
2. **CorpusEnforcementSpec.md**: Boundary enforcement mechanisms ✅
3. **AgentFrameworkSpec.md**: LLM integration and execution patterns ✅
4. **HITLTaskSpec.md**: Human-in-the-loop workflow architecture ✅
5. **PipelineExecutionSpec.md**: State machine execution details ✅
6. **APISchemaSpec.md**: Domain-specific API contracts ✅
7. **FailureModesSpec.md**: Error handling and recovery patterns ✅

### Design Gate Completion Confirmed

- [x] All 7 specifications written and internally consistent
- [x] Cross-references resolved between specifications
- [x] Alignment verified with existing design documents
- [x] Human review completed with documented decisions
- [x] Implementation guidance ready for P3.1-P3.12 execution

**Phase 3 Implementation Status**: READY FOR P3.1 EXECUTION UPON HUMAN AUTHORIZATION

---

## Phase 3 — Build (Implementation Tasks)

### P3.1 Database Schema & Persistence Layer
**Maps to PRD:** Phase 3 data foundation requirements

**Objective:** Implement persistent storage for documents, states, lineage, and audit records using Phase 2 data model contracts.

**Scope:**
- Relational database schema for documents, states, lineage, and audit records
- Database connection and session management infrastructure
- Document lifecycle operations with state tracking
- Immutable audit event logging and lineage persistence
- Database migration framework

**Explicitly Not In Scope:**
- Database optimization or indexing strategies
- Multi-tenancy or access control beyond corpus isolation
- Backup/recovery procedures
- Connection pooling or performance tuning

**Acceptance Criteria:**
- Document records can be created, read, updated with state transitions
- Lineage DAG persists without cycles, supports traversal queries
- All state changes generate immutable audit events
- Database starts from empty state using migrations
- No direct database access outside this layer

**Status:** Not started

---

### P3.2 Pipeline State Machine Execution
**Maps to PRD:** Phase 3 pipeline orchestration requirements  
**State Machine Authority**: [PipelineStateMachine.md](PipelineStateMachine.md) - Authoritative state definitions and business logic  
**Implementation Guide**: [design/phase-3-specs/PipelineExecutionSpec.md](design/phase-3-specs/PipelineExecutionSpec.md) - Technical execution mechanics  
**HITL Integration**: [design/phase-3-specs/HITLTaskSpec.md](design/phase-3-specs/HITLTaskSpec.md) - Human task system integration

**Objective:** Implement document state machine execution engine using Phase 2 pipeline contracts.

**Scope:**
- State transition execution engine implementing PipelineStateMachine.md rules exactly
- Pipeline step runner framework with PipelineExecutionSpec.md mechanics
- Failure detection, retry logic, and HITL escalation per state definitions
- Progress tracking and state change event publishing with audit trail
- Manual state override capabilities for administration (emergency controls)
- State validation against PipelineStateMachine.md before all transitions

**Explicitly Not In Scope:**
- Specific pipeline step implementations (covered in later tasks)
- Performance optimization or parallel processing
- Complex scheduling or priority queues
- Pipeline analytics or metrics beyond basic progress
- Custom states not defined in PipelineStateMachine.md

**Acceptance Criteria:**
- Documents transition between PipelineStateMachine.md states automatically
- Failed transitions generate error states and HITL tasks per specifications
- Pipeline can be paused, resumed, and manually advanced per admin controls
- State changes visible through logging and events with full audit trail
- No pipeline step bypasses PipelineStateMachine.md state validation
- All state transitions comply with PipelineStateMachine.md authority

**Status:** Not started

---

### P3.3 Document Ingestion Implementation  
**Maps to PRD:** Phase 3 document processing requirements

**Objective:** Implement document acquisition, normalization, and text extraction using Phase 2 ingestion contracts.

**Scope:**
- File upload handler for multiple document formats
- Document normalization with text extraction and preservation
- Metadata extraction and source tagging system
- Document validation, format checking, and error recovery

**Explicitly Not In Scope:**
- Research agent automation (external API integration)
- Complex document parsing (claims parsing, legal section detection)
- Document comparison or similarity detection
- Batch processing or bulk upload features

**Acceptance Criteria:**
- Documents upload through web interface successfully
- Text extracted from PDF and XML formats reliably
- Document metadata populated automatically where possible
- Failed uploads generate clear error messages
- Original documents preserved alongside normalized text

**Status:** Not started

---

### P3.4 OCR and Image Processing Pipeline
**Maps to PRD:** Phase 3 image intelligence requirements

**Objective:** Implement OCR processing and image handling using Phase 2 image processing contracts.

**Scope:**
- Image extraction from PDF documents
- OCR text recognition for scanned content
- Image fingerprinting and duplicate detection
- OCR confidence scoring and quality validation
- Image metadata tracking and correction workflows

**Explicitly Not In Scope:**
- Advanced computer vision or diagram interpretation
- Machine learning model training or fine-tuning
- Image enhancement or preprocessing beyond basic OCR
- Automated diagram description generation

**Acceptance Criteria:**
- Images extracted from uploaded documents automatically
- OCR produces readable text from scanned pages
- Duplicate images detected and flagged for review
- OCR confidence scores available for human review
- Poor quality OCR flagged for manual correction

**Status:** Not started

---

### P3.5 Corpus Classification and Storage
**Maps to PRD:** Phase 3 corpus management requirements

**Objective:** Implement document classification and corpus isolation using Phase 2 corpus contracts.

**Scope:**
- Document type classification and corpus assignment logic
- Corpus isolation enforcement and access controls
- Corpus integrity validation and health monitoring
- Document reclassification workflows with audit trails

**Explicitly Not In Scope:**
- Automated document classification using ML
- Content-based similarity or clustering
- Cross-corpus analytical queries
- Corpus statistics or analytics dashboards

**Acceptance Criteria:**
- Documents correctly assigned to appropriate corpus
- Corpus boundaries strictly enforced in all retrieval operations
- Document type classification available through UI
- Reclassification generates audit events
- No document appears in multiple corpora simultaneously

**Status:** Not started

---

### P3.6 Text Chunking and RAG Infrastructure
**Maps to PRD:** Phase 3 retrieval system requirements

**Objective:** Implement text chunking, embedding, and retrieval infrastructure using Phase 2 retrieval contracts.

**Scope:**
- Text chunking strategy and implementation
- Embedding generation and vector database integration
- Corpus-aware retrieval with ranking and relevance scoring
- Retrieval performance optimization and caching

**Explicitly Not In Scope:**
- Custom embedding model training
- Multi-modal embedding (text + image)
- Advanced retrieval techniques (re-ranking, query expansion)
- Retrieval analytics or user behavior tracking

**Acceptance Criteria:**
- Text documents chunked into searchable segments
- Embeddings generated and stored for all text chunks
- Retrieval returns relevant passages from specified corpus only
- Search results include provenance links to source documents
- Retrieval performance adequate for interactive use

**Status:** Not started

---

### P3.7 Agent Execution Framework
**Maps to PRD:** Phase 3 agent orchestration requirements

**Objective:** Implement agent execution infrastructure using Phase 2 agent contracts and AgentResponsibilities boundaries.

**Scope:**
- Build agent execution runtime (prompt construction, LLM calls, response parsing)
- Implement agent boundary enforcement (corpus access restrictions)
- Add agent prompt templating and parameter injection
- Create agent execution logging and audit trails
- Build agent result validation and schema enforcement
- Add agent failure handling and retry mechanisms

**Explicitly Not In Scope:**
- Specific agent implementations (covered in next task)
- Agent performance optimization or caching
- Multi-agent coordination or conversation
- Agent learning or adaptation mechanisms

**Acceptance Criteria:**
- Agents execute within defined corpus and authority boundaries
- Agent prompts constructed from approved templates only
- Agent responses validated against expected schemas
- All agent executions logged with full provenance
- Agent failures handled gracefully without system impact

**Status:** Not started

---

### P3.8 Core Agent Implementations
**Maps to PRD:** Phase 3 agent capability requirements

**Objective:** Implement specific agents per AgentResponsibilities definitions within execution framework.

**Scope:**
- Build Classification Agent (assign doc_type and corpus)
- Implement Prior Art Analysis Agent (identify conflicts, risk only)
- Add Office Action Analysis Agent (extract examiner reasoning)
- Create Product Mapping Agent (map features to disclosures)
- Build Claim Drafting Agent (generate claims from Open Patent Corpus only)
- Add Support Verification Agent (validate claim support in open patent)

**Explicitly Not In Scope:**
- Agent UI-editable prompts (deferred to HITL interfaces)
- Complex multi-step agent workflows
- Agent-to-agent communication or coordination
- Agent result optimization or refinement

**Acceptance Criteria:**
- Each agent executes within assigned corpus boundaries only
- Prior Art Analysis Agent never provides claim language
- Claim Drafting Agent grounds all claims in Open Patent Corpus
- Support Verification Agent catches unsupported claim elements
- All agents produce structured, auditable outputs

**Status:** Not started

---

### P3.9 HITL Task Generation and Workflow
**Maps to PRD:** Phase 3 human-in-the-loop requirements
**Implementation Authority:** [HITLTaskSpec.md](design/phase-3-specs/HITLTaskSpec.md)

**Objective:** Implement human-in-the-loop task workflows per HITLTaskSpec.md consolidated specification.

**Scope:** See HITLTaskSpec.md for complete implementation requirements:
- Task lifecycle management (pending, assigned, in_progress, completed, rejected)
- Single reviewer UI interface with FastAPI+HTMX architecture
- Evidence bundle assembly and presentation
- Task completion workflows with audit trails
- Pipeline integration for state transitions

**Authority Note:** HITLTaskSpec.md is the single consolidated authority for all task management implementation details. This BuildPlan section provides execution context only.

**Explicitly Not In Scope:**
- Multi-user assignment models (deferred to Phase 4)
- Complex approval chains or workflow routing
- Task performance analytics or optimization
- Automated task assignment algorithms

**Acceptance Criteria:** Per HITLTaskSpec.md acceptance criteria - all task management functionality operational with single reviewer model

**Status:** Not started

---

### P3.10 System Logging and Event Infrastructure
**Maps to PRD:** Phase 3 observability requirements

**Objective:** Implement comprehensive logging, events, and error reporting using Phase 2 logging contracts.

**Scope:**
- Build structured logging infrastructure (JSON logs, correlation IDs)
- Implement event publishing for all major system actions
- Add error logging and exception tracking
- Create log aggregation and search capabilities
- Build system health monitoring and alerting
- Add user-facing activity logs and audit reports

**Explicitly Not In Scope:**
- Performance metrics or application monitoring
- Log analysis or business intelligence
- External monitoring system integration
- Log retention policies or archival

**Acceptance Criteria:**
- All system actions logged with structured data
- Errors captured with full context and stack traces
- Events published for pipeline progress, agent execution, task completion
- Logs searchable by correlation ID, user, document, or time range
- System health visible through logs and basic metrics

**Status:** Not started

---

### P3.11 Minimal UI for HITL and System Visibility
**Maps to PRD:** Phase 3 user interface requirements

**Objective:** Implement basic web interface for human review tasks and system visibility.

**Scope:**
- Build document upload and viewing interface
- Implement task review interface (display context, capture decisions)
- Add document and pipeline status visibility
- Create basic search and navigation
- Build audit log viewer for transparency
- Add system status and error reporting dashboard

**Explicitly Not In Scope:**
- Advanced UI/UX design or user experience optimization
- Mobile interface or responsive design
- User authentication or access control
- UI performance optimization or client-side caching

**Acceptance Criteria:**
- Users can upload documents and view processing status
- Human review tasks presented with full context for decision-making
- Document processing progress visible to users
- Audit trails accessible for review and verification
- System errors visible to administrators with actionable information

**Status:** Not started

---

### P3.12 Phase 3 Integration and Verification
**Maps to PRD:** Phase 3 completion requirements

**Objective:** Verify end-to-end system functionality and phase discipline compliance.

**Scope:**
- Run complete document processing workflow (upload → OCR → corpus assignment → agent analysis → HITL review)
- Verify corpus isolation maintained throughout all operations
- Test agent boundary enforcement and authority restrictions
- Validate provenance tracking from source documents to final outputs
- Check audit trail completeness and immutability
- Verify no Phase 4 features leaked into implementation

**Explicitly Not In Scope:**
- Performance testing or load testing
- Security testing or penetration testing
- User acceptance testing or usability evaluation
- Production readiness or deployment validation

**Acceptance Criteria:**
- Complete document-to-claim workflow executable end-to-end
- All corpus constraints automatically enforced
- Agent boundaries respected and violations prevented
- Complete audit trail from source document to human decisions
- No unauthorized features or capabilities present

**Tag:** `phase-3-build-complete`

**Status:** Not started

---

## Phase 1 — Prune (Completed Tasks)

### P1.1 Disable Redis / ARQ Startup  
**Maps to PRD:** §2.2 Disable External Infrastructure

- Disable Redis pool creation during startup
- Disable ARQ queue initialization
- Remove Redis cleanup in lifespan teardown
- Ensure app starts without external services

**Status:** ✅ Complete  
**Commit:** Phase 1.1

---

### P1.2 Remove Admin Interface  
**Maps to PRD:** §2.1 Remove Unused Template Features

- Remove admin interface imports
- Remove admin initialization and mounting
- Delete admin modules and configuration
- Verify no admin references remain

**Status:** ✅ Complete  
**Commit:** Phase 1.2

---

### P1.3 Remove Authentication / JWT  
**Maps to PRD:** §2.1 Remove Unused Template Features

- Remove JWT login endpoints
- Remove auth middleware and dependencies
- Remove auth-related configuration (JWT_*, ADMIN_*)
- Remove auth utilities if unused

**Status:** ✅ Complete  
**Commit:** Phase 1.3

---

### P1.4 Remove Rate Limiting & Caching  
**Maps to PRD:** §2.1 Remove Unused Template Features

- Remove rate limiting dependencies
- Remove Redis-based cache logic
- Remove related configuration
- Ensure no Redis references remain

**Status:** ✅ Complete  
**Commit:** Phase 1.4

---

### P1.5 Remove Background Task Endpoints  
**Maps to PRD:** §2.1 Remove Unused Template Features

- Remove ARQ task endpoints
- Remove background task registration
- Remove worker-related code paths

**Status:** ✅ Complete  
**Commit:** Phase 1.5

---

### P1.6 Simplify Configuration Surface  
**Maps to PRD:** §2.3 Simplify Configuration

- Remove unused settings classes
- Remove unused environment variables
- Ensure application starts with no `.env`
- Ensure defaults are safe and minimal

**Status:** ✅ Complete  
**Commit:** Phase 1.6

---

### P1.7 Finalize Governance Documentation  
**Maps to PRD:** §2.4 Add AI Governance

- Ensure all required governance documents exist and are complete
- Verify AgentRules.md consolidates phase discipline and execution rules
- Verify PRD.md scope matches Phase 1 outcomes
- Update BuildPlan.md to reflect completed P1.x task status
- Ensure consistent phase numbering across all documents

**Status:** ✅ Complete  
**Commit:** Phase 1.7

---

### P1.8 Prepare Target Folder Structure  
**Maps to PRD:** §2.5 Prepare Structure

Create empty directories only (no logic):

- `common/`
- `pipelines/`
- `llm/`
- `state/`

Use `.gitkeep` files as needed.

**Status:** ✅ Complete

---

### P1.9 Phase 1 Verification & Tag  
**Maps to PRD:** §5 Acceptance Criteria

- Verify application starts with single command
- Verify no external services required
- Verify no Redis / ARQ / auth / admin references
- Verify governance docs exist

**Tag:** `phase-1-prune-complete`

**Status:** ✅ Complete  
**Commit:** Phase 1.9

---

## Phase 2 — Harden (Structure & Contracts)

**Citing PRD Phase 2 Intent:** Introduce structure, contracts, and enforcement WITHOUT implementation.

**Phase 2 Rules:**
- Create interfaces and contracts ONLY
- NO business logic implementation
- NO external service integration  
- NO user-facing features
- Structure preparation for Phase 3

### Phase 2 — Pre-Execution Clarifications & Known Issues

**ACKNOWLEDGED ITEMS** (Documentation only, not tasks):

• **API Routing Policy Finalization** - Trailing slash policy must be chosen and documented in Phase 2, no enforcement until Phase 3, current Phase 1 behavior accepted as-is

• **Testing Strategy Clarification** - No automated testing introduced in Phase 2, testing strategy deferred (Phase 3 or later), Phase 2 validation is structural not behavioral

• **Persistence & Database Scope Boundary** - Phase 2 allows data models and interfaces only, no schema migrations, no storage engines, persistence decisions deferred

• **Observability vs Logging Distinction** - Phase 2 defines logging interfaces only, metrics/tracing/alerting are out of scope, observability planning deferred

• **Production & Deployment Concerns** - Docker, CI/CD, deployment are explicitly out of scope, no production hardening in Phase 2, these belong to future phase (unnumbered)

• **Enforcement Timing Reminder** - Phase 2 documents invariants, Phase 3 enforces them, no enforcement logic allowed in Phase 2

---

### P2.1 Establish Common Services Skeleton
**Maps to PRD:** Phase 2 structural preparation

- Create `common/` module structure with empty classes
- Define API routing invariants (slash, prefix, versioning)
- Define canonical API response & error envelopes (schema only)
- Define service interface contracts (no implementations):
  - **Request/Execution Context Service**: request_id, trace/correlation metadata, lifecycle-safe propagation
  - **Time/Clock Service**: Centralized UTC time source, mockable interface, no direct datetime.now() usage outside this service
  - **ID Generation Service**: Canonical UUID/ULID generation, single interface for ID creation, no ad-hoc uuid usage in Phase 3
  - **Logging Interface**: Structured logging contract, correlation via request_id
- Add type hints and docstrings for intended behavior
- Create `__init__.py` files with explicit exports
- **FORBIDDEN:** Any business logic or external calls

**Note:** All services are interfaces/abstract contracts only - no implementations, no runtime wiring, no external dependencies

**Status:** ✅ Complete  
**Commit:** Phase 2.1

**Status:** ✅ Complete

---

## Phase 2 Invariants (Documentation Only)

The following rules are documented during Phase 2 but not enforced until Phase 3:

**A) Async/Sync Execution Boundary Rule**
- Async IO allowed in API and orchestration layers
- CPU-bound work must be sync and isolated
- Rule is documented only in Phase 2

**B) API Routing Shape Invariant**
- Single trailing-slash policy (choose one, document only)
- Versioned prefix invariant (/api/v1)
- No implicit index routes

**C) API Response & Error Envelope Invariant**
- Canonical success response schema
- Canonical error response schema
- Schema definition only (no enforcement yet)

---

### P2.2 Define Explicit Document State Machine
**Maps to PRD:** Phase 2 lifecycle enforcement

- Create `state/` module with document state enums
- Define state transition rules as pure data structures
- Add validation contracts (interfaces only)
- Document state machine behavior in comments
- **FORBIDDEN:** State machine execution logic

**Status:** ✅ Complete  
**Commit:** Phase 2.2

---

### P2.3 Introduce Deterministic Pipeline Step Contracts
**Maps to PRD:** Phase 2 pipeline preparation

- Create `pipelines/` module with step interface definitions
- Define input/output contracts for each pipeline stage
- Add pipeline composition contracts (no orchestration)
- Create step validation interface definitions
- **FORBIDDEN:** Pipeline execution or step implementations

**Status:** ✅ Complete  
**Commit:** Phase 2.3

---

### P2.4 Add Phase-Locked Feature Flags
**Maps to PRD:** Phase 2 enforcement mechanisms

- Create phase detection utilities
- Add feature flag enforcement decorators (structure only)
- Define phase violation exception types
- Create phase boundary validation contracts
- **FORBIDDEN:** Feature implementations behind flags

**Status:** ✅ Complete  
**Commit:** Phase 2.4

---

### P2.5 Add Provenance & Lineage Tracking Contracts
**Maps to PRD:** Phase 2 audit preparation

- Define lineage data models in `common/models/`
- Create provenance tracking interface contracts
- Add audit trail data structure definitions
- Define tracking event types and schemas
- **FORBIDDEN:** Tracking implementations or storage logic

**Status:** ✅ Complete  
**Commit:** Phase 2.5

---

### P2.6 Phase 2 Verification & Tag
**Maps to PRD:** Phase 2 acceptance criteria

- Verify all contracts are defined but not implemented
- Verify no business logic exists in Phase 2 modules
- Verify phase enforcement mechanisms exist
- Verify structure is ready for Phase 3 implementation
- Run comprehensive Phase 2 acceptance tests

**Tag:** `phase-2-harden-complete`

**Status:** ✅ Complete

**Commit:** Phase 2.6 Complete - Tag Applied

---

### P2.7 Phase 2 Contract Integration Verification
**Maps to PRD:** Phase 2 contract readiness for Phase 3

**Objective:** Validate Phase 2 contracts can be imported and work together without implementation conflicts.

**Scope:**
- Test all Phase 2 interface imports (common/, pipelines/, state/)
- Validate abstract contract consistency and type completeness
- Check for circular dependencies between contract modules  
- Verify dataclass field ordering prevents runtime errors
- Ensure contract interfaces are ready for Phase 3 implementation

**Explicitly Not In Scope:**
- Implementation or business logic validation
- Runtime behavior testing (no implementations exist)
- External dependency verification
- Performance or execution testing

**Acceptance Criteria:**
- All Phase 2 contracts import successfully without errors
- No dataclass field ordering issues (required fields before optional)
- Abstract interface method counts verified for completeness
- No circular import dependencies detected
- Contract type hints validate correctly
- Phase 2 module structure ready for Phase 3 implementation

**Status:** ✅ Complete

**Commit:** Phase 2.7 - Contract Integration Verified

---

## Phase Transition Rules

**Phase 2 (Harden) Requirements:**
- Phase 1 must be explicitly tagged complete
- All Phase 1 acceptance criteria met
- No Phase 1 violations remain

**Phase 3 (Build) Requirements:**
- Phase 2 must be explicitly tagged complete
- All contracts and structures defined
- Phase enforcement mechanisms operational
- No premature implementations exist

---

## Phase 3 Open Questions / Decisions Required

While defining Phase 3 tasks, the following open questions and decision points were identified that require human input before full execution:

### Q3.1 Testing Strategy Integration
**Question:** Should Phase 3 include automated testing implementation alongside each task?
**Impact:** Testing could catch integration issues early but adds complexity to each task
**Decision Needed:** Include basic unit/integration tests in Phase 3, or defer testing to separate phase
**Affected Tasks:** All P3.x tasks potentially affected

### Q3.2 Research Agent Automation Scope  
**Question:** Should P3.3 Document Ingestion include automated research agent capabilities (USPTO API, Google Patents API)?
**Impact:** Manual upload only vs. automated document acquisition
**Decision Needed:** Limit Phase 3 to manual upload only, or include research automation
**Affected Tasks:** P3.3 primarily, P3.12 verification

### Q3.3 UI Technology Stack
**Question:** What technology should be used for P3.11 Minimal UI implementation?
**Impact:** Development time, maintainability, integration complexity
**Decision Needed:** Choose web framework (FastAPI templates, React SPA, etc.)
**Affected Tasks:** P3.11 UI implementation

### Q3.4 LLM Integration Approach
**Question:** How should agents integrate with LLM services (OpenAI API, local models, etc.)?
**Impact:** Cost, latency, data privacy, infrastructure requirements
**Decision Needed:** LLM service selection and integration pattern
**Decision Made:** Local LLM inference using PyTorch/Transformers stack (see DevelopmentEnvironment.md)
**Hardware Support:** Development system supports 70B+ models with RTX-5090 and 96GB RAM
**Affected Tasks:** P3.7 Agent Framework, P3.8 Agent Implementations

### Q3.5 Production vs Development Database
**Question:** Should P3.1 implement production database setup or development-only SQLite?
**Impact:** Deployment complexity, data persistence, performance characteristics
**Decision Needed:** Database selection for Phase 3 implementation
**Affected Tasks:** P3.1 Database Schema, P3.12 Integration testing

### Q3.6 Diagram Description Automation
**Question:** Should Phase 3 include automated diagram description generation or HITL-only?
**Impact:** P3.4 OCR scope, agent complexity, accuracy requirements
**Decision Needed:** Manual diagram review only vs. automated description attempts
**Affected Tasks:** P3.4 OCR and Image Processing

---

## Authority & Enforcement

- This BuildPlan is **execution-authoritative**
- PRD.md is **requirements-authoritative**
- AgentRules.md is **governance-authoritative**

If conflicts arise:
1. AgentRules.md wins
2. PRD.md defines scope
3. BuildPlan.md defines execution order

---

## One-Line Summary

> **BuildPlan.md defines how we move forward without breaking phase discipline.**


