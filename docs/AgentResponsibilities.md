# Agent Responsibilities — Governed Patent Intelligence Backend

**Authority**: Defines agent-specific corpus access permissions and operational boundaries
**Corpus Business Rules**: [CorpusModel.md](CorpusModel.md) - AUTHORITATIVE corpus definitions and access matrix
**Technical Enforcement**: [CorpusEnforcementSpec.md](design/CorpusEnforcementSpec.md) - Implementation of corpus restrictions

## Document Authority

This document defines **what each agent is allowed to do**, what it **must not do**, and **which corpora each agent may access** per CorpusModel.md business rules.

---

## Prompt Registry & Parameter Schema (UI-Editable Enforcement)

**CRITICAL ENFORCEMENT**: All UI-editable agent prompts must conform to **Prompt Registry + Parameter Schema** architecture:

### Prompt Registry Structure
- **Base Template**: Fixed legal/rubric rules and constraints (non-editable)
- **Parameter Schema**: Defined editable parameters with validation rules
- **Style/Focus Parameters**: User-controllable within legal bounds
- **Constraint Inheritance**: All prompts inherit phase discipline and corpus rules

### UI-Editable Parameters (ALLOWED)
- **Focus Areas**: Emphasis on specific claim types or patent sections
- **Drafting Style**: Verbosity, technical depth, explanatory detail
- **Scope Preferences**: Broad vs. narrow claim scope guidance
- **Avoidance Emphasis**: Specific prior art patterns to avoid
- **Exclusions**: Topics or approaches to de-emphasize

### UI-NON-Editable Elements (FORBIDDEN)
- **Legal Standards**: Patentability requirements, statutory criteria
- **Corpus Access Rules**: Which corpora agents may access
- **Risk Scoring Rubrics**: Objective assessment criteria  
- **Phase Discipline Rules**: What may be implemented in current phase
- **Audit Requirements**: Provenance tracking and evidence standards

### Implementation Requirements
- **Parameter Validation**: All UI inputs validated against parameter schema
- **Audit Logging**: All prompt modifications logged with user identity and timestamp
- **Version Control**: Prompt changes tracked with rollback capability
- **Legal Review**: Prompt templates reviewed for professional responsibility compliance

---

## Agent Responsibility Matrix (Complete Rewrite)

### Research Agent
**Primary Function**: Document acquisition from external sources
- **Corpus Access**: 🔄 ALL (for assignment purposes only)
- **Allowed Actions**:
  - USPTO patent database queries
  - Google Patents API integration (Phase 4+)
  - Office Action/IPR document retrieval
  - Product documentation acquisition
  - Source validation and metadata extraction
- **UI-Editable Prompts**: ✅ Search targets, source priorities, acquisition scope
- **Explicit Restrictions**:
  - No document interpretation or analysis
  - No corpus classification decisions (assignment only)
  - No content generation or summarization
- **Output**: Raw documents with source metadata for downstream processing

### Document Classification Agent  
**Primary Function**: Document type and corpus assignment
- **Corpus Access**: 🔄 ALL (for classification purposes only)
- **Allowed Actions**:
  - Document type detection (patent, prior_art, office_action, product_doc)
  - Source type validation (manual_upload, research_agent)
  - Initial corpus assignment per CorpusModel.md rules
  - Metadata extraction and normalization
- **UI-Editable Prompts**: ❌ None (objective classification only)
- **Explicit Restrictions**:
  - No content analysis beyond classification
  - No claim drafting or language generation
  - Classification decisions must follow CorpusModel.md rules exactly
- **Output**: Structured classification labels with confidence scores

### Prior Art Analysis Agent
**Primary Function**: Risk analysis and avoidance reasoning
- **Corpus Access**: 🔴 Adversarial ONLY (prior art, OA, IPR documents)
- **Allowed Actions**:
  - Novelty risk identification (§102 analysis)
  - Obviousness pattern detection (§103 analysis)
  - Examiner reasoning extraction from Office Actions
  - IPR invalidity argument analysis
  - Claim vulnerability assessment
- **UI-Editable Prompts**: ✅ Analysis emphasis, risk scoring focus, avoidance priorities  
- **Explicit Restrictions**:
  - **NEVER supplies claim language or positive claim support**
  - No access to Open Patent Corpus for claim drafting
  - Risk analysis only - no claim optimization suggestions
  - May not override CorpusModel.md adversarial corpus constraints
- **Output**: Risk assessments and avoidance recommendations (no claim text)

### Product Mapping Agent
**Primary Function**: Product-to-disclosure evidence mapping
- **Corpus Access**: 🔵 Product Corpus ONLY + 🟢 Open Patent ONLY (for mapping)
- **Allowed Actions**:
  - Product feature identification and categorization
  - Technical specification analysis
  - Product-to-patent disclosure mapping
  - Evidence bundle preparation for read-on analysis
  - Infringement theory development support
- **UI-Editable Prompts**: ✅ Mapping focus, technical depth, evidence priorities
- **Explicit Restrictions**:
  - No claim drafting or language generation
  - No prior art or Office Action analysis (different corpus)
  - Evidence collection only - no legal conclusions
- **Output**: Product-to-disclosure mapping evidence (structured)

### Claim Drafting Agent
**Primary Function**: Claim generation grounded exclusively in Open Patent Corpus
- **Corpus Access**: 🟢 Open Patent Corpus ONLY
- **Allowed Actions**:
  - Independent claim drafting from patent specification
  - Dependent claim generation based on independent claims
  - Claim scope optimization within specification boundaries
  - Support verification against patent disclosure
  - Alternative claim embodiment generation
- **UI-Editable Prompts**: ✅ LIMITED to style/scope/focus parameters within Prompt Registry
- **Explicit Restrictions**:
  - **MANDATORY CorpusModel.md compliance**: Open Patent Corpus ONLY
  - No access to adversarial or product corpora for claim generation
  - UI edits limited to predefined parameters (no freeform legal editing)
  - All claim elements must trace to Open Patent Corpus support
- **Output**: Draft claims with full Open Patent Corpus lineage

### Support Verification Agent  
**Primary Function**: Claim support validation against patent specification
- **Corpus Access**: 🟢 Open Patent Corpus ONLY
- **Allowed Actions**:
  - Claim element support verification
  - Written description compliance checking
  - Enablement requirement validation
  - Best mode disclosure verification
  - Indefiniteness analysis (clarity checking)
- **UI-Editable Prompts**: ❌ None (objective verification only)
- **Explicit Restrictions**:
  - No claim rewriting or optimization
  - Support verification only - no drafting assistance
  - Fixed verification rubric (no UI customization)
- **Output**: Support verification reports with specific citation mapping

### Task Generation Agent (HITL)
**Primary Function**: Human-in-the-loop workflow coordination  
- **Corpus Access**: 🔄 Per task scope (varies by task type)
- **Allowed Actions**:
  - HITL task detection and trigger identification
  - Evidence bundle assembly for human review
  - Task metadata creation (priority, context, requirements)
  - Human interface preparation and data marshaling
  - Task completion workflow coordination
- **UI-Editable Prompts**: ❌ None (objective task generation only)
- **Explicit Restrictions**:
  - **NEVER makes decisions or approvals** (human authority only)
  - No outcome determination or result evaluation
  - Task creation only - no task resolution
  - Cannot override human decisions or bypass HITL requirements
- **Output**: Structured HITL tasks with complete evidence context

### Audit & Provenance Agent
**Primary Function**: Lineage tracking and evidence chain maintenance
- **Corpus Access**: 🔄 ALL (audit purposes only - no content generation)
- **Allowed Actions**:
  - Provenance record creation and linking
  - Lineage graph maintenance and validation  
  - Evidence chain verification and audit trail generation
  - Compliance reporting and audit bundle preparation
  - Immutable record preservation and integrity checking
- **UI-Editable Prompts**: ❌ None (objective audit only)
- **Explicit Restrictions**:
  - No content analysis, judgment, or interpretation
  - No decision-making or approval authority
  - Audit trail integrity must never be compromised
  - Read-only access for audit purposes
- **Output**: Provenance records and audit reports (structured, immutable)

### Orchestrator/Supervisor Agent
**Primary Function**: Pipeline coordination and agent boundary enforcement
- **Corpus Access**: ❌ None (coordination only)
- **Allowed Actions**:
  - Agent execution sequencing and workflow control
  - Corpus access rule enforcement and violation detection
  - Pipeline state management and transition control
  - Error handling and recovery workflow coordination
  - Resource allocation and agent boundary management
- **UI-Editable Prompts**: ❌ None (system orchestration only)  
- **Explicit Restrictions**:
  - No content generation or analysis
  - No corpus access for any content purposes
  - Cannot override agent corpus restrictions or CorpusModel.md rules
  - System coordination only - no business logic
- **Output**: System coordination events and enforcement alerts

---

## Corpus Access Legend

- **🟢 Open Patent**: Authorized for claim drafting per CorpusModel.md
- **🔴 Adversarial**: Risk analysis ONLY - NO claim language per CorpusModel.md  
- **🔵 Product**: Evidence mapping ONLY per CorpusModel.md
- **🔄 Multiple/Scoped**: Access per specific operational need with restrictions
- **❌ No Access**: System/orchestration agents only

---

## Cross-Corpus Contamination Prevention

**CRITICAL RULE**: No agent may combine corpus access for content generation:

- **Claim Drafting Agent**: Open Patent ONLY - no adversarial or product input
- **Prior Art Analysis Agent**: Adversarial ONLY - no claim drafting capability  
- **Product Mapping Agent**: Product + Open Patent for mapping ONLY - no claim generation
- **All Other Agents**: Single corpus or orchestration/audit roles only

**Violation Detection**: Orchestrator Agent monitors and blocks cross-corpus violations with immediate alert generation.

---

## HITL Decision Authority (Clarified)

**Human Authority Is Absolute**:
- All agent outputs are **recommendations only**
- Human decisions are **authoritative and final**
- Agent recommendations cannot override human judgment
- All human decisions are **logged with full provenance**
- HITL task outcomes are **immutable once human-approved**

**Agent Limitations**:
- Task Generation Agent creates tasks but **never approves outcomes**
- All agents **suggest and recommend only** 
- **No agent has decision-making authority** over claim acceptance, diagram interpretation, or corpus assignment overrides

---

## Diagram & Image Agent Responsibilities (Alignment)

**Duplicate Detection**: Agents may identify potential duplicates using perceptual hashing
**Human Decision Required**: Only humans may approve canonical reuse, mark diagrams IGNORED, or resolve near-duplicate ambiguity
**IGNORED Diagram Handling**: 
- Remains in full lineage with audit trail
- Excluded from retrieval and claim support by default
- Visible in audit reports and provenance tracking
- Human rationale required and immutable

**Cross-Corpus Diagram Reuse**: Most restrictive parent corpus rule applies (per CorpusModel.md)

---

## Enforcement & Monitoring

- **Real-time Monitoring**: All agent actions monitored for corpus compliance
- **Violation Alerts**: Immediate notifications for any boundary violations  
- **Audit Trail**: Complete agent action history with corpus access logging
- **Human Override Authority**: Project Manager can override agent restrictions with justification
- **Compliance Reporting**: Regular corpus access compliance verification and reporting

This specification ensures strict agent boundary enforcement while maintaining complete auditability and human oversight authority.