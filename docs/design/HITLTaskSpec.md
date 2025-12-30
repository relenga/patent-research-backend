# HITL Task Specification — CONSOLIDATED TASK MANAGEMENT AUTHORITY

**Status**: APPROVED - FastAPI+HTMX UI and Single Reviewer Confirmed (Dec 30, 2025)  
**Authority**: SINGLE AUTHORITY for all task management system requirements and implementation  
**Cross-References**: [PipelineStateMachine.md](../../PipelineStateMachine.md) (task triggers), [AgentResponsibilities.md](../../AgentResponsibilities.md) (task generation agents), [DatabaseSchemaSpec.md](./DatabaseSchemaSpec.md), [PipelineExecutionSpec.md](./PipelineExecutionSpec.md)

## Consolidated Task Management Authority

**This document is the SINGLE SOURCE OF TRUTH for:**
- Task lifecycle definitions and state management
- HITL workflow requirements and implementation patterns  
- Task assignment models and reviewer interaction
- Evidence bundle structure and assembly
- UI requirements for task management
- Pipeline integration and trigger mechanisms

**Referenced Documents** (provide context, not authority):
- **PipelineStateMachine.md**: Documents state transitions that trigger task creation
- **AgentResponsibilities.md**: Defines agents that generate tasks requiring human review
- **BuildPlan.md P3.9**: Execution requirements (references this spec for implementation details)
- **TaskManagementSystemStatus.md**: OBSOLETE - superseded by this specification

## Implementation History and Status

### Phase 1 — Prune ✅ Complete
**Decision**: Background task infrastructure deliberately **removed**
- ❌ ARQ (Async Redis Queue) removed from FastAPI boilerplate
- ❌ Redis workers removed  
- ❌ Background task processing infrastructure removed
- **Rationale**: Unnecessary complexity for initial patent intelligence requirements

### Phase 2 — Harden ✅ Complete  
**Design Status**: Abstract contracts and data models defined
- ✅ `state/` module: Document state machine with task-triggering transitions
- ✅ `common/models/audit.py`: Task audit tracking schemas
- ✅ `common/models/provenance.py`: Provenance tracking for human decisions
- ✅ Pipeline contracts for task generation triggers

### Phase 3 — Build (This Specification)
**Implementation Approach**: Database-only task management
- **No Background Queue System**: Tasks managed through PostgreSQL persistence only
- **State Machine Integration**: Human tasks trigger document state transitions
- **Provenance Tracking**: All task decisions tracked through audit contracts
- **Single Reviewer Model**: Simplified assignment for Phase 3

## Purpose

Defines human-in-the-loop task lifecycle, assignment model, evidence bundle structure, UI requirements, and pipeline integration for patent intelligence workflows.

## Required Content (Minimum Specification)

### Task Lifecycle States

#### Core States
- [ ] **PENDING**: Task created, awaiting human assignment
- [ ] **ASSIGNED**: Task assigned to human reviewer  
- [ ] **IN_PROGRESS**: Human actively working on task
- [ ] **REVIEW_REQUIRED**: Task completed, requires secondary review
- [ ] **COMPLETED**: Task approved and pipeline advancement authorized
- [ ] **REJECTED**: Task rejected, requiring rework or escalation

#### State Transitions
- [ ] Valid transition matrix with authorization requirements
- [ ] Automatic timeout handling for stalled tasks
- [ ] Escalation triggers for overdue tasks
- [ ] Rollback procedures for rejected tasks

### Assignment Model (APPROVED APPROACH)

#### Single Reviewer Strategy
- [x] **Single Human Reviewer**: All tasks assigned to single reviewer for Phase 3
- [x] **Reviewer Selection**: Dropdown or fixed identifier selection (no authentication)
- [x] **Task Assignment**: Automatic assignment to selected reviewer
- [x] **Session Tracking**: Basic context preservation across browser sessions
- [x] **No User Management**: No login, passwords, roles, or multi-user support

#### Actor Identity Integration
- [x] **Simple Identity Model**: Reviewer name stored for audit compliance only
- [x] **Session Continuity**: Task state preserved across reviewer sessions
- [x] **Activity Logging**: All reviewer actions logged with reviewer identifier
- [x] **Context Preservation**: Task evidence and decisions preserved

### Evidence Bundle Structure

#### Bundle Composition
- [ ] **Primary Documents**: Source documents for review
- [ ] **Agent Outputs**: Agent-generated analysis or claims
- [ ] **Context Information**: Corpus boundaries, agent authorities
- [ ] **Validation Data**: Supporting evidence and references
- [ ] **Review Criteria**: Specific acceptance requirements

#### Bundle Assembly
- [ ] Automatic evidence gathering from agent runs
- [ ] Context enrichment with relevant metadata
- [ ] Bundle validation and completeness checks
- [ ] Version control for bundle modifications

### UI Requirements (APPROVED APPROACH)

#### FastAPI Server-Rendered Interface
- [x] **Technology Stack**: Jinja2 templates + HTMX for interactivity
- [x] **No SPA**: Avoids multi-server lifecycle complexity
- [x] **Server-Rendered**: Backend controls all UI state transitions
- [x] **HTMX Interactivity**: Dynamic updates without full page reloads
- [x] **Single Service**: No separate frontend build system required

#### Core UI Capabilities
- [x] **Task List View**: Server-rendered task dashboard with status filtering
- [x] **Evidence Bundle Interface**: Document and agent output presentation
- [x] **Task Completion Forms**: Structured input forms with validation
- [x] **Basic Reporting**: Progress tracking and audit trail visibility

#### Integration Requirements
- [ ] FastAPI backend API integration
- [ ] Real-time task status updates
- [ ] Document viewer for evidence review
- [ ] Audit trail visibility for compliance

### Pipeline Integration

#### Pipeline Trigger Mechanisms
- [ ] Task completion triggers state transitions
- [ ] Multiple task resolution for complex workflows
- [ ] Conditional progression based on task outcomes
- [ ] Failure propagation and workflow suspension

#### Workflow Orchestration
- [ ] Task dependency management
- [ ] Parallel task execution coordination
- [ ] Workflow versioning and rollback capabilities
- [ ] Performance monitoring and bottleneck detection

## Design Decisions (APPROVED)

1. **UI Technology Stack**: **FastAPI server-rendered HTML** (Jinja + HTMX)
   - **Rationale**: Avoids multi-server lifecycle instability; simplifies HITL workflows; faster iteration for single reviewer; backend governs all state
   - **Constraints**: HTMX for interactivity only; no separate frontend build; API remains reusable

2. **Assignment Strategy**: **Single reviewer model** for Phase 3
   - **Rationale**: Single human reviewer; no authentication complexity; simple identity tracking
   - **Constraints**: Dropdown/fixed reviewer selection; no multi-user workflows

3. **Evidence Persistence**: Reference-based approach with full audit trails
4. **Task Granularity**: Structured task definitions aligned with agent outputs

## Implementation Guidance

### Database Integration
- Task entity with lifecycle state tracking
- Evidence bundle storage and versioning
- Assignment audit trails and history
- Performance metrics and reporting queries

### API Endpoints
```python
# Task management endpoints
POST /api/v1/tasks/create
GET /api/v1/tasks/assigned/{actor_id}
PUT /api/v1/tasks/{task_id}/complete
GET /api/v1/evidence-bundles/{bundle_id}
```

### Workflow Integration
- PipelineStateMachine integration for transitions
- Agent run completion triggers task creation
- Task completion triggers pipeline advancement
- Failure handling and workflow recovery

## Acceptance Criteria

- [ ] Task lifecycle states fully defined and implemented
- [ ] Assignment model functional with audit trails
- [ ] Evidence bundles automatically assembled
- [ ] Minimal UI operational for task management
- [ ] Pipeline integration triggers working correctly
- [ ] Performance requirements met for human workflows
- [ ] Human reviewer approval obtained

---

**Status**: SPECIFICATION COMPLETE - Ready for P3.9 Implementation
**Approved**: FastAPI+HTMX UI + Single Reviewer Model (Dec 30, 2025)