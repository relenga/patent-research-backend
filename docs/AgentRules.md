# AgentRules.md
## AI Governance, Phase Control & Execution Rules (Authoritative)

---

## Purpose

This document defines the **mandatory governance rules** for all AI-assisted
development in this repository (Copilot, ChatGPT, and specialized agents).

This file is the **single authoritative governance document** for the project.

Goals:
- Prevent architectural drift
- Enforce strict phase discipline
- Avoid premature implementation
- Stabilize the development environment
- Enable safe, fast AI-assisted development

This document **replaces and supersedes**:
- CopilotRules.md (deprecated)
- Previous governance documentation

---

## Authority Model (Non-Negotiable)

1. **Human developer is the final authority**
2. **This document governs AI behavior**
3. **BuildPlan.md governs execution order**
4. **PRD.md governs scope**
5. **If rules conflict, the most restrictive rule applies**
6. **If uncertain, STOP and ask**

---

## Project Phases (Authoritative)

### Phase 0 — Bootstrap ✅ COMPLETE
- Environment verification
- Toolchain stability
- No feature changes

### Phase 1 — Prune ✅ COMPLETE
- Remove unused template features
- Disable external infrastructure
- Establish governance
- Prepare empty structure only

### Phase 2 — Harden ✅ COMPLETE
- Interfaces and contracts ONLY
- No implementations
- No runtime wiring
- No external services

### Phase 3 — Build 🔄 ACTIVE / AUTHORIZED
- Concrete implementations using Phase 2 contracts
- OCR, pipelines, agents, persistence
- UI and workflow implementation
- **All enforcement rules become ACTIVE**

---

## Global Rules (Apply to ALL Agents)

1. **Phase awareness is mandatory**
   - Every change must respect the current phase
   - Future-phase features are forbidden
   - If uncertain, the agent must STOP

2. **No architecture changes without explicit approval**
   - Folder layout
   - Service boundaries
   - Dependency graph
   - Lifecycle models

3. **No new dependencies unless explicitly approved**
   - Especially databases, queues, auth, LLM SDKs

4. **No silent behavior changes**
   - Startup behavior
   - Lifespan hooks
   - Background execution

5. **Violations require immediate rollback**

---

## Documentation Map (REQUIRED READING)

**For Multi-Chat Development**: All agent chats must use this map to locate authoritative documents.

### Core Governance Documents
- **`docs/AgentRules.md`** (THIS FILE): AI governance, phase control, and execution rules
- **`docs/BuildPlan.md`**: Execution authority - what tasks exist and in what order
- **`docs/PRD.md`**: Requirements authority - what must be true (includes phase summary)
- **`docs/WBS.md`**: Work breakdown implementation details

### Business Logic & System Design  
- **`docs/SystemNarrative.md`**: Business narrative - what the system does end-to-end
- **`docs/CorpusModel.md`**: AUTHORITATIVE corpus business rules and boundaries
- **`docs/PipelineStateMachine.md`**: AUTHORITATIVE pipeline state definitions
- **`docs/DataFlowDiagram.md`**: AUTHORITATIVE visual flow reference
- **`docs/AgentResponsibilities.md`**: Agent-specific corpus access permissions
- **`docs/ProvenanceAudit.md`**: Audit requirements and compliance

### Technical Implementation Specifications
- **`docs/design/`** folder contains ALL technical specifications:
  - `DatabaseSchemaSpec.md`: Database implementation
  - `PipelineExecutionSpec.md`: Pipeline execution mechanics  
  - `CorpusEnforcementSpec.md`: Corpus isolation technical implementation
  - `HITLTaskSpec.md`: Human-in-the-loop task workflows
  - `AgentFrameworkSpec.md`: Agent technical framework
  - `APISchemaSpec.md`: API implementation specifications
  - `FailureModesSpec.md`: Error handling and recovery

### Environment & Development
- **`docs/DevelopmentEnvironment.md`**: Hardware specs, local LLM capabilities

### FORBIDDEN LOCATIONS
- **`docs/archive/`**: ❌ IGNORE COMPLETELY - obsolete documents only
- **`docs/getting-started/`**: ❌ Template documentation, not authoritative  
- **`docs/user-guide/`**: ❌ Template documentation, not authoritative

### File Creation Rules
- **Test files**: MUST go in `test_files/` directory
- **Scripts >120 chars**: MUST go in `test_files/` per Command Length Rule
- **New docs**: Only with explicit BuildPlan task authorization

### Authority Hierarchy (When Documents Conflict)
1. **AgentRules.md** (governance) - WINS
2. **BuildPlan.md** (execution order)  
3. **PRD.md** (scope requirements)
4. **Design specifications** (implementation constraints)
5. **Business logic documents** (context only)

**Rule**: If uncertain about document authority, STOP and ask the Project Manager.

---

## Agent Roles & Allowed Actions

### Architect Agent
Allowed:
- Review structure
- Identify violations
- Recommend changes

Forbidden:
- Writing code
- Adding dependencies
- Implementing features

---

### Project Manager Agent
Allowed:
- Define milestones
- Sequence tasks
- Enforce phase boundaries

Forbidden:
- Writing production code
- Refactoring logic

---

### Developer Agent
Allowed:
- Implement explicitly assigned tasks
- Make minimal, scoped changes

Forbidden:
- Implementing future-phase logic
- Architectural invention

---

### Debugger Agent
Allowed:
- Diagnose errors
- Remove root causes
- Fix deterministic defects

Forbidden:
- Masking issues
- Adding infrastructure to “fix” problems

---

## Backend Lifecycle Invariant (CRITICAL)

**Backend start/stop is ALWAYS human-controlled.**

AI agents MUST NOT:
- Start backend servers
- Start frontend servers
- Manage runtime processes
- Use VS Code integrated terminals for server execution

ONLY supported backend startup:
- `RunJobs/startBackend.bat`

If backend appears broken:
➡ Instruct the user to restart using the batch file.

---

## Execution Environment Rules (Windows-Specific)

### Terminal Rules
- DO NOT use VS Code integrated terminals for servers
- Use Windows native terminals only
- Use `;` instead of `&&` in PowerShell
- Prefer PowerShell-native commands

### Command Length Rule
- Commands >120 characters must be moved to `.py` files
- All test scripts go in `test_files/`

---

## Inter-Chat Communication Rules

- NO code blocks in inter-chat prompts
- Plain text instructions only
- Explicit file paths and line ranges
- Prompts must be copy/paste safe

---

## API & Persistence Standards (Phase-Conditional)

### API Routing
- Trailing slash policy must be consistent
- Frontend must match backend paths exactly
- Versioned prefix required (`/api/v1`)

### Database (Introduced in Phase 3)
- Use approved `get_session()` context manager
- No manual session creation
- No deprecated patterns

---

## Change Control

Any of the following require **explicit human approval**:
- Architecture changes
- New agents
- New pipelines
- New dependencies
- Changes to this document

Unapproved changes must be reverted.

---

## Violation Handling

If an agent:
- Implements future-phase features
- Adds undeclared dependencies
- Changes architecture without approval

➡ The change MUST be reverted immediately.

---

## One-Line Rule

> **If it’s not allowed in this phase, the agent must not write it.**

---

## Documentation Integrity & Synchronization

**Rule:** All documentation MUST accurately reflect the current codebase.

- When features are added, removed, or materially changed, relevant documentation MUST be updated in the same change set.
- README.md is considered a **governed artifact**, not marketing material.
- Any detected mismatch between documentation and code constitutes a governance violation.

---

## File & Directory Management Authority

- Agents MAY create files only when explicitly required by the active BuildPlan task.
- Agents MAY NOT restructure, move, or delete directories without Project Manager authorization.
- Large structural changes require documentation updates.

---

## Scope Conflict & Creep Handling

If a request conflicts with the current phase scope:

1. Agent MUST halt execution
2. Agent MUST flag the conflict
3. Project Manager decides:
   - Reject
   - Defer to later phase
   - Amend scope documents

Agents may NOT silently expand scope.

---

## Phase Transition Authority

- Only the Project Manager may authorize phase transitions.
- Phase completion requires:
  - All tasks marked complete
  - Verification step executed
  - Explicit phase tag applied in git

Agents may NOT self-transition phases.

---

## Configuration Management Rules

- `.env` files, secrets, and configuration defaults are **governed assets**
- Agents may NOT introduce new environment variables without approval
- Production-affecting configuration changes require human approval

---

## Git & Version Control Governance

- Agents may commit only when explicitly authorized
- Tags are reserved for phase boundaries
- Branch creation for templates or experiments must be documented

---

## External Dependency & Service Approval

- Any new external service, API, or dependency requires:
  - Explicit PM approval
  - Justification
  - Scope impact acknowledgment

---

## Testing & Quality Requirements

Testing requirements are phase-specific:

- Phase 1–2: Structural validation only
- Phase 3: Functional tests required
- Phase 4+: Performance, robustness, and adversarial testing

Agents must not introduce tests beyond the active phase scope.

---

## Emergency Override Procedures

In exceptional circumstances requiring rule suspension:

- Human developer MUST document override reason
- Human developer MUST specify restoration plan
- Override duration MUST be time-bounded
- All overrides MUST be reviewed in next phase transition

Examples of valid emergency overrides:
- Critical security vulnerability requiring immediate patch
- Production system failure requiring emergency fix
- External dependency failure requiring workaround

Overrides do NOT apply to:
- Feature development shortcuts
- Convenience modifications
- Performance optimizations

---

## Enforcement Escalation

**Violation Tracking:**
- First violation: Warning and immediate rollback
- Second violation: Additional restrictions on agent type
- Third violation: Agent type disabled until human review

**Repeated violations by the same agent type triggers:**
- Mandatory human approval for all changes by that agent type
- Reduced autonomy until compliance demonstrated
- Documentation update required explaining restriction

**Escalation Reset:**
Violation count resets at each phase transition, allowing fresh start with new phase rules.

