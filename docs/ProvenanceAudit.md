# ProvenanceAudit.md  
**Provenance, Lineage, and Auditability Specification**

---

## 1. Purpose

This document defines the provenance, lineage, and audit requirements for all artifacts produced by the system, including:

- Documents
- Extracted text
- Diagrams and images
- OCR outputs
- Intermediate analytical results
- Draft claims
- Final claim sets

The goal is to ensure **litigation-grade traceability**, such that every claim element can be traced back to authoritative source material with a verifiable chain of custody.

This document specifies **what must be tracked**, **how relationships are modeled**, and **what evidence must be preserved**, without prescribing storage or implementation details.

---

## 2. Core Principles

### 2.1 Litigation-Grade Traceability

Every substantive output must support the question:

> “Where did this come from, who created it, under what rules, and based on what evidence?”

### 2.2 Non-Repudiation

Once recorded, provenance records are immutable. Corrections occur through **new records**, not mutation.

### 2.3 Evidence-Centric Design

Claims are treated as **legal assertions**, not text generation outputs. Provenance must support admissibility and expert testimony.

### 2.4 Human-in-the-Loop Accountability

All HITL interventions must be explicitly captured, including:
- Who approved
- What was changed
- Why it was changed
- What evidence was reviewed

---

## 3. Provenance Object Model (Conceptual)

### 3.1 Provenance Record

A provenance record represents the creation or transformation of an artifact.

**Required fields:**
- `provenance_id`
- `artifact_id`
- `artifact_type`
- `action_type` (create, transform, approve, reject, annotate)
- `timestamp_utc`
- `actor_type` (agent, human)
- `actor_id`
- `inputs[]` (artifact references)
- `outputs[]` (artifact references)
- `policy_context` (phase, ruleset version)
- `confidence_level` (if applicable)
- `notes`

---

### 3.2 Artifact Types (Non-Exhaustive)

- SourceDocument
- ExtractedText
- DiagramImage
- DiagramDescription
- OCRResult
- ClassificationLabel
- ClaimDraft
- ClaimRevision
- ClaimSet
- RiskAssessment
- HITLDecision

---

## 4. Lineage Graph

### 4.1 Directed Acyclic Graph (DAG)

All artifacts participate in a **lineage DAG** where:
- Nodes = artifacts
- Edges = provenance records

Cycles are forbidden.

### 4.2 Multi-Parent Support

Artifacts may derive from multiple inputs:
- Claims derived from multiple documents
- Diagrams reused across patents
- Text + diagram fusion outputs

---

## 5. Diagram & Image Provenance (Critical)

### 5.1 Diagrams as First-Class Evidence

Diagrams/images are treated as independent artifacts with their own provenance.

Each diagram must have:
- A stable `diagram_id`
- One or more source references
- A semantic description (human or agent generated)
- A classification state

---

### 5.2 Diagram Identity & Reuse

The system must support:

- **Canonical Diagrams**
  - Identical diagrams reused across documents
  - One authoritative description reused by reference

- **Duplicate Detection Outcomes**
  - `IDENTICAL_TO_CANONICAL`
  - `VARIANT_OF_CANONICAL`
  - `UNIQUE`
  - `IGNORED`

Each outcome must generate a provenance record.

---

### 5.3 Ignored Images

Images may be explicitly marked as ignored with a required reason:
- Decorative
- Logo
- Advertisement
- Non-technical
- Redundant context

Ignored images remain auditable but are excluded from claim support.

---

## 6. Claim Provenance Requirements

### 6.1 Claim Element Mapping

Each claim element must reference:
- Supporting text passages
- Supporting diagrams (if applicable)
- Negative constraints (what was avoided)

Mappings must be machine-readable and auditable.

---

### 6.2 Claim Revision History

Every claim revision must:
- Preserve the prior version
- Identify the reason for revision
- Identify the triggering analysis (e.g., prior art risk)

---

## 7. Risk & Validation Provenance

### 7.1 Risk Assessments

All risk scores must include:
- Inputs used
- Rules applied
- Agent identity
- Timestamp

### 7.2 Validation Failures

Failed validations are retained as evidence, not discarded.

---

## 8. Human-in-the-Loop (HITL) Audit Trail

### 8.1 Required HITL Records

For each HITL action:
- Task ID
- Artifact(s) reviewed
- Decision taken
- Rationale
- Time spent
- Confidence assessment

### 8.2 Legal Significance

HITL approvals are considered **expert confirmations** and must be traceable.

---

## 9. Phase Awareness

Each provenance record must include:
- Development phase (Phase 3+, etc.)
- Active governance ruleset
- Enforcement mode (advisory vs enforced)

This allows retrospective analysis of system maturity.

---

## 10. Export & Reporting Requirements

The system must be capable of producing:

- Claim-to-evidence reports
- Diagram reuse reports
- HITL intervention logs
- Full lineage graphs for a claim set

Export formats are implementation-defined but must preserve structure.

---

## 11. Out of Scope (This Document)

- Storage technology
- Database schema
- Performance optimization
- Visualization tooling

These are addressed in later design and implementation phases.

---

## 12. Success Criteria

This provenance system is considered successful if:

- Every claim can be defended with traceable evidence
- Diagram reuse is provable and consistent
- HITL decisions are auditable
- No artifact exists without lineage
- Litigation narratives can be reconstructed deterministically

---

**Status:** Draft — Design Authority  
**Phase Alignment:** Phase 2 (Contracts) → Phase 3 (Implementation)  
