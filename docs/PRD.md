# PRD.md  
## Phase 1 — Prune & Governance

---

## 1. Purpose

The purpose of **Phase 1 (Prune)** is to reduce the forked FastAPI boilerplate to a **minimal, predictable, and governable backend** that:

- Starts without external infrastructure
- Contains no unused or misleading features
- Is safe for AI-assisted development
- Is structurally prepared for future phases without implementing them

Phase 1 is about **removal, clarification, and control**, not adding capability.

---

## 2. In Scope (Phase 1)

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

## 3. Explicitly Out of Scope (Phase 1)

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

## 4. Non-Goals

Phase 1 does NOT attempt to:

- Deliver user-facing features
- Improve performance
- Optimize architecture
- Design final folder responsibilities
- Implement future systems early

Success is defined by **simplicity and control**, not capability.

---

## 5. Acceptance Criteria (Phase 1 Complete)

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

## 6. Phase Transition Rule

Phase 2 (Harden) may not begin until:

- Phase 1 is explicitly tagged complete
- All acceptance criteria are met
- No Phase 1 violations remain

---

## 7. One-Line Summary

> **Phase 1 removes complexity and ambiguity so later phases can add structure safely.**
