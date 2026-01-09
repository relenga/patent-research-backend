# Agent Responsibilities — Governed Patent Intelligence Backend

**Authority**: Defines agent-specific corpus access permissions and operational boundaries
**Corpus Business Rules**: [CorpusModel.md](CorpusModel.md) - AUTHORITATIVE corpus definitions and access matrix
**Technical Enforcement**: [CorpusEnforcementSpec.md](design/phase-3-specs/CorpusEnforcementSpec.md) - Implementation of corpus restrictions

## Document Authority

This document defines **what each agent is allowed to do**, what it **must not do**, and **which corpora each agent may access** per CorpusModel.md business rules.

**Corpus Compliance**: All agent corpus access must comply with CorpusModel.md access matrix. CorpusEnforcementSpec.md implements technical enforcement of these rules.

This document governs **authority boundaries and decision rights**, not implementation details.

If there is a conflict, the following precedence applies:
1. AgentRules.md (authoritative governance)
2. BuildPlan.md
3. This document

---

## Corpus Access Compliance (MANDATORY)

**All agents must comply with [CorpusModel.md](CorpusModel.md) access matrix**:

✅ **AUTHORIZED Corpus Operations**:
- Classification Agent: Access all corpora for document assignment
- Prior Art Analysis Agent: Access Adversarial corpus for risk analysis ONLY
- Claim Drafting Agent: Access Open Patent corpus ONLY for claim drafting
- Product Mapping Agent: Access Product corpus for evidence mapping ONLY

❌ **FORBIDDEN Corpus Operations**:
- ANY agent accessing Adversarial corpus for claim language
- Claim Drafting Agent accessing ANY corpus except Open Patent
- ANY cross-corpus contamination in agent inputs or outputs

**Enforcement**: CorpusEnforcementSpec.md implements runtime validation of these restrictions.

## General Rules (Non-Negotiable)

- Agents may **only** perform actions explicitly listed here
- Any ambiguity must be resolved conservatively
- UI-editable prompts are **parameterized inputs**, not instructions
- Legal standards, claim validity rules, and risk thresholds are **never user-editable**
- Agents do **not** self-authorize scope expansion
- All agent actions are provenance-tracked

---

## UI-Editable Prompt Enforcement (Critical)

When an agent allows UI-editable input:

- Inputs must bind to **predefined prompt templates**
- Editable parameters are limited to:
  - focus areas
  - drafting emphasis
  - verbosity
  - stylistic preferences
  - exclusions (what to avoid discussing)

UI-editable prompts may **NOT**:
- Define legal standards
- Override statutory requirements
- Change patentability criteria
- Alter risk scoring rules
- Introduce new objectives

All prompt edits are:
- Logged
- Versioned
- Auditable

---

## Agent Responsibility Matrix

| Agent | Purpose | Corpus Access | UI-Editable Prompt | Explicit Restrictions |
|-----|--------|---------------|-------------------|----------------------|
| Research Agent | Acquire documents (patents, OA/IPR, prior art, product docs) | 🔄 ALL (assignment only) | ✅ Yes (targets, sources) | Cannot interpret, evaluate, or summarize |
| Document Ingestion Agent | Normalize, extract text/images, OCR | 🔄 ALL (processing only) | ❌ No | No interpretation or classification |
| Classification Agent | Assign `doc_type`, `source_type`, corpus membership | 🔄 ALL (assignment only) | ❌ No | No drafting or reasoning |
| Prior Art Analysis Agent | Identify conflicts, novelty risks | 🔴 Adversarial ONLY | ✅ Yes (analysis emphasis only) | **NEVER supplies claim language** |
| Office Action / IPR Analysis Agent | Extract examiner / PTAB reasoning | 🔴 Adversarial ONLY | ✅ Yes | No claim generation |
| Product Mapping Agent | Map product features to disclosures | 🔵 Product ONLY | ✅ Yes | No claim drafting |
| Claim Drafting Agent | Draft claims grounded **only** in open patent corpus | 🟢 Open Patent ONLY | ✅ Yes (limited) | **CorpusModel.md compliance mandatory** |
| Claim Risk Evaluation Agent | Score §102/103/IPR risk | 🔴 Adversarial ONLY | ❌ No | Fixed rubric only |
| Consistency / Support Agent | Verify claim support in spec | 🟢 Open Patent ONLY | ❌ No | No rewriting or optimization |
| Revision / Optimization Agent | Revise claims based on feedback | 🟢 Open Patent ONLY | ❌ No | No freeform creativity |
| Task Generation Agent (HITL) | Create human review tasks | 🔄 Per task scope | ❌ No | **Never makes decisions or approvals** |
| Audit / Provenance Agent | Maintain lineage and evidence | 🔄 ALL (audit only) | ❌ No | No analysis or judgment |
| Orchestrator / Supervisor Agent | Control sequencing and stopping | ❌ No corpus access | ❌ No | No content generation |
| User Interaction Agent | Translate user intent into structured actions | ❌ No corpus access | ✅ Yes (light) | No analysis or drafting |

**Corpus Legend**:
- 🟢 Open Patent: Claim drafting authorized per CorpusModel.md
- 🔴 Adversarial: Risk analysis only – NO claim language per CorpusModel.md  
- 🔵 Product: Evidence mapping only per CorpusModel.md
- 🔄 Multiple: Access per specific operational need with restrictions
- ❌ No corpus access: System/orchestration agents only

---

## Prior Art Usage Boundary (Clarified)

- Prior art **may be analyzed** to:
  - identify risk
  - highlight avoidance constraints
  - flag vulnerabilities
- Prior art **may NOT**:
  - supply claim language
  - be cited as affirmative support
  - be used as drafting input

Claims must be grounded **exclusively** in the open patent corpus.

---

## HITL Task Generation Boundary (Clarified)

The Task Generation Agent:

**May:**
- Detect when human input is required
- Package evidence and context
- Create structured tasks (verify, approve, annotate)

**May NOT:**
- Approve or reject claims
- Resolve ambiguity
- Choose outcomes
- Score correctness

All outcomes are decided by humans and recorded as provenance.

---

## Diagram & Image Responsibilities (Alignment)

- Agents may identify duplicate or near-duplicate diagrams
- Only humans may:
  - approve canonical reuse
  - mark diagrams as IGNORED
- IGNORED diagrams:
  - remain in lineage
  - are excluded from retrieval and claim support
  - remain visible in audit reports

---

## Authority Statement

This document is authoritative for **agent behavior and boundaries**.

Violations constitute governance failures and require rollback per AgentRules.md.

---

## Agent-to-BuildPlan Task Mapping

| Agent | Primary BuildPlan Task | Secondary Tasks |
|-------|----------------------|----------------|
| Research Agent | P3.2 Document Ingestion | P3.5 Pipeline orchestration |
| Classification Agent | P3.4 Corpus Construction | P3.5 Pipeline orchestration |
| Prior Art Analysis Agent | P3.7 Claim Analysis Agents | P3.8 Claim Drafting System |
| Claim Drafting Agent | P3.8 Claim Drafting System | P3.9 HITL Task System |
| Task Generation Agent | P3.9 HITL Task System | P3.5 Pipeline orchestration |
| Orchestrator Agent | P3.5 Pipeline Orchestration | All phases coordination |

**Note:** No agent may operate outside their assigned BuildPlan tasks.
