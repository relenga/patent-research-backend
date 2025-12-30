# PRD.md  
## Phase 1 — Prune & Governance

---

## Purpose

The purpose of **Phase 1 (Prune)** is to reduce the forked FastAPI boilerplate to a **minimal, predictable, and governable backend** that:

- Starts without external infrastructure
- Contains no unused or misleading features
- Is safe for AI-assisted development
- Is structurally prepared for future phases without implementing them

Phase 1 is about **removal, clarification, and control**, not adding capability.

---

## In Scope (Phase 1)

Phase 1 includes **only** the following objectives.

### 2.1 Remove Unused Template Features

The following template-provided features must be **disabled or removed entirely**:

- Redis usage
- ARQ background job queues
- Admin panels (CRUDAdmin, admin lifespan wrappers)
- Authentication (JWT, users, roles)
- Rate limiting
- Caching layers
- Example or demo endpoints
- Any code paths requiring external services at startup

**Acceptance Criteria**
- Application starts without Redis
- No background workers start automatically
- No admin services initialize
- No external services are required to run locally

---

### 2.2 Disable External Infrastructure at Startup

Application startup must be limited to:

- Configuration loading
- Logging initialization
- FastAPI app creation

**Explicitly forbidden during Phase 1 startup**:
- Redis connections
- Queue initialization
- Background workers
- Admin bootstrapping
- Database migrations

If external infrastructure is referenced, it must be:
- Disabled
- Stubbed
- Or removed

---

### 2.3 Simplify Configuration Surface

Configuration must be:

- Understandable from a single entry point
- Safe to run with **no `.env` file**
- Free of unused or misleading settings

**Requirements**
- Remove Redis-related settings
- Remove unused environment variables
- Default values must not cause crashes
- Missing optional configuration must not fail startup

---

### 2.4 Add AI Governance & Agent Control

Phase 1 must establish **explicit AI governance** to prevent architectural drift.

**Required artifacts**
- `docs/AgentRules.md`
- Clear phase definitions
- Explicit forbidden actions for agents

Agents must be able to determine:
- Current phase
- What they are allowed to change
- What must not be implemented yet

---

### 2.5 Prepare (But Do Not Implement) Target Structure

The repository must reflect **future intent** without adding behavior.

Allowed:
- Creating empty directories
- Adding `.gitkeep` files
- Documenting intended responsibilities

Forbidden:
- Adding logic
- Adding imports
- Moving existing behavior into new folders

Target directories to prepare:
- `common/`
- `pipelines/`
- `llm/`
- `state/`

---

## Explicitly Out of Scope (Phase 1)

The following items are **not allowed** in Phase 1 and must not be implemented or partially implemented:

- `/common` infrastructure logic
- State machines or lifecycle enforcement
- Phase-locked feature flags
- Pipelines or orchestration logic
- OCR functionality
- Vectorization
- LLM integration
- Database schema design
- Persistence layers
- Background task implementations

Any attempt to introduce these is a **Phase violation**.

---

## Non-Goals

Phase 1 does NOT attempt to:

- Deliver user-facing features
- Improve performance
- Optimize architecture
- Design final folder responsibilities
- Implement future systems early

Success is defined by **simplicity and control**, not capability.

---

## Acceptance Criteria (Phase 1 Complete)

Phase 1 is complete when all of the following are true:

- The application starts locally with a single command
- No external services are required
- No Redis or background queue errors appear
- Unused template features are removed
- Configuration is minimal and safe by default
- `AgentRules.md` exists and is enforced
- Target folders exist but are empty
- No future-phase code exists

---

## Phase Transition Rule

Phase 2 (Harden) may not begin until:

- Phase 1 is explicitly tagged complete
- All acceptance criteria are met
- No Phase 1 violations remain

---

## Phase 2-3 Requirements Alignment

**Note:** This PRD covers Phase 1 requirements only. Phase 2-3 requirements are execution-authoritative per BuildPlan.md.

**Phase 2 Requirements:** Structure and contract definition per BuildPlan.md Phase 2 tasks

**Phase 3 Requirements:** Core patent intelligence system implementation per BuildPlan.md P3.1-P3.12 tasks:
- **P3.1-P3.2**: Database foundation and document lifecycle management
- **P3.3-P3.4**: Document ingestion pipeline with OCR and image processing capabilities  
- **P3.5-P3.6**: Corpus management with isolation and retrieval systems
- **P3.7-P3.8**: Agent framework and patent analysis implementations
- **P3.9**: Human-in-the-loop task workflows and review processes
- **P3.10**: System logging, audit trails, and compliance infrastructure
- **P3.11**: User interface for document processing and human review
- **P3.12**: End-to-end integration and phase discipline verification

**Legal & Business Acceptance Requirements:**
- Corpus isolation prevents cross-contamination of patent prosecution and prior art analysis
- Complete audit trails support litigation requirements and professional responsibility
- Human review workflows ensure attorney oversight of AI-generated content
- Agent boundary enforcement prevents unauthorized claim language generation
- Provenance tracking enables verification of all analysis sources and reasoning

**Context Documents:** SystemNarrative.md, PipelineStateMachine.md, CorpusModel.md, AgentResponsibilities.md, ProvenanceAudit.md provide implementation context and constraints.

**Authority:** BuildPlan.md defines execution requirements. Design documents provide legal and technical constraints.

---

## Development Phase Summary (Extracted from ScopeByPhase.md)

### Task Management System Status Summary

**Overall Status:** ❌ Not Implemented

- **Phase 1:** ✅ Background task infrastructure deliberately removed (ARQ/Redis)
- **Phase 2:** ✅ HITL contracts and audit models defined as interfaces
- **Phase 3:** ❌ Human-in-the-loop workflow implementation pending (P3.9)

**Key Architecture:** Database-only task persistence, no queue system, state machine integration

### Phase Summary Overview

#### Phase 0 — Bootstrap ✅ COMPLETE
**Goal:** Environment verification and toolchain stability  
**Status:** Complete - Tagged `phase-0-complete`

#### Phase 1 — Prune ✅ COMPLETE  
**Goal:** Simplification and control through removal  
**Status:** Complete - Tagged `phase-1-prune-complete`  
**Details:** See Phase 1 requirements in this document above

#### Phase 2 — Harden ✅ COMPLETE  
**Goal:** Structure, contracts, and enforcement preparation  
**Status:** Complete - Tagged `phase-2-harden-complete`  
**Scope:** Contracts and interfaces ONLY - no implementations, no business logic, no external integrations

#### Phase 3 — Build — DESIGN GATE CLOSED
**Goal:** Feature implementation using Phase 2 contracts  
**Gate Status:** CLOSED - Technical specifications completed and approved  
**Human Approval:** All 5 critical technology decisions approved  
**Implementation Authorization:** Ready for P3.1 execution upon human authorization

**Planned Implementation Capabilities:**
- Document upload, normalization, and text extraction (manual upload path)
- OCR processing for images and scanned content with quality scoring
- Corpus classification and isolation enforcement (Open Patent, Adversarial, Product, Guidance)
- Agent execution within strict corpus and authority boundaries
- Text chunking, embedding generation, and corpus-aware retrieval
- Human-in-the-loop task generation, review workflows, and audit trails
- Basic web interface for document management and human review tasks
- Comprehensive system logging and event tracking

**Critical Enforcement Boundaries:**
- **Corpus Isolation:** Retrieval operations strictly limited to specified corpus
- **Agent Authority:** Each agent limited to defined responsibilities and corpus access
- **HITL Requirements:** Human approval mandatory for all claim outputs
- **Audit Completeness:** All actions logged with immutable provenance tracking
- **Phase Discipline:** No optimization, analytics, or production features

---

## One-Line Summary

> **Phase 1 removes complexity and ambiguity so later phases can add structure safely.**
