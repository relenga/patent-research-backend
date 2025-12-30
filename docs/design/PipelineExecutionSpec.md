# Pipeline Execution Specification

**Status**: APPROVED - PostgreSQL and Diagram Automation Decisions Confirmed (Dec 30, 2025)  
**Authority**: Technical implementation of PipelineStateMachine.md business logic for P3.2 Pipeline State Machine Execution  
**State Machine Authority**: [PipelineStateMachine.md](../../PipelineStateMachine.md) - AUTHORITATIVE state definitions and transition rules
**HITL Integration**: [HITLTaskSpec.md](./HITLTaskSpec.md) - Human task integration with pipeline states
**Database Schema**: [DatabaseSchemaSpec.md](./DatabaseSchemaSpec.md) - Database implementation of state machine

## Authority Relationship

**PipelineStateMachine.md defines WHAT** (states, transitions, business rules)
**This specification defines HOW** (execution mechanics, triggers, failure handling)
**HITLTaskSpec.md defines WHEN** (human intervention points and task creation)

**State Compliance**: All execution mechanics must implement PipelineStateMachine.md state transitions exactly as defined.

## Purpose

Defines pipeline execution mechanics including transition triggers, failure mapping, idempotency rules, and audit/provenance requirements for document processing workflows.

## Required Content (Minimum Specification)

## State Machine Compliance (MANDATORY)

**All execution mechanics must implement PipelineStateMachine.md definitions exactly**:

✅ **REQUIRED State Implementations**:
- Document states: INGESTED → NORMALIZED → TEXT_EXTRACTED → IMAGES_EXTRACTED → READY
- Image states: IMAGE_EXTRACTED → HASHED → DUPLICATE_CHECKED → READY
- Failure states: ANY → BLOCKED (HITL) or FAILED (fatal)
- Administrative states: Manual overrides and emergency controls

❌ **FORBIDDEN Implementations**:
- State transitions not defined in PipelineStateMachine.md
- Implicit or undocumented state changes
- Bypassing state validation or audit requirements
- Custom states without PipelineStateMachine.md authority

**Validation**: All state transitions must validate against PipelineStateMachine.md rules before execution.

### Transition Trigger Mechanisms

#### Automatic Triggers
- [ ] **Agent Completion**: Agent run success triggers next pipeline step
- [ ] **Time-based**: Scheduled transitions for time-sensitive processes
- [ ] **Condition-based**: Business rule evaluation triggers
- [ ] **External Event**: API calls or system events trigger transitions

#### Human-Authorized Triggers
- [ ] **HITL Task Completion**: Human approval triggers pipeline advancement
- [ ] **Manual Override**: Project manager manual state transitions
- [ ] **Emergency Controls**: Immediate pipeline suspension/recovery
- [ ] **Batch Processing**: Bulk document state transitions

### Failure Mapping to States

#### Failure Categories
- [ ] **Transient Failures**: Temporary resource or network issues
- [ ] **Validation Failures**: Schema or business rule violations
- [ ] **Agent Failures**: LLM errors or boundary violations
- [ ] **System Failures**: Infrastructure or dependency failures

#### State Mapping Rules
- [ ] **PROCESSING_FAILED**: Agent execution or validation failures
- [ ] **VALIDATION_REQUIRED**: Output quality issues requiring review
- [ ] **ERROR_INVESTIGATION**: System failures requiring diagnosis
- [ ] **SUSPENDED**: Corpus violations or compliance issues

#### Recovery Procedures
- [ ] Automatic retry for transient failures
- [ ] Manual intervention triggers for systematic failures
- [ ] Rollback procedures for corrupted states
- [ ] Escalation procedures for unrecoverable failures

### Idempotency Rules

#### Operation Idempotency
- [ ] **State Transitions**: Repeated transition calls are safe
- [ ] **Agent Executions**: Duplicate runs produce consistent results
- [ ] **Audit Events**: Event deduplication prevents double-logging
- [ ] **Pipeline Steps**: Step re-execution produces identical outcomes

#### Consistency Guarantees
- [ ] **Transaction Boundaries**: Atomic state and data updates
- [ ] **Concurrent Safety**: Multiple pipeline execution coordination
- [ ] **Partial Failure Recovery**: Consistent state after interruptions
- [ ] **Version Consistency**: Document version alignment with states

### Implementation Validation Requirements

**BuildPlan Reference**: [BuildPlan.md P3.2](../../BuildPlan.md) - Implementation task definitions and acceptance criteria

**Mandatory Implementation Checks**:
- ✅ All PipelineStateMachine.md state transitions implemented exactly
- ✅ State validation occurs before every transition attempt
- ✅ HITL task generation follows HITLTaskSpec.md requirements
- ✅ Audit trail captures all state changes with timestamps and triggers
- ✅ Emergency controls allow manual override with proper authorization
- ✅ No custom states or transitions outside PipelineStateMachine.md authority

**BuildPlan.md P3.2 Compliance**:
- Pipeline step runner framework implements trigger mechanisms defined here
- Failure detection maps to state machine failure paths exactly
- Progress tracking exposes state machine states through specified interfaces
- Manual override capabilities match administrative controls defined here

**Cross-Specification Integration** (APPROVED APPROACH):

#### OCR + Human Correction Workflow
- [x] **OCR Assistance**: Automated text extraction from diagram images
- [x] **Human Validation**: All diagram descriptions require human approval
- [x] **Canonical Reuse**: Approved diagrams may reference canonical descriptions
- [x] **Audit Completeness**: Ignored diagrams remain auditable but excluded from reasoning
- [x] **Legal Compliance**: No full automation for legally critical patent diagrams

#### Pipeline Integration
- [x] **OCR Processing Step**: Automated diagram text extraction with quality scoring
- [x] **Human Review Task**: HITL task generated for diagram description approval
- [x] **Canonical Storage**: Approved descriptions stored for reuse validation
- [x] **Provenance Tracking**: Complete audit trail for diagram processing decisions

### Audit & Provenance Rules per Transition

#### Mandatory Audit Events
- [ ] **STATE_TRANSITION**: From/to states with triggering actor
- [ ] **PIPELINE_STEP_START**: Step initiation with parameters
- [ ] **PIPELINE_STEP_COMPLETE**: Step completion with outputs
- [ ] **FAILURE_OCCURRENCE**: Failure details and recovery actions

#### Provenance Tracking
- [ ] **Activity Lineage**: Step-by-step processing history
- [ ] **Entity Evolution**: Document transformation tracking
- [ ] **Agent Attribution**: Which agents contributed to outcomes
- [ ] **Human Attribution**: HITL task completion attribution

#### Context Preservation
- [ ] Full input context capture for each transition
- [ ] Configuration and parameter logging
- [ ] Environmental state at time of execution
- [ ] Performance metrics and timing data

## Design Decisions (APPROVED)

1. **Execution Model**: Asynchronous pipeline execution with PostgreSQL persistence
   - **Rationale**: PostgreSQL provides reliable transaction boundaries and concurrent safety
   - **Constraints**: Single-node deployment with local database

2. **Failure Strategy**: Graceful degradation with comprehensive audit trails
3. **Concurrency Control**: PostgreSQL optimistic locking for state transitions
4. **State Persistence**: Real-time state synchronization with audit event generation
5. **Diagram Automation**: **OCR + Human Correction** (no full automation)
   - **Rationale**: Patent diagrams are legally critical; OCR assists but human validation required
   - **Constraints**: All descriptions require approval; canonical reuse allowed when explicitly approved

## Implementation Guidance

### Core Execution Engine
```python
# Pipeline execution interfaces
class PipelineExecutor:
    async def execute_transition(document_id: str, trigger: Trigger) -> bool
    async def handle_failure(failure: PipelineFailure) -> RecoveryAction

class StateManager:
    async def transition_state(document_id: str, from_state: State, to_state: State)
    async def validate_transition(document_id: str, transition: Transition) -> bool
```

### Integration Points
- Database transaction management for atomic state changes
- Agent framework integration for step execution
- HITL task system integration for human-authorized transitions
- Logging and audit systems for comprehensive event capture

### Performance Considerations
- Pipeline execution queue management
- Resource allocation for concurrent document processing
- Monitoring and alerting for pipeline bottlenecks
- Performance metrics collection and analysis

## Acceptance Criteria

- [ ] All transition trigger mechanisms implemented
- [ ] Failure mapping comprehensive and tested
- [ ] Idempotency rules enforced throughout system
- [ ] Audit and provenance capture complete
- [ ] Performance requirements met for document throughput
- [ ] Integration with other system components verified
- [ ] Human reviewer approval obtained

---

**Status**: SPECIFICATION COMPLETE - Ready for P3.2 Implementation
**Approved**: PostgreSQL + OCR+Human Diagram Processing (Dec 30, 2025)