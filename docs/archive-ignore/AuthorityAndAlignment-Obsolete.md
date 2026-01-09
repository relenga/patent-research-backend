# Phase 3 Design Gate — Authority and Alignment

**Purpose**: Establish clear document authority hierarchy and resolve overlaps between existing design documents and new Phase 3 specifications.

## Document Authority Hierarchy

### Execution Authority (Unchanging)
- **[BuildPlan.md](../BuildPlan.md)**: Sole authority for task existence, scope, and execution sequence
- **[AgentRules.md](../AgentRules.md)**: Governance, phase control, and agent behavior rules

### Design Context (Referenced for Constraints)
- **[PRD.md](../PRD.md)**: Product requirements and phase constraints
- **[SystemNarrative.md](../SystemNarrative.md)**: Business context and use cases
- **[CorpusModel.md](../CorpusModel.md)**: Corpus isolation rules and boundaries

### Implementation Guidance (New Phase 3 Authority)
- **Phase 3 Specifications**: Technical implementation details for P3.x tasks
- **[DevelopmentEnvironment.md](../DevelopmentEnvironment.md)**: Hardware and LLM integration guidance

## Authority Resolution

### Where Documents Overlap

#### Database Design
- **CorpusModel.md**: Defines corpus isolation **business rules**
- **DatabaseSchemaSpec.md**: Defines database **implementation patterns**
- **Resolution**: CorpusModel.md authoritative for business constraints; DatabaseSchemaSpec.md authoritative for technical implementation

#### Agent Behavior  
- **AgentResponsibilities.md**: Defines agent **boundaries and authorities**
- **AgentFrameworkSpec.md**: Defines agent **execution infrastructure**
- **Resolution**: AgentResponsibilities.md authoritative for what agents can do; AgentFrameworkSpec.md authoritative for how agents execute

#### Pipeline Execution
- **PipelineStateMachine.md**: Defines state machine **rules and transitions**
- **PipelineExecutionSpec.md**: Defines execution **mechanisms and failure handling**
- **Resolution**: PipelineStateMachine.md authoritative for business logic; PipelineExecutionSpec.md authoritative for technical implementation

#### Audit and Provenance
- **ProvenanceAudit.md**: Defines audit **requirements and compliance**
- **FailureModesSpec.md**: Defines audit **event generation during failures**
- **Resolution**: ProvenanceAudit.md authoritative for what must be audited; FailureModesSpec.md authoritative for how audit events are generated

## Cross-Reference Requirements

### Design Documents → Phase 3 Specs
All Phase 3 specifications must reference and align with:
- Business constraints from design documents
- Technical patterns established in Phase 2
- Compliance requirements from audit specifications

### Phase 3 Specs → Design Documents
All specifications must declare:
- Which design document provides business authority
- How technical implementation serves business requirements  
- Where implementation decisions extend beyond business constraints

## Consistency Verification

### Required Alignments
- [ ] **Corpus boundaries** consistent between CorpusModel.md and CorpusEnforcementSpec.md
- [ ] **Agent authorities** consistent between AgentResponsibilities.md and AgentFrameworkSpec.md  
- [ ] **State machine rules** consistent between PipelineStateMachine.md and PipelineExecutionSpec.md
- [ ] **Audit requirements** consistent between ProvenanceAudit.md and all specs generating events
- [ ] **Task workflows** consistent between TaskManagementSystemStatus.md and HITLTaskSpec.md

### Conflict Resolution Process
1. **Business vs Technical**: Business requirements (design docs) override technical preferences (specs)
2. **Spec vs Spec**: Higher-level architectural decisions (DatabaseSchemaSpec.md) constrain component specs
3. **Unclear Authority**: Escalate to human reviewer for authoritative decision

---

**Design Gate Requirement**: All cross-references and authority declarations must be verified before Phase 3 implementation authorization.