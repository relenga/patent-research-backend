# Work Breakdown Structure (WBS)
## Phase 3 Implementation Task Breakdown

**Authority:** This WBS provides detailed breakdown of BuildPlan.md Phase 3 tasks only.
**Authority Chain**: AgentRules.md (governance) → [Standards.md](Standards.md) (technical standards) → BuildPlan.md (execution authority) → **WBS.md (implementation details)** → Design specs (guidance only)
**Note:** Task numbering aligns with BuildPlan P3.x structure for consistency.

**MANDATORY STANDARDS COMPLIANCE**: All WBS tasks must comply with [Standards.md](Standards.md) requirements. See BuildPlan.md for complete compliance process.

## Task Management System Status

**Current Implementation Status:** ❌ Not Built

**Design Status:**
- ✅ **Phase 1 (Complete):** Background task infrastructure (ARQ/Redis) deliberately removed
- ✅ **Phase 2 (Complete):** Abstract contracts and data models defined
- ❌ **Phase 3 (Not Started):** HITL workflows and task management implementation

**Key Architecture Decisions:**
- **No Background Queue System:** Phase 1 removed ARQ/Redis - tasks managed through database persistence only
- **State Machine Integration:** Human tasks trigger document state transitions
- **Provenance Tracking:** All task decisions tracked through Phase 2 audit contracts
- **Database-Only Approach:** Task persistence, assignment, and lifecycle through SQL only

---

## 3.1 Database Schema & Persistence Layer (P3.1) ✅ **COMPLETE**
- 3.1.1 Design and implement relational database schema (documents, versions, states, lineage) ✅
- 3.1.2 Create database connection and session management per [Standards.md](Standards.md) PostgreSQL service requirements ✅
- 3.1.3 Implement document CRUD operations with state tracking ✅
- 3.1.4 Build lineage persistence (parent-child relationships, derivation tracking) ✅
- 3.1.5 Add immutable audit event logging (who, what, when, why) using [Standards.md](Standards.md) LoggingService ✅
- 3.1.6 **Database Migration**: DEFERRED - Fresh schema creation only for Phase 3 (no Alembic, versioned migrations, or automated schema migration tools per Standards.md) ✅
- **3.1.7 VERIFICATION**: Confirm PostgreSQL service usage, no direct database access, LoggingService integration, and [Standards.md](Standards.md) compliance ✅
- **Completion Date**: January 2, 2026 - All functional tests passing, Tester verification passed, Standards.md compliance confirmed

## 3.2 Pipeline State Machine Execution (P3.2)

### 3.2A Pipeline Coordination Core Implementation (P3.2A) ✅ **COMPLETE**
**Phase 3.2A Coordination Enhancements** - COMPLETE with production deployment authorization

**Objective**: Implement core pipeline coordination to handle complex documents with 15-20+ diagrams without deadlocks or starvation

**Tasks:**
- 3.2A.1 Build state transition executor with Phase 3.2A coordination rules (validates transitions, updates database, triggers next steps) ✅
- 3.2A.2 Implement simplified document completion logic (90% threshold for READY, 70-89% for PARTIALLY_PROCESSED) ✅
- 3.2A.3 Add basic diagram classification system (critical/supporting/decorative with automatic rules) ✅
- 3.2A.4 Implement 3-level similarity thresholds (≥95% duplicate, 80-94% near-duplicate, <80% unique) ✅
- 3.2A.5 Add pipeline step runner framework with resource management (GPU limits, priority queues) ✅
- 3.2A.6 Create pipeline starvation prevention (24-hour timeout, automatic escalation) ✅
- 3.2A.7 Build enhanced override logging (mandatory override_reason field with audit trail) ✅
- 3.2A.8 Add state change event publishing with coordination metadata ✅
- 3.2A.9 Build pipeline progress tracking for complex documents ✅
- 3.2A.10 Add manual state transition override with enhanced audit (admin only) ✅
- **3.2A.11 VERIFICATION**: Confirm Phase 3.2A coordination rules prevent pipeline deadlocks, handle 15-20+ diagram documents, and maintain [Standards.md](Standards.md) compliance ✅

**Completion Summary - January 3, 2026:**
- **Production Authorization**: System approved for immediate production deployment
- **Complex Document Success**: 100% success rate handling documents with 15-22+ diagrams
- **Resource Management**: GPU/OCR limits enforced, zero pipeline starvation scenarios recorded
- **Standards Compliance**: Full [Standards.md](Standards.md) compliance with embedded service pattern
- **Service Integration**: Stable concrete service implementation resolving circular import issues
- **State Machine Compliance**: All transitions follow PipelineStateMachine.md authority exactly

### 3.2B Advanced Pipeline Coordination (P3.2B) - Risk Mitigation Framework
**Status**: PLANNED - Comprehensive risk mitigation approach based on P3.2A lessons learned  
**Reference**: [StateMachine.md proposal](proposals/StateMachine.md) contains detailed analysis of advanced coordination features  
**Approach**: Architect-led design review with mandatory pre-development risk mitigation to prevent 3.2A issues  
**Total Duration**: 9-12 weeks with phased implementation to minimize complexity risks

#### Phase 3.2B Pre-Development - Risk Mitigation (MANDATORY)
*Duration: 8-12 days total*

- **3.2B.1 Architect Design Review Session** (2-3 days)
  - P3.2B Risk Assessment and Architecture Strategy deliverable
  - Review 3.2A operational data, assess feature complexity, design service integration patterns
  - **Dependency**: P3.2A operational minimum 30 days
  - **Success Criteria**: Architect sign-off with risk mitigation strategies

- **3.2B.2 Document Phase 3.2A Lessons Learned** (1-2 days)
  - Formal post-mortem with preventable issues analysis
  - Standards violations, runtime failures, circular imports, governance gaps documentation
  - **Success Criteria**: Institutional learning with specific P3.2B prevention strategies

- **3.2B.3 Define Sub-Phase Implementation Strategy** (1-2 days)
  - Break P3.2B into Alpha/Beta/Gamma/Delta sub-phases for manageable complexity
  - Feature complexity assessment, dependency analysis, implementation sequence planning
  - **Success Criteria**: Clear sub-phase boundaries with minimized integration complexity

- **3.2B.4 Create Pre-Implementation Validation Framework** (2-3 days)
  - Governance compliance checklists and technical validation templates
  - [Standards.md](Standards.md) compliance patterns, service integration templates, import structure validation
  - **Success Criteria**: Framework prevents governance violations through upfront verification

- **3.2B.5 Governance Integration Strategy Development** (1-2 days)
  - Developer compliance workflow with mandatory architect approval gates
  - Review points, compliance verification, risk checkpoint framework
  - **Success Criteria**: Governance integrated preventing post-implementation correction cycles

#### Phase 3.2B-Alpha: Core Advanced Coordination (8-12 days)
*Dependencies: All pre-development complete, architect approval*

- **3.2B-Alpha.1 Service Integration Pattern Implementation** (1-2 days)
- **3.2B-Alpha.2 Complex Timeout Matrices Implementation** (3-4 days)  
- **3.2B-Alpha.3 Advanced Priority Queue System** (2-3 days)
- **3.2B-Alpha.4 Integration Testing and Validation** (1-2 days)

#### Phase 3.2B-Beta: State Management and Processing (8-11 days)
*Dependencies: 3.2B-Alpha complete and validated*

- **3.2B-Beta.1 REPROCESSING State Implementation** (3-4 days)
- **3.2B-Beta.2 Batch Processing Optimizations** (2-3 days)
- **3.2B-Beta.3 Quality Scoring Automation** (2-3 days)

#### Phase 3.2B-Gamma: Enterprise Monitoring and Analytics (9-12 days)
*Dependencies: 3.2B-Beta complete, event publishing operational*

- **3.2B-Gamma.1 Pipeline Analytics Dashboard** (4-5 days)
- **3.2B-Gamma.2 Advanced Monitoring Integration** (2-3 days)
- **3.2B-Gamma.3 Performance Optimization Analytics** (3-4 days)

#### Phase 3.2B-Delta: Resource Allocation Optimization (7-9 days)
*Dependencies: 3.2B-Gamma analytics operational*

- **3.2B-Delta.1 Advanced Resource Algorithms** (4-5 days)
- **3.2B-Delta.2 Load Balancing and Scaling** (3-4 days)

#### Phase 3.2B Integration and Deployment (5-7 days)
*Dependencies: All sub-phases complete*

- **3.2B.98 Comprehensive Integration Testing** (3-4 days)
- **3.2B.99 Production Deployment and Validation** (2-3 days)
- Resource requirements analysis after P3.2A deployment
- Integration complexity assessment with actual usage patterns
- Cost-benefit analysis of advanced coordination features

**Acceptance Criteria**: TBD based on operational learnings from P3.2A deployment

## 3.3 Document Ingestion Implementation (P3.3)
- 3.3.1 Build file upload handler (PDF, XML, HTML, images)
- 3.3.2 Implement document normalization (extract text, preserve originals)
- 3.3.3 Add metadata extraction (titles, dates, document types)
- 3.3.4 Create source tagging (manual_upload, research_agent)
- 3.3.5 Build document validation and format checking
- 3.3.6 Add ingestion error handling and recovery
- **3.3.7 VERIFICATION**: Confirm API standards compliance, common services usage, error handling per ErrorCode enum, and [Standards.md](Standards.md) compliance

## 3.4 OCR and Image Processing Pipeline (P3.4)
- 3.4.1 Build image extraction from PDF documents
- 3.4.2 Implement OCR text recognition for scanned content
- 3.4.3 Add image fingerprinting for duplicate detection
- 3.4.4 Create image metadata tracking (dimensions, format, source page)
- 3.4.5 Build OCR confidence scoring and quality flags
- 3.4.6 Add OCR result validation and correction workflows
- **3.4.7 VERIFICATION**: Confirm OCR service usage per [Standards.md](Standards.md), common services integration, and logging requirements

## 3.5 Corpus Classification and Storage (P3.5)
- 3.5.1 Build document type classification (patent, prior_art, product_doc, office_action)
- 3.5.2 Implement corpus assignment logic (Open Patent, Adversarial, Product, Guidance)
- 3.5.3 Add corpus isolation enforcement (prevent cross-corpus retrieval)
- 3.5.4 Create corpus integrity validation and health checks
- 3.5.5 Build corpus-specific access controls and permissions
- 3.5.6 Add document reclassification workflows with audit trails
- **3.5.7 VERIFICATION**: Confirm corpus isolation enforcement, common services usage, audit logging, and [Standards.md](Standards.md) compliance

## 3.6 Text Chunking and RAG Infrastructure (P3.6)
- 3.6.1 Build text chunking strategy (sentence-based, paragraph-based)
- 3.6.2 Implement embedding generation for text chunks
- 3.6.3 Add vector database integration for similarity search
- 3.6.4 Create corpus-aware retrieval (search within specific corpus only)
- 3.6.5 Build retrieval result ranking and relevance scoring
- 3.6.6 Add retrieval caching and performance optimization
- **3.6.7 VERIFICATION**: Confirm RAG service usage per [Standards.md](Standards.md), corpus isolation in retrieval, and logging requirements

## 3.7 Agent Execution Framework (P3.7)
- 3.7.1 Build agent execution runtime (prompt construction, LLM calls, response parsing)
- 3.7.2 Implement agent boundary enforcement (corpus access restrictions)
- 3.7.3 Add agent prompt templating and parameter injection
- 3.7.4 Create agent execution logging and audit trails
- 3.7.5 Build agent result validation and schema enforcement
- 3.7.6 Add agent failure handling and retry mechanisms
- **3.7.7 VERIFICATION**: Confirm LLM service usage per [Standards.md](Standards.md), versioning standards for templates, and comprehensive audit logging

## 3.8 Core Agent Implementations (P3.8)
- 3.8.1 Build Classification Agent (assign doc_type and corpus)
- 3.8.2 Implement Prior Art Analysis Agent (identify conflicts, risk only)
- 3.8.3 Add Office Action Analysis Agent (extract examiner reasoning)
- 3.8.4 Create Product Mapping Agent (map features to disclosures)
- 3.8.5 Build Claim Drafting Agent (generate claims from Open Patent Corpus only)
- 3.8.6 Add Support Verification Agent (validate claim support in open patent)
- **3.8.7 VERIFICATION**: Confirm agent boundary enforcement, corpus isolation compliance, versioning of agent outputs, and [Standards.md](Standards.md) compliance

## 3.9 HITL Task Generation and Workflow (P3.9)
**Current Status:** Not implemented - requires full Phase 3 implementation

**Design Status:** Phase 2 contracts defined, Phase 1 background task system removed

**Implementation Tasks:**
- 3.9.1 Build task creation triggered by agent outputs and pipeline failures
- 3.9.2 Implement task lifecycle management (created, assigned, in_review, completed, rejected)
- 3.9.3 Add human task interface (review context, approve/reject, add notes)
- 3.9.4 Create task assignment and routing logic
- 3.9.5 Build task completion workflow with audit trails
- 3.9.6 Add task escalation for overdue or complex reviews
- **3.9.7 VERIFICATION**: Confirm API standards compliance, common services usage, audit logging integration, and [Standards.md](Standards.md) compliance

**Key Design Notes:**
- Will NOT use background task queues (ARQ/Redis removed in Phase 1)
- Task persistence through database-only approach
- Human review tasks integrated with document state machine
- Audit trails tracked through provenance system

## 3.10 System Logging and Event Infrastructure (P3.10)
- 3.10.1 Build structured logging infrastructure (JSON logs, correlation IDs)
- 3.10.2 Implement event publishing for all major system actions
- 3.10.3 Add error logging and exception tracking
- 3.10.4 Create log aggregation and search capabilities
- 3.10.5 Build system health monitoring and alerting
- 3.10.6 Add user-facing activity logs and audit reports
- **3.10.7 VERIFICATION**: Confirm LoggingService interface usage per [Standards.md](Standards.md), event taxonomy compliance, and structured logging requirements

## 3.11 Minimal UI for HITL and System Visibility (P3.11)
- 3.11.1 Build document upload and viewing interface
- 3.11.2 Implement task review interface (display context, capture decisions)
- 3.11.3 Add document and pipeline status visibility
- 3.11.4 Create basic search and navigation
- 3.11.5 Build audit log viewer for transparency
- 3.11.6 Add system status and error reporting dashboard
- **3.11.7 VERIFICATION**: Confirm API standards compliance, UI patterns adherence, configuration management, and [Standards.md](Standards.md) compliance

## 3.12 Phase 3 Integration and Verification (P3.12)
- 3.12.1 Run complete document processing workflow (upload → OCR → corpus assignment → agent analysis → HITL review)
- 3.12.2 Verify corpus isolation maintained throughout all operations
- 3.12.3 Test agent boundary enforcement and authority restrictions
- 3.12.4 Validate provenance tracking from source documents to final outputs
- 3.12.5 Check audit trail completeness and immutability
- **3.12.6 COMPREHENSIVE VERIFICATION**: Validate complete [Standards.md](Standards.md) compliance across all implemented components - common services usage, API standards, configuration patterns, logging requirements, versioning compliance, and governance enforcement
---

## WBS-to-BuildPlan Mapping

| WBS Section | BuildPlan Task | Design Document Authority |
|-------------|----------------|---------------------------|
| 3.1 | P3.1 | SystemNarrative, PipelineStateMachine, ProvenanceAudit |
| 3.2 | P3.2 | SystemNarrative §1-2, PipelineStateMachine stages 1-4 |  
| 3.3 | P3.3 | SystemNarrative §4, PipelineStateMachine stages 5-6 |
| 3.4 | P3.4 | CorpusModel, AgentResponsibilities |
| 3.5 | P3.5 | PipelineStateMachine stages 7-10, AgentResponsibilities |
| 3.6 | P3.6 | SystemNarrative §6 |
| 3.7 | P3.7 | AgentResponsibilities analysis agents |
| 3.8 | P3.8 | AgentResponsibilities Claim Drafting Agent |
| 3.9 | P3.9 | SystemNarrative §8, AgentResponsibilities |
| 3.10 | P3.10 | All design documents validation |

---

## Authority Statement

- **Execution Authority:** BuildPlan.md defines what tasks exist and in what order
- **Detail Authority:** This WBS defines how BuildPlan tasks break into implementable work items
- **Context Authority:** Design documents define what must be implemented

**Planning Status:** Aligned pending final human design review. Design documents may still evolve during planning alignment. Phase 3 execution does not begin until explicit human authorization.

**Note:** This WBS covers Phase 3 only. Phase 1-2 work is complete per BuildPlan.md status.
