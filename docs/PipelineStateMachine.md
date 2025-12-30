# Pipeline State Machine — AUTHORITATIVE STATE DEFINITIONS

**Authority**: SINGLE AUTHORITY for all pipeline state definitions and transition rules
**Execution Implementation**: [PipelineExecutionSpec.md](design/phase-3-specs/PipelineExecutionSpec.md) (execution mechanics)
**Implementation Tasks**: [BuildPlan.md P3.2](BuildPlan.md#p32-pipeline-state-machine-execution) (execution requirements)

## Document Authority

This document defines **what pipeline states exist and when transitions occur**, providing the business logic that governs all pipeline execution. Other documents implement these rules:

- **PipelineExecutionSpec.md**: HOW to technically implement these state transitions  
- **BuildPlan.md P3.2**: WHAT implementation tasks are required
- **HITLTaskSpec.md**: HOW human tasks integrate with pipeline states
- **DatabaseSchemaSpec.md**: Database schema supporting these state definitions

## Purpose

This document defines the **document processing pipeline and state machine** governing how documents, text, images, and diagrams flow through the system.

It specifies:
- Lifecycle states
- Transition rules
- Failure handling
- Human-in-the-Loop (HITL) escalation
- Explicit handling of **images and diagrams as first-class entities**

This document defines **structure and behavior expectations only**.  
Implementation details belong to Phase 3+.

---

## Design Principles

1. **Deterministic Progression**
   - Every entity progresses through explicit states
   - No implicit transitions

2. **Separation of Concerns**
   - Documents, text blocks, images, and diagrams have distinct lifecycles
   - Shared lineage links them

3. **Image/Diagram Elevation**
   - Images are not secondary artifacts
   - Diagrams provide evidence preparation for patent analysis and product mapping

4. **Reuse Over Redundancy**
   - Identical diagrams should share canonical descriptions
   - Duplicate effort is avoided

5. **Human Escalation Where Necessary**
   - OCR and diagram interpretation require HITL
   - Decisions are auditable and repeatable

---

## Entity Types Governed by the Pipeline

| Entity Type | Description |
|------------|------------|
| Document | Source artifact (patent, OA, product doc, legal text) |
| TextBlock | Extracted textual content |
| Image | Raw embedded image (figure, diagram, photo) |
| Diagram | Interpreted technical image with semantic meaning |
| DiagramDescription | Canonical textual explanation of a diagram |
| LineageRecord | Provenance linkage between entities |
| Task | Human review or intervention request |

---

## High-Level Pipeline Stages

1. Acquisition
2. Normalization
3. Extraction
4. Image Isolation
5. Duplicate Detection
6. Interpretation (OCR + Vision)
7. Validation (Automated + HITL)
8. Canonicalization
9. Corpus Assignment
10. Ready for Analysis

Manual uploads and research-agent acquisitions enter the pipeline identically after registration. All downstream processing is uniform and source-agnostic.


---

## Document State Machine

### Document States

| State | Meaning |
|-----|--------|
| INGESTED | Document identified and registered |
| NORMALIZED | Format standardized |
| TEXT_EXTRACTED | Text successfully extracted |
| IMAGES_EXTRACTED | Images isolated |
| PARTIALLY_PROCESSED | Some entities pending review |
| READY | All required components complete |
| BLOCKED | Awaiting HITL or external decision |
| FAILED | Processing failed irrecoverably |

---

## Image / Diagram State Machine (Elevated)

### Image States

| State | Meaning |
|------|--------|
| IMAGE_EXTRACTED | Image isolated from document |
| HASHED | Perceptual/hash fingerprint generated |
| DUPLICATE_CHECKED | Compared against canonical registry |
| DUPLICATE_LINKED | Matched to existing canonical image |
| UNIQUE | No prior match found |
| IGNORED | Explicitly marked as non-semantic |
| NEEDS_INTERPRETATION | Requires OCR / vision analysis |
| INTERPRETED | Textual/structural meaning extracted |
| NEEDS_HITL | Requires human confirmation |
| CANONICALIZED | Approved diagram description exists |
| READY | Eligible for downstream reasoning (corpus constraints apply) |

---

## Duplicate & Reuse Handling (Critical)

### Duplicate Detection Rules

- Every image produces:
  - Perceptual hash
  - Structural embedding
- Comparison against **Diagram Canonical Registry**

### Possible Outcomes

| Outcome | Action |
|-------|-------|
| Identical | Link to existing canonical diagram |
| Near-duplicate | HITL decision required |
| Unique | New diagram interpretation required |
| Non-semantic | Mark as IGNORED |

---

## Ignore Semantics (Required)

Images may be explicitly marked as **IGNORED** for reasons including:

- Logos
- Advertisements
- Decorative images
- Non-technical photos
- Repeated boilerplate figures

Ignored images:
- Remain in lineage
- Are excluded from evidence preparation
- Are auditable decisions

### Ignored Image Handling (Explicit Rules)

Images marked as **IGNORED**:

- Are stored with a required `ignored_reason`
- Remain fully represented in lineage and audit trails
- Are excluded from:
  - RAG retrieval
  - Evidence preparation for claim analysis
  - Diagram-to-claim mapping
- Remain visible in:
  - Provenance reports
  - Diagram registries
  - HITL review history

Ignored images are never deleted and never silently excluded.


---

## Diagram Interpretation Flow

1. OCR (text inside diagram)
2. Vision model structure analysis
3. Caption + reference extraction
4. Semantic description draft
5. Confidence scoring

### Escalation Conditions (HITL)

- Low OCR confidence
- Ambiguous technical meaning
- Potential claim-critical diagram
- Near-duplicate uncertainty

---

## Human-in-the-Loop Tasks

| Task Type | Trigger |
|---------|--------|
| Verify OCR | Low confidence text |
| Approve duplicate | Near-match detected |
| Write diagram description | Complex technical figure |
| Approve canonicalization | Diagram reused across corpus |
| Mark ignore | Non-semantic image |

All HITL actions:
- Create auditable Task records
- Require explicit human decision
- Feed back into pipeline state

---

## State Transition Rules (AUTHORITATIVE)

**Implementation Authority**: PipelineExecutionSpec.md must implement these exact transition rules

### Document State Transitions
- INGESTED → NORMALIZED (automatic)
- NORMALIZED → TEXT_EXTRACTED (automatic)
- TEXT_EXTRACTED → IMAGES_EXTRACTED (automatic)
- IMAGES_EXTRACTED → PARTIALLY_PROCESSED (if images pending)
- IMAGES_EXTRACTED → READY (if no images or all images complete)
- PARTIALLY_PROCESSED → READY (when all dependencies complete)
- ANY → BLOCKED (awaiting HITL)
- ANY → FAILED (fatal error)

### Image/Diagram State Transitions
- IMAGE_EXTRACTED → HASHED (automatic)
- HASHED → DUPLICATE_CHECKED (automatic)
- DUPLICATE_CHECKED → DUPLICATE_LINKED (if identical match)
- DUPLICATE_CHECKED → UNIQUE (if no match)
- DUPLICATE_CHECKED → BLOCKED (if near-duplicate, requires HITL)
- UNIQUE → NEEDS_INTERPRETATION (automatic)
- NEEDS_INTERPRETATION → INTERPRETED (OCR + vision processing)
- INTERPRETED → CANONICALIZED (automatic or HITL approval)
- CANONICALIZED → READY (automatic)
- ANY → IGNORED (human decision)
- ANY → FAILED (fatal error)

**Trigger Types** (implemented by PipelineExecutionSpec.md):
- **Automatic**: Agent completion or business rule evaluation
- **HITL**: Human task completion triggers transition
- **Manual**: Administrative override
- **External**: API calls or system events

## State Transition Rules (Examples)

- IMAGE_EXTRACTED → HASHED
- HASHED → DUPLICATE_CHECKED
- DUPLICATE_CHECKED → DUPLICATE_LINKED
- DUPLICATE_CHECKED → UNIQUE
- UNIQUE → NEEDS_INTERPRETATION
- NEEDS_INTERPRETATION → INTERPRETED
- INTERPRETED → CANONICALIZED
- CANONICALIZED → READY
- ANY → BLOCKED (awaiting HITL)
- ANY → FAILED (fatal error)

---

## Failure & Recovery Semantics

- Failures are localized to entities
- Document may proceed while images block
- Retry allowed only for:
  - OCR
  - Vision interpretation
- Fatal failures require human resolution

---

## Pipeline Guarantees

When an entity reaches **READY**:
- All dependencies are satisfied
- Provenance links exist
- Decisions are auditable
- Reuse is maximized
- No silent assumptions remain

**Important:** Pipeline readiness does not grant claim-support authority. Downstream agents must obey corpus usage rules defined in CorpusModel.md.

---

## Relationship to Other Documents

| Document | Relationship |
|--------|-------------|
| PRD.md | Defines *what* is required |
| SystemNarrative.md | Explains *why* |
| CorpusModel.md | Defines *where knowledge may be used* |
| AgentResponsibilities.md | Defines *who acts* |
| ProvenanceAudit.md | Defines *how decisions are proven* |

---

## Phase Alignment

- Phase 2: State definitions only (this document)
- Phase 3+: Execution logic, storage, enforcement

---

## Summary

This pipeline treats **images and diagrams as legally significant evidence**, not secondary artifacts.

It ensures:
- Diagram reuse across patents
- Explicit ignore decisions
- Human oversight where required
- Strong claim defensibility

This is essential to achieving the system’s litigation and patent strategy goals.
