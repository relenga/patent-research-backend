Replace the entire contents of README.md with the following:

# Governed Patent Intelligence Backend

> ⚠️ **AUTHORITATIVE NOTICE**
>
> This repository is a **heavily pruned and governed derivative** of the Benav Labs FastAPI boilerplate.
> Many template features were intentionally removed.
>
> **docs/AgentRules.md is authoritative.**
> If this README conflicts with AgentRules.md or BuildPlan.md, this README is wrong.

---

## Project Status

**Current Phase:** Phase 3 — Build (ACTIVE)  
**Governance:** Strict phase-controlled development  
**Primary Goal:** Patent claim generation, validation, and litigation support

---

## What This System Is

This is a **governed AI backend** designed to support:

- Patent document ingestion (USPTO, OA/IPR, prior art, competitive product docs)
- Research-agent–driven corpus construction
- Claim drafting grounded in an open patent specification
- Risk evaluation against prior art, Office Actions, and IPRs
- Product-to-claim mapping for litigation targeting
- Full provenance, auditability, and defensibility of generated claims

This system exists to **support patent prosecution and litigation**, not to act as a generic web backend.

---

## What Is Explicitly NOT Included

The following were **removed in Phase 1 (Prune)** and **do not exist** in this repository:

- ❌ Authentication (JWT, sessions, users)
- ❌ Rate limiting or tier systems
- ❌ Background task queues (ARQ, Celery, Redis workers) - includes HITL task systems
- ❌ Redis caching (server or client)
- ❌ Admin panels
- ❌ Docker / CI / production orchestration
- ❌ setup.py bootstrap scripts

These may be reintroduced **only with explicit Project Manager approval** and corresponding documentation updates.

---

## Current Capabilities (Phase 2 Complete)

Structural foundations only — **business logic is implemented in Phase 3+**:

- FastAPI application skeleton
- Governed common services (logging, IDs, time, context) — interfaces/contracts
- Deterministic pipeline contracts — interfaces/contracts
- Explicit document state machine — enums + transition tables
- Provenance, lineage, and audit data models (no persistence logic yet)
- Phase enforcement & feature-flag scaffolding (no runtime enforcement in Phase 2)
- Windows-stable backend lifecycle control

---

## Governance (Read These First)

All development is governed by:

- `docs/AgentRules.md`
- `docs/BuildPlan.md`
- `docs/PRD.md`
- `docs/ScopeByPhase.md`
- System design documents in `docs/`

Agents and contributors **must comply** with phase constraints and authority rules.

---

## How to Run the Backend (Authoritative)

**Backend startup is human-controlled.**

```text
RunJobs/startBackend.bat


