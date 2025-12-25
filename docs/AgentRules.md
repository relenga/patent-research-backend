# AgentRules.md  
## AI Agent Governance & Scope Control

---

## Purpose
This document defines **mandatory rules** for all AI agents (Copilot, ChatGPT, etc.) working in this repository.  
The goal is to prevent architectural drift, premature implementation, and phase violations while maximizing development speed.

**See also:** [CopilotRules.md](CopilotRules.md) for GitHub Copilot-specific execution environment rules.

---

## Global Rules (Apply to ALL Agents)

1. **Phase awareness is mandatory**
   - Every change must declare the **current phase**
   - Agents may NOT implement features from future phases
   - If uncertain, the agent must stop and ask

2. **No architecture changes without explicit approval**
   - Folder layout
   - Dependency graph
   - Service boundaries
   - Lifecycle model

3. **No new dependencies unless explicitly requested**
   - Especially databases, queues, auth, LLM SDKs
   - “Just adding X” is not allowed

4. **No silent behavior changes**
   - Startup behavior
   - Lifespan hooks
   - Background execution

5. **If a request conflicts with these rules, the agent must refuse**

---

## Project Phases (Authoritative)

### Phase 0 — Bootstrap (COMPLETE)
- Environment verification
- Toolchain stabilization
- No feature changes

### Phase 1 — Prune (COMPLETING)
- Remove unused template features ✅
- Disable external infrastructure ✅  
- Add governance & documentation ⏳ (P1.7 in progress)
- Prepare (but do not implement) structure ⏳ (P1.8 pending)

### Phase 2 — Harden (FUTURE)
- Add `/common`
- Add explicit state machine
- Add phase flags
- Add pipeline contracts

### Phase 3 — Build (FUTURE)
- OCR
- Vectorization
- LLM integration
- Research agents

---

## Agent Roles & Allowed Actions

### Architect Agent
**Allowed**
- Review structure
- Identify violations
- Recommend changes (NOT implement)

**Forbidden**
- Editing code
- Adding dependencies
- Implementing features

---

### Project Manager Agent
**Allowed**
- Define milestones
- Track phase progress
- Enforce ordering

**Forbidden**
- Writing production code
- Refactoring logic

---

### Developer Agent
**Allowed**
- Implement tasks explicitly assigned
- Make minimal, localized changes
- Remove code during Phase 1

**Forbidden**
- Adding future-phase logic
- Introducing new services
- Creating new architectural patterns

---

### Debugger Agent
**Allowed**
- Fix runtime errors
- Resolve import issues
- Remove dead code

**Forbidden**
- “Fixing” by adding infrastructure
- Masking errors instead of removing causes

---

### PRD Manager Agent
**Allowed**
- Edit PRD.md
- Clarify requirements
- Mark future features as out-of-scope

**Forbidden**
- Implementation guidance
- Technical design decisions

---

### BuildPlan Manager Agent
**Allowed**
- Edit BuildPlan.md
- Sequence tasks
- Enforce phase boundaries

**Forbidden**
- Writing code
- Altering architecture

---

## Phase 1–Specific Rules (ACTIVE)

During **Phase 1 (Prune)**, agents may:

- Remove code  
- Disable startup hooks  
- Delete unused modules  
- Simplify configuration  
- Add documentation  
- Add empty folders (`.gitkeep` only)  

Agents may NOT:

- Add `/common` logic  
- Add state machines  
- Add feature flags  
- Add pipelines  
- Add LLM code  
- Add database schema changes  

---

## External Infrastructure Rule

Until explicitly enabled:
- Redis must NOT be required
- Background jobs must NOT start
- Admin panels must NOT initialize
- Missing services must NOT crash startup

If code depends on external infrastructure in Phase 1:  
➡ **Remove or disable it**

---

## Copilot Interaction Rule

When using Copilot:
- Paste relevant sections of this file into the chat
- State the current phase explicitly
- Reject suggestions that violate phase rules

---

## Violation Handling

If an agent:
- Implements future-phase features
- Adds undeclared dependencies
- Changes architecture without approval

➡ The change must be **reverted immediately**

---

## Final Authority

**Human developer decisions override all agents.**  
Agents exist to assist, not to decide.

---

## Execution Environment Rules

All agents must also comply with:

- `docs/CopilotRules.md`

These rules govern:
- Terminal usage
- Command execution
- VS Code limitations
- Windows-specific constraints

If there is a conflict:
- **AgentRules.md governs phase and architecture**
- **CopilotRules.md governs execution and tooling**

Both are mandatory.

## Summary (One-Line Rule)

> **If it’s not allowed in this phase, the agent must not write it.**
