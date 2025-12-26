# BuildPlan.md  
## Phase-Based Execution Plan

---

## Purpose

This document defines the **execution plan** for the project.  
It translates **PRD requirements** into **ordered, phase-scoped tasks**.

Key principles:
- PRD defines *what must be true*
- BuildPlan defines *how and in what order we execute*
- Task numbering is **phase-scoped** and **stable**
- No task may violate phase boundaries defined in AgentRules.md

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

### Phase 2 — Harden (NEXT)
Goal: Introduce structure, contracts, and enforcement

**Status:** 🔄 Ready to begin

---

### Phase 3 — Build (FUTURE)
Goal: Implement OCR, pipelines, and LLM-driven functionality

**Status:** 🔮 Future - Planning deferred until Phase 2 completion

**Functional Scope (Per Governance Docs):**
- OCR functionality
- Vectorization
- LLM integration  
- Research agents
- Pipeline orchestration logic
- Background task implementations
- Database schema design (if needed)

**Planning Approach:**
- Detailed task breakdown will be defined as Phase 2 nears completion
- Implementation order and technical decisions to be determined collaboratively
- Task definitions will leverage Phase 2 contracts and structures

**Phase 3 Gate:**
- Cannot begin until Phase 2 is tagged complete
- Requires Phase 2 contracts to be operational
- Task planning session required before implementation begins

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
- Add cross-references between AgentRules.md and CopilotRules.md
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

**Status:** ⏳ Pending

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


