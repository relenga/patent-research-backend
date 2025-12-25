# BuildPlan.md  
## Phase-Based Execution Plan

---

## 1. Purpose

This document defines the **execution plan** for the project.  
It translates **PRD requirements** into **ordered, phase-scoped tasks**.

Key principles:
- PRD defines *what must be true*
- BuildPlan defines *how and in what order we execute*
- Task numbering is **phase-scoped** and **stable**
- No task may violate phase boundaries defined in AgentRules.md

---

## 2. Task Numbering Convention

All execution tasks follow this format:

P<Phase>.<TaskNumber>


Examples:
- P1.1 = Phase 1, Task 1
- P2.3 = Phase 2, Task 3

Task numbers are **unique within a phase**, not global.

---

## 3. Phase Overview

### Phase 0 — Bootstrap (COMPLETE)
Goal: Verify environment and toolchain

Status: ✅ Complete  
Tag: `phase-0-complete`

---

### Phase 1 — Prune (CURRENT)
Goal: Remove unused features, disable external infrastructure, and establish governance

This phase focuses on **simplification and control**, not capability.

---

### Phase 2 — Harden (FUTURE)
Goal: Introduce structure, contracts, and enforcement

---

### Phase 3 — Build (FUTURE)
Goal: Implement OCR, pipelines, and LLM-driven functionality

---

## 4. Phase 1 — Prune (Detailed Task Plan)

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

**Status:** ⏳ Pending

---

### P1.7 Add Governance & AI Control Docs  
**Maps to PRD:** §2.4 Add AI Governance

- Add `docs/AgentRules.md`
- Add `docs/PRD.md`
- Add `docs/BuildPlan.md`
- Add `docs/CopilotRules.md`
- Cross-reference governance documents

**Status:** ⏳ Pending

---

### P1.8 Prepare Target Folder Structure  
**Maps to PRD:** §2.5 Prepare Structure

Create empty directories only (no logic):

- `common/`
- `pipelines/`
- `llm/`
- `state/`

Use `.gitkeep` files as needed.

**Status:** ⏳ Pending

---

### P1.9 Phase 1 Verification & Tag  
**Maps to PRD:** §5 Acceptance Criteria

- Verify application starts with single command
- Verify no external services required
- Verify no Redis / ARQ / auth / admin references
- Verify governance docs exist

**Tag:** `phase-1-prune-complete`

**Status:** ⏳ Pending

---

## 5. Phase Transition Rules

Phase 2 (Harden) may not begin until:

- All Phase 1 tasks are complete
- Phase 1 acceptance criteria are met
- Phase 1 is explicitly tagged
- No Phase 1 violations remain

---

## 6. Authority & Enforcement

- This BuildPlan is **execution-authoritative**
- PRD.md is **requirements-authoritative**
- AgentRules.md is **governance-authoritative**

If conflicts arise:
1. AgentRules.md wins
2. PRD.md defines scope
3. BuildPlan.md defines execution order

---

## 7. One-Line Summary

> **BuildPlan.md defines how we move forward without breaking phase discipline.**


